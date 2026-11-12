"""
LLM judge for the taxonomy output.

Runs as one process per vLLM server, started by launchers/parallel_worker.sh
(via `make judge SPLIT=...`) with a different model than the taxonomy model. Each input is a
taxonomy output JSON from 2.01; for every record the judge says whether the top label
is correct, plausible or incorrect, and which label it would choose. Output is one JSON per
input file, named by OUTPUT_PATTERN. Run it when the pytest on the inference outputs fails
(`make inference-check`), or on its own for a second opinion.
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.inference import parallel
from src.inference import prompts as p
from src.inference import utils as u
from src.inference.judge import build_judge_prompt, parse_verdict
from src.inference.taxonomy import valid_labels

MAX_RETRIES = 3
CONCURRENCY = 100

# The taxonomy prompt the outputs were produced with (its topology is what the judge applies)
DATA_TAX = config.DATA_TAX
PROMPTS = {"kmetty2026": p.kmetty2026, "kmetty2026_simple": p.kmetty2026_simple}
if DATA_TAX not in PROMPTS:
    raise SystemExit(f"Unknown DATA_TAX '{DATA_TAX}', expected one of {list(PROMPTS)}")


def judge_one(record, taxonomy_prompt, labels, agent):
    prompt = build_judge_prompt(taxonomy_prompt, record)
    top1 = record["predictions"][0]["label"] if record.get("predictions") else None
    last_raw = None
    for attempt in range(1, MAX_RETRIES + 1):
        last_raw = u.run_llm(prompt, agent)
        verdict = parse_verdict(last_raw, labels)
        if verdict is not None:
            return {"path": record["path"], "model_top1": top1, "attempts": attempt, **verdict}
        print(f"  Invalid judge output (attempt {attempt}/{MAX_RETRIES}) for {record['path']}", flush=True)
        time.sleep(1)
    return {"path": record["path"], "model_top1": top1, "attempts": MAX_RETRIES,
            "verdict": None, "judge_label": None, "error": "invalid output", "raw_output": last_raw}


def make_process_file(agent):
    taxonomy_prompt = PROMPTS[DATA_TAX]()
    labels = valid_labels(taxonomy_prompt)

    def process_file(source_file, output_file):
        with open(source_file, encoding="utf-8") as f:
            records = json.load(f)
        print(f" {os.path.basename(source_file)}: judging {len(records)} records", flush=True)

        t0 = time.time()
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            results = list(pool.map(lambda r: judge_one(r, taxonomy_prompt, labels, agent), records))  # order preserved
        n_failed = sum(r["verdict"] is None for r in results)
        print(f" judge done in {time.time() - t0:.0f}s | {n_failed} without a valid verdict", flush=True)

        parallel.write_json_atomic(output_file, results)

    return process_file


if __name__ == "__main__":
    parallel.main(make_process_file, "LLM judge for the taxonomy output")
