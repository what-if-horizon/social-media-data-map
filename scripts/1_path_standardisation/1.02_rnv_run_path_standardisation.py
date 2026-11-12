"""
Path standardisation: does a path point to the same data as a path in the catalogue?

The catalogue of a platform is its largest donation (<REF_DIR>/<platform>/*.csv, column final_path). For every
input path the model returns the catalogue path that holds the same data, or "NA" (prompt: path_std2026 in
src/inference/prompts.py). A path that is itself in the catalogue is matched to itself without asking the model
("method": "exact").

Runs as one process per vLLM server, started by launchers/parallel_worker.sh:
  make path_std-run SPLIT=smoke|test|validation    the smoke, test or validation sample
  make path_std                                    all merged structures
Each input CSV (`final_path` column) is processed against the one server given by --agent_id; output is one JSON
per input CSV, named by OUTPUT_PATTERN (set by the Makefile). Output records:
  {"path": ..., "match": "<catalogue path or NA>", "rationale": ..., "method": "exact" | "llm"}
A path whose answer is still invalid after three tries (a "match" that is not in the catalogue, or no JSON) goes
to a sibling "_failed" file. tests/test_path_std_output.py checks the output.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.inference import parallel
from src.inference import prompts as p
from src.inference import utils as u
from src.inference.pathmatch import NA, build_path_prompt, catalogue_text, parse_match

COL_PATH = "final_path"
MAX_RETRIES = 3
CONCURRENCY = 100

# Prompt per name (PATH_STD); the name goes into the output file names
PROMPTS = {"path_std2026": p.path_std2026}
PATH_STD = config.PATH_STD
if PATH_STD not in PROMPTS:
    raise SystemExit(f"Unknown PATH_STD '{PATH_STD}', expected one of {list(PROMPTS)}")


def load_catalogue(platform):
    """Paths of the largest donation of the platform: the first file in REF_DIR/<platform>/."""
    config.require("REF_DIR")
    platform_dir = os.path.join(config.REF_DIR, platform)
    ref_file = os.path.join(platform_dir, sorted(os.listdir(platform_dir))[0])
    return pd.read_csv(ref_file, dtype=str)[COL_PATH].dropna().drop_duplicates().tolist()


def run_one(path, prefix_template, catalogue, catalogue_set, agent):
    if path in catalogue_set:
        return {"path": path, "match": path, "rationale": "The path is in the catalogue.", "method": "exact"}, None
    prompt = build_path_prompt(prefix_template, catalogue, path)
    last_raw = None
    for attempt in range(1, MAX_RETRIES + 1):
        last_raw = u.run_llm(prompt, agent)
        parsed = parse_match(last_raw, catalogue_set)
        if parsed is not None:
            return {"path": path, "match": parsed["match"], "rationale": parsed["rationale"], "method": "llm"}, None
        print(f"  Invalid output (attempt {attempt}/{MAX_RETRIES}) for {path}", flush=True)
        time.sleep(1)
    return None, {"path": path, "error": "invalid output", "raw": str(last_raw)}


def make_process_file(agent):
    template = PROMPTS[PATH_STD]()

    def process_file(source_file, output_file):
        platform = os.path.basename(os.path.dirname(source_file))
        catalogue_list = load_catalogue(platform)
        catalogue, catalogue_set = catalogue_text(catalogue_list), set(catalogue_list)

        df = pd.read_csv(source_file, dtype=str)
        paths = df[COL_PATH].dropna().drop_duplicates().tolist()
        n_exact = sum(x in catalogue_set for x in paths)
        print(f" {os.path.basename(source_file)}: {len(paths)} paths, {n_exact} in the catalogue, "
              f"catalogue of {len(catalogue_list)} paths", flush=True)

        t0 = time.time()
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            results = list(pool.map(lambda x: run_one(x, template, catalogue, catalogue_set, agent), paths))  # order kept
        ok = [r for r, _ in results if r is not None]
        failed = [f for _, f in results if f is not None]
        n_na = sum(r["match"] == NA for r in ok)
        print(f" done in {time.time() - t0:.0f}s | {len(ok)} ok ({n_na} NA), {len(failed)} failed", flush=True)

        parallel.write_json_atomic(output_file.replace(".json", "_failed.json"), failed)
        parallel.write_json_atomic(output_file, ok)

    return process_file


if __name__ == "__main__":
    parallel.main(make_process_file, "Path standardisation")
