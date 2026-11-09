"""
Taxonomy labelling of merged-structure paths (DATA_TAX prompt, e.g. kmetty2026).

Runs as one process per vLLM server, started by launchers/parallel_worker.sh
(via `make taxonomy-<platform>`). It receives its bucket of CSV files on the
command line, classifies every `final_path` in each file against the one
server given by --agent_id, and writes one output JSON per input CSV,
named by OUTPUT_PATTERN (set by the Makefile), e.g.
{platform}_{n}_class_ids_{tax}_{countries}_{model}.json. The launcher treats "output file exists" as "done", so
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
from src.inference import prompts as p
from src.inference import utils as u
from src.inference import parallel
from src.inference.taxonomy import build_prompt, parse_prediction, valid_labels

COL_PATH = "final_path"
MAX_RETRIES = 3

# Which prompt to use; the output file name comes from OUTPUT_PATTERN (see src/inference/parallel.py)
DATA_TAX = os.environ["DATA_TAX"]


CONCURRENCY = 100

# Prompt per taxonomy name (DATA_TAX); the name goes into the output file name
PROMPTS = {"kmetty2026": p.kmetty2026}
if DATA_TAX not in PROMPTS:
    raise SystemExit(f"Unknown DATA_TAX '{DATA_TAX}', expected one of {list(PROMPTS)}")


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

    parallel.write_json_atomic(output_file, output_list)


def make_process_file(agent):
    template = PROMPTS[DATA_TAX]()

    def process_file(source_file, output_file):
        generate_predictions(source_file, output_file, agent, template, dataset_name=os.path.basename(source_file))

    return process_file


if __name__ == "__main__":
    parallel.main(make_process_file, "Labeling DDP taxonomy")
