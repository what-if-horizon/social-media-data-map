"""
Taxonomy classification of merged-structure paths (DATA_TAX prompt, e.g. kmetty2026).

Runs as one process per vLLM server, started by launchers/parallel_worker.sh
(via `make taxonomy-<platform>`). It receives its bucket of CSV files on the
command line, classifies every `final_path` in each file against the one
server given by --agent_id, and writes one output JSON per input CSV,
named {platform}_{n}_class_ids_{tax}_{countries}_{model}.json. The launcher treats "output file exists" as "done", so
outputs are written to a .partial file first and renamed when complete.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src.agents.initAgents import AgentManager
from src.inference import prompts as p
from src.inference import utils as u
from src.inference.taxonomy import build_prompt, output_name, parse_prediction, valid_labels

COL_PATH = "final_path"
MAX_RETRIES = 3

# Output name parts; see output_name() in src/inference/taxonomy.py
DATA_TAX = os.environ["DATA_TAX"]
COUNTRIES = os.environ["COUNTRIES"]


CONCURRENCY = 100

# Prompt per taxonomy name (DATA_TAX); the name goes into the output file name
PROMPTS = {"kmetty2026": p.kmetty2026}
if DATA_TAX not in PROMPTS:
    raise SystemExit(f"Unknown DATA_TAX '{DATA_TAX}', expected one of {list(PROMPTS)}")

MODEL_CONFIG = os.environ["MODEL_CONFIG"]


def run_llm_validated(prompt, agent, labels, max_retries=MAX_RETRIES):
    last_raw = None
    for attempt in range(1, max_retries + 1):
        last_raw = u.run_llm(prompt, agent)
        parsed = parse_prediction(last_raw, labels)
        if parsed is not None:
            return {"raw": last_raw, "parsed": parsed, "ok": True, "attempts": attempt}
        print(f"  Invalid output (attempt {attempt}/{max_retries}), retrying...", flush=True)
        time.sleep(1)
    return {"raw": last_raw, "parsed": None, "ok": False, "attempts": max_retries}


def generate_predictions(source_file, output_file, agent, template, dataset_name="Dataset"):
    labels = valid_labels(template)
    print(f"\n{'=' * 50}\n STARTING PREDICTIONS: {dataset_name}\n{'=' * 50}", flush=True)

    try:
        df = pd.read_csv(source_file, sep=",", dtype=str, engine="c", on_bad_lines="skip")
    except Exception:
        df = pd.read_csv(source_file, sep=",", dtype=str, engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])

    paths = df[COL_PATH].fillna("").astype(str).tolist()
    prompts = [build_prompt(template, path) for path in paths]
    print(f" {len(prompts)} prompts prepared, running LLM...", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        results = list(pool.map(lambda pr: run_llm_validated(pr, agent, labels), prompts))  # order preserved
    n_failed = sum(not r["ok"] for r in results)
    print(f" LLM done in {time.time() - t0:.0f}s | {n_failed} failed after {MAX_RETRIES} attempts", flush=True)

    # One record per path: {"path": ..., <fields returned by the model>}
    output_list = []
    for path, r in zip(paths, results):
        node = {"path": path}
        if r["ok"]:
            node.update({k: v for k, v in r["parsed"].items() if k != "path"})
        else:
            node.update({"predictions": None, "error": "invalid output", "raw_output": r["raw"]})
        output_list.append(node)

    # Write to .partial, then rename: the launcher only treats complete files as done
    partial = f"{output_file}.partial"
    with open(partial, "w") as f:
        json.dump(output_list, f, indent=2)
    os.replace(partial, output_file)


def process_files(files: List[str], source_folder: str, output_folder: str, agent, agent_id: str) -> None:
    """Process this server's bucket of CSVs one after another. A failing file is reported and skipped."""
    os.makedirs(output_folder, exist_ok=True)
    template = PROMPTS[DATA_TAX]()
    platform = os.path.basename(os.path.normpath(source_folder))

    failed = []
    for idx, filename in enumerate(files):
        source_file = os.path.join(source_folder, filename)
        output_file = os.path.join(output_folder, output_name(platform, filename, DATA_TAX, COUNTRIES, MODEL_CONFIG))
        try:
            generate_predictions(source_file, output_file, agent, template, dataset_name=filename)
            print(f"[{agent_id}] {idx + 1}/{len(files)}: wrote {output_file}", flush=True)
        except Exception as e:
            failed.append(filename)
            print(f"[{agent_id}] FAILED {filename}: {e!r}", file=sys.stderr, flush=True)

    print(f"[{agent_id}] finished: {len(files) - len(failed)} ok, {len(failed)} failed", flush=True)
    if failed:
        print(f"[{agent_id}] failed files: {' '.join(failed)}", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    print("START ", datetime.now(), flush=True)

    parser = argparse.ArgumentParser(description="Labeling DDP taxonomy")
    parser.add_argument("--files", type=str, nargs="+", required=True, help="File names to process in source_folder.")
    parser.add_argument("--source_folder", type=str, required=True, help="Source folder.")
    parser.add_argument("--output_folder", type=str, required=True, help="Output folder.")
    parser.add_argument("--agent_id", type=str, required=True, help="Model 'id' from the YAML to send requests to.")
    args = parser.parse_args()

    manager = AgentManager()  # reads MODEL_YAML and MODEL_DIR from the environment
    if args.agent_id not in manager.agents:
        raise RuntimeError(f"No model with id '{args.agent_id}' in MODEL_YAML ({list(manager.agents)}).")
    agent = manager.get(args.agent_id)

    print(f"[{args.agent_id}] processing {len(args.files)} file(s).", flush=True)
    process_files(args.files, args.source_folder, args.output_folder, agent, args.agent_id)

    print("FINISH ", datetime.now(), flush=True)
