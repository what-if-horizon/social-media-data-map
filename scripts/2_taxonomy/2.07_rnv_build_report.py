"""
Build the HTML report for one phase.

  python scripts/2_taxonomy/2.07_rnv_build_report.py --split smoke

Collects, for the split (smoke, test or validation):
  pytest result    results/02_taxonomy/reports/<split>_pytest.json      (make inference-check)
  taxonomy outputs  <ANNOTATION_ROOT>/inference/<INFERENCE_SUBDIR>/<split>/<platform>/*.json
  judge            <ANNOTATION_ROOT>/inference/03_judge/<split>/<platform>/*.json  (make judge)
  human evaluation results/02_taxonomy/reports/<split>_human_eval.json  (make eval-human)
Missing parts are reported as such in the HTML, so the report can be built at any stage.
Writes results/02_taxonomy/reports/<split>_report.html.
"""

import argparse
import glob
import json
import os

# PYTHONPATH is the repo root (set by the launcher)
from src.inference.report import build_report

PLATFORMS = ["facebook", "instagram", "tiktok", "youtube", "x"]
INFERENCE_SUBDIR = os.environ.get("INFERENCE_SUBDIR", "02_path_classification")


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def load_per_platform(root):
    out = {}
    for platform in PLATFORMS:
        records = []
        for f in sorted(glob.glob(os.path.join(root, platform, "*.json"))):
            if f.endswith("_failed.json"):
                continue
            with open(f, encoding="utf-8") as fh:
                records += json.load(fh)
        if records:
            out[platform] = records
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--split", required=True, choices=["smoke", "test", "validation"])
    parser.add_argument("--report-dir", default="results/02_taxonomy/reports")
    args = parser.parse_args()

    annotation_root = os.environ.get("ANNOTATION_ROOT", os.path.join(os.environ["ROOT_DIR"], "ddd_annotation"))
    inference = load_per_platform(os.path.join(annotation_root, "inference", INFERENCE_SUBDIR, args.split))
    judge = load_per_platform(os.path.join(annotation_root, "inference", "03_judge", args.split))
    pytest_result = load_json(os.path.join(args.report_dir, f"{args.split}_pytest.json"))
    human = load_json(os.path.join(args.report_dir, f"{args.split}_human_eval.json"))

    models = {"taxonomy model": os.environ.get("MODEL_CONFIG", "").replace(".yaml", ""),
              "judge": os.environ.get("MODEL_CONFIG_JUDGE", "").replace(".yaml", "")}
    html = build_report(args.split, pytest_result, inference, judge, human,
                        {k: v for k, v in models.items() if v})

    os.makedirs(args.report_dir, exist_ok=True)
    out = os.path.join(args.report_dir, f"{args.split}_report.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out)


if __name__ == "__main__":
    main()
