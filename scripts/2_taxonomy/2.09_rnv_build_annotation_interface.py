"""
Build the annotation interface (annotation/annotation_interface.html) from the test and validation samples
and the taxonomy output for them. YouTube is excluded.

What the participant sees: two parts, each ordered by platform. Part 1 (first half of the paths) shows the model's
five labels plus "None of the above"; part 2 (second half) shows the full list of labels only. Which paths go to which
part is random per platform and split. The split (test or validation) is not in the page.

  make taxonomy-sample                       # 2.03: test + validation samples
  make annotation-run                        # 2.01 with kmetty2026_simple on test + validation, no YouTube (GPU jobs)
  make annotation-interface                  # 2.09: this script
  make annotation-interface-smoke            # same page from the smoke sample, to try the interface (20 paths)

Paths:       <ANNOTATION_ROOT>/sample/<split>/<platform>/<platform>_<split>.csv   (column final_path)
Predictions: <ANNOTATION_ROOT>/inference/02_path_classification_kmetty2026_simple/<split>/<platform>/*.json
             (prompt kmetty2026_simple: five ranked labels; make annotation-run). They are shown to the
             annotator in shuffled order. A path without valid predictions (not run, or "predictions": null) is shown
             with the full category table only.
The script stops if predictions are missing, so a half-finished run does not reach the participants; pass
--allow-missing to build anyway. The order is shuffled with SEED.
"""

import argparse
import csv
import glob
import json
import os
import random
import re
from pathlib import Path

from src import config

REPO = Path(__file__).resolve().parents[2]
HTML = REPO / "annotation" / "annotation_interface.html"
INSTRUCTIONS = REPO / "annotation" / "12112026_annotation_instructions_DDP_topology.md"
NAMES = {"facebook": "Facebook", "instagram": "Instagram", "tiktok": "TikTok", "x": "X"}  # no YouTube
SPLITS = ["test", "validation"]
TOP_N = 5

parser = argparse.ArgumentParser()
parser.add_argument("--allow-missing", action="store_true", help="build even if some paths have no predictions")
parser.add_argument("--smoke", action="store_true",
                    help="test build from the smoke sample (5 paths per platform, no YouTube) -> annotation_interface_smoke.html")
args = parser.parse_args()
if args.smoke:
    SPLITS = ["smoke"]
    args.allow_missing = True

label_to_id = {m.group(2).strip(): int(m.group(1))
               for m in re.finditer(r"^### (\d+)\. (.+)$", INSTRUCTIONS.read_text(), re.M)}
assert len(label_to_id) == 15, f"expected 15 labels in {INSTRUCTIONS}, found {len(label_to_id)}"


INFERENCE = os.path.join(config.ANNOTATION_ROOT, "inference")
# The smoke sample may only have been run with the older kmetty2026 prompt (three labels): use it as a fallback.
PREDICTIONS_DIRS = [os.path.join(INFERENCE, "02_path_classification_kmetty2026_simple")]
if args.smoke:
    PREDICTIONS_DIRS.append(os.path.join(INFERENCE, "02_path_classification"))


def load_predictions(split, platform):
    """path -> list of label ids, best first."""
    preds = {}
    files = [f for d in PREDICTIONS_DIRS for f in sorted(glob.glob(os.path.join(d, split, platform, "*.json")))]
    for f in files:
        for r in json.load(open(f)):
            if not r.get("predictions") or r["path"] in preds:   # the first folder with a valid answer wins
                continue
            ranked = sorted(r["predictions"], key=lambda p: -p["confidence"])
            ids = [label_to_id[p["label"]] for p in ranked if p["label"] in label_to_id]
            if ids:
                preds[r["path"]] = list(dict.fromkeys(ids))[:TOP_N]
    return preds


# One entry per path. The split is used for the balancing below but never goes into the page: participants must not
# know whether a path comes from test or validation (join on platform + path afterwards).
by_platform = {platform: {split: [] for split in SPLITS} for platform in NAMES}
missing = []
for split in SPLITS:
    for platform, name in NAMES.items():
        preds = load_predictions(split, platform)
        csv_file = sorted(glob.glob(os.path.join(config.sample_dir(split), platform, f"{platform}_{split}*.csv")))[0]  # smoke: x_smoke_5.csv
        with open(csv_file) as fh:
            for row in csv.DictReader(fh):
                path = row["final_path"]
                if path not in preds:
                    missing.append((split, platform, path))
                by_platform[platform][split].append({"platform": name, "path": path, "top5": preds.get(path, [])})

if missing:
    by = {}
    for s_, p_, _ in missing:
        by[(s_, p_)] = by.get((s_, p_), 0) + 1
    print("No predictions for:", ", ".join(f"{s_}/{p_}: {n}" for (s_, p_), n in sorted(by.items())))
    print("Run `make annotation-run` for these first.")
    if not args.allow_missing:
        raise SystemExit("Stopping; use --allow-missing to build without them.")

# Two parts. Part 1 = the first half of the paths, with the model's suggestions; part 2 = the other half, full list only.
# Within every platform and split, half of the paths (rounded up) go to part 1, chosen at random, so the part is not
# confounded with platform or split. Each part is ordered by platform (NAMES order), shuffled within the platform.
rng = random.Random(config.SEED)
parts = {1: {pl: [] for pl in NAMES}, 2: {pl: [] for pl in NAMES}}
for platform in NAMES:
    for split in SPLITS:
        group = by_platform[platform][split][:]
        rng.shuffle(group)
        half = (len(group) + 1) // 2
        parts[1][platform] += group[:half]
        parts[2][platform] += group[half:]

items = []
for part in (1, 2):
    for platform in NAMES:
        group = parts[part][platform]
        rng.shuffle(group)
        for it in group:
            items.append({"id": f"{platform}_{len(items)}", "part": part, **it})
print({f"part{pt}": sum(len(v) for v in parts[pt].values()) for pt in parts})

out_file = HTML.with_name("annotation_interface_smoke.html") if args.smoke else HTML
html = HTML.read_text()   # the main page is the template, also for --smoke
block = "// BEGIN ITEMS\nconst ITEMS = " + json.dumps(items, indent=1, ensure_ascii=False) + ";\n// END ITEMS"
html = re.sub(r"// BEGIN ITEMS.*?// END ITEMS", lambda m: block, html, flags=re.S)
if args.smoke:   # its own saved progress, and a visible title, so it is not mistaken for the real thing
    html = html.replace('"ddp_annotation_v1"', '"ddp_annotation_smoke"').replace("<title>DDP path annotation</title>", "<title>DDP path annotation (SMOKE TEST)</title>")
    html = html.replace("<h1>Annotating paths in Digital Data Packages</h1>", "<h1>SMOKE TEST: Annotating paths in Digital Data Packages</h1>")
out_file.write_text(html)
print(f"{len(items)} paths ({len(items) - len(missing)} with predictions) -> {out_file}")
