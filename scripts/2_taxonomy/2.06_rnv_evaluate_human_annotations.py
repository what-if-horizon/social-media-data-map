"""
Evaluate the taxonomy of the test or validation set against human annotations.

  python scripts/2_taxonomy/2.06_rnv_evaluate_human_annotations.py --split test

Reads, per platform:
  inference:   <ANNOTATION_ROOT>/inference/<INFERENCE_SUBDIR>/<split>/<platform>/*.json   (2.01 output)
  annotations: <ANNOTATION_ROOT>/annotation/<split>/<platform>/*.xlsx   with columns `final_path` and the label column
and writes results/02_taxonomy/reports/<split>_human_eval.json (used by 2.07). Platforms
without annotations are skipped with a message, so this can run before all annotations are in.
"""

import argparse
import glob
import json
import os

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.inference import prompts as p
from src.inference.evaluation import evaluate
from src.inference.taxonomy import valid_labels

PLATFORMS = config.PLATFORMS


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--split", required=True, choices=["test", "validation"])
    parser.add_argument("--label-col", default=config.LABEL_COL,
                        help="Column with the human label in the annotation files (env LABEL_COL, default 'label')")
    parser.add_argument("--annotation-pattern", default="*.xlsx", help="Annotation files per platform folder")
    parser.add_argument("--report-dir", default=config.REPORT_DIR)
    args = parser.parse_args()

    config.require("ANNOTATION_ROOT")
    labels = valid_labels(p.kmetty2026())

    result = {"split": args.split, "label_col": args.label_col, "platforms": {}}
    all_records, all_gold = [], {}
    for platform in PLATFORMS:
        inf_files = sorted(glob.glob(os.path.join(config.inference_dir(args.split), platform, "*.json")))
        ann_files = sorted(glob.glob(os.path.join(config.annotation_dir(args.split), platform, args.annotation_pattern)))
        if not inf_files or not ann_files:
            print(f"{platform}: skipped (inference files: {len(inf_files)}, annotation files: {len(ann_files)})")
            continue

        records = []
        for f in inf_files:
            with open(f, encoding="utf-8") as fh:
                records += json.load(fh)
        ann = pd.concat([pd.read_excel(f) for f in ann_files])
        if args.label_col not in ann.columns:
            raise SystemExit(f"{platform}: column {args.label_col!r} not in annotation files {ann_files}")
        ann = ann.dropna(subset=[args.label_col])      # sheets that are not annotated yet
        ann = ann[ann[args.label_col].astype(str).str.strip() != ""]
        gold = dict(zip(ann["final_path"], ann[args.label_col]))

        result["platforms"][platform] = evaluate(records, gold, labels)
        # Pooled: prefix paths with the platform, as the same path can occur on several platforms
        all_records += [{**r, "path": f"{platform}:{r['path']}"} for r in records]
        all_gold.update({f"{platform}:{k}": v for k, v in gold.items()})
        s = result["platforms"][platform]
        print(f"{platform}: n={s['n']} top-1={s['top1_accuracy']} top-3={s['top3_accuracy']}")

    result["pooled"] = evaluate(all_records, all_gold, labels) if all_records else None
    os.makedirs(args.report_dir, exist_ok=True)
    out = os.path.join(args.report_dir, f"{args.split}_human_eval.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
