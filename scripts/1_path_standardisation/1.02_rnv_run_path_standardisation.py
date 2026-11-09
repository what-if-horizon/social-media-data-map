"""
Path standardisation: map every merged-structure path to a path from the catalogue of
reference paths (largest donation) or "NA".

Runs as one process per vLLM server, started by launchers/parallel_worker.sh
(via `make path_std-<platform>`). Each input CSV (`final_path` column) is processed
against the one server given by --agent_id; output is one JSON per input CSV, named by
OUTPUT_PATTERN (set by the Makefile). The catalogue for a platform is the first file in
REF_DIR/<platform>/. Rows that fail after all retries go to a sibling "_failed" file.
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src.inference import parallel
from src.inference import utils as u
from src.inference.legacy import prompts as p
from src.inference.taxonomy import extract_json_dict

COL_PATH = "final_path"
MAX_RETRIES = 3
CONCURRENCY = 100

REF_DIR = os.environ["REF_DIR"]   # .../00_ingest/004_largest_donation


def load_refs(platform):
    platform_dir = os.path.join(REF_DIR, platform)
    ref_file = os.path.join(platform_dir, sorted(os.listdir(platform_dir))[0])
    return pd.read_csv(ref_file)[COL_PATH].tolist()


def run_one(path, template, refs_str, agent):
    last_raw = None
    for attempt in range(1, MAX_RETRIES + 1):
        last_raw = u.run_llm(u.prepare_prompt(path, template, refs_str), agent)
        parsed = extract_json_dict(last_raw)
        if parsed is not None and isinstance(parsed.get("estimated_path"), str):
            return {"path": path, **parsed}, None
        print(f"  Invalid output (attempt {attempt}/{MAX_RETRIES}) for {path}", flush=True)
        time.sleep(1)
    return None, {"path": path, "error": "invalid output", "raw": str(last_raw)}


def make_process_file(agent):
    template = p.prompt_std_ids()

    def process_file(source_file, output_file):
        platform = os.path.basename(os.path.dirname(source_file))
        refs = load_refs(platform)
        refs_str = str(refs)

        df = pd.read_csv(source_file, dtype=str)
        # Skip paths that are already reference paths, and duplicates
        paths = df[COL_PATH].dropna().drop_duplicates()
        paths = paths[~paths.isin(set(refs))].tolist()
        print(f" {os.path.basename(source_file)}: {len(paths)} paths to standardise", flush=True)

        t0 = time.time()
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            results = list(pool.map(lambda x: run_one(x, template, refs_str, agent), paths))  # order preserved
        ok = [r for r, _ in results if r is not None]
        failed = [f for _, f in results if f is not None]
        print(f" LLM done in {time.time() - t0:.0f}s | {len(ok)} ok, {len(failed)} failed", flush=True)

        parallel.write_json_atomic(output_file.replace(".json", "_failed.json"), failed)
        parallel.write_json_atomic(output_file, ok)

    return process_file


if __name__ == "__main__":
    parallel.main(make_process_file, "Path standardisation")
