"""
Re-run the paths of the annotation run (make annotation-run) that have no valid prediction, and merge the answers in.

  make annotation-retry-prepare   # 1. CPU, seconds: failed paths -> <ANNOTATION_ROOT>/sample_retry/<split>/<platform>/
  make annotation-retry           # 2. one GPU job: 2.01 on those paths (attempt 1 as before, attempts 2-3 with more tokens)
  make annotation-retry-merge     # 3. CPU, seconds: valid retry answers replace the failed records

prepare: scans <ANNOTATION_ROOT>/inference/02_path_classification_kmetty2026_simple/<split>/<platform>/*.json for records
         that fail validate_record (n=5), writes their paths to sample_retry/ and prints the count per split/platform.
merge:   for every file with a retry result, replaces a failed record by the retry record if that one is valid.
         The original file is first copied to <name>.json.before_retry (once). Records that still fail stay as they were.
Retry output goes to <...>_kmetty2026_simple_retry/, so nothing is overwritten by the GPU job.
"""

import glob
import json
import os
import shutil
import sys

import pandas as pd

os.environ["DATA_TAX"] = "kmetty2026_simple"  # before src.config is read: five predictions per record
from src import config
from src.inference import prompts as p
from src.inference.taxonomy import valid_labels, validate_record

SPLITS = ["test", "validation"]
PLATFORMS = ["facebook", "instagram", "tiktok", "x"]  # no YouTube
BASE = os.path.join(config.ANNOTATION_ROOT, "inference", "02_path_classification_kmetty2026_simple")
RETRY = BASE + "_retry"
SAMPLE_RETRY = os.path.join(config.ANNOTATION_ROOT, "sample_retry")
LABELS = valid_labels(p.kmetty2026_simple())


def failed(rec):
    return bool(validate_record(rec, LABELS, n=config.N_PREDICTIONS))


def prepare():
    shutil.rmtree(SAMPLE_RETRY, ignore_errors=True)
    shutil.rmtree(RETRY, ignore_errors=True)   # an old retry output would make the launcher skip the files
    total = 0
    for split in SPLITS:
        for platform in PLATFORMS:
            paths = []
            for f in sorted(glob.glob(os.path.join(BASE, split, platform, "*.json"))):
                paths += [r["path"] for r in json.load(open(f, encoding="utf-8")) if failed(r)]
            if not paths:
                continue
            out = os.path.join(SAMPLE_RETRY, split, platform)
            os.makedirs(out, exist_ok=True)
            pd.DataFrame({"final_path": paths}).to_csv(os.path.join(out, f"{platform}_{split}.csv"), index=False)
            print(f"{split}/{platform}: {len(paths)} paths to retry")
            total += len(paths)
    print(f"total: {total}" + ("" if total else "  (nothing to retry)"))


def merge():
    fixed = still = 0
    for f in sorted(glob.glob(os.path.join(RETRY, "*", "*", "*.json"))):
        split, platform = f.split(os.sep)[-3:-1]
        orig = os.path.join(BASE, split, platform, os.path.basename(f))
        new = {r["path"]: r for r in json.load(open(f, encoding="utf-8")) if not failed(r)}
        records = json.load(open(orig, encoding="utf-8"))
        n_fixed = 0
        for i, r in enumerate(records):
            if failed(r) and r["path"] in new:
                records[i] = new[r["path"]]
                n_fixed += 1
        if n_fixed:
            if not os.path.exists(orig + ".before_retry"):
                shutil.copy2(orig, orig + ".before_retry")
            with open(orig + ".partial", "w", encoding="utf-8") as fh:
                json.dump(records, fh, indent=2, ensure_ascii=False)
            os.replace(orig + ".partial", orig)
        fixed += n_fixed
        still += sum(failed(r) for r in records)
        print(f"{split}/{platform}: {n_fixed} fixed, {sum(failed(r) for r in records)} still without a valid prediction")
    print(f"fixed {fixed}; still invalid in the files with a retry: {still}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("prepare", "merge"):
        raise SystemExit("usage: 2.10_rnv_retry_failed_annotation.py prepare|merge")
    prepare() if mode == "prepare" else merge()
