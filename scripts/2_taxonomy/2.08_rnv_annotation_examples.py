"""
Example paths per platform and category, for the annotation instructions.

  python scripts/2_taxonomy/2.08_rnv_annotation_examples.py pool        # 1. draw the paths the model will label
  make taxonomy-run SPLIT=pool                                          # 2. the model labels them (GPU, one job)
  python scripts/2_taxonomy/2.08_rnv_annotation_examples.py examples    # 3. pick EXAMPLES_K random paths per label

pool:     EXAMPLES_POOL_N (500) random paths per platform from the merged structures
          (<ROOT_DIR>/<DATA_DIR>/00_ingest/005_merged_structures), without any path in the smoke, test or validation
          sample. Writes <ANNOTATION_ROOT>/sample/pool/<platform>/<platform>_pool.csv.
examples: for every platform and every taxonomy label, EXAMPLES_K (3) random paths among those the model gave that
          label as its top-1 prediction (any confidence). Writes
            <ANNOTATION_ROOT>/sample/examples/<platform>/<platform>_examples.csv   final_path (2.03 keeps these out of test/validation)
            <ANNOTATION_ROOT>/annotation/examples/annotation_examples.xlsx           examples + coverage sheets
            <ANNOTATION_ROOT>/annotation/examples/annotation_examples.md             to paste into the instructions
          Labels come from the model, not from people: check them before they go into the instructions.
          Where the pool has fewer than K paths for a label on a platform, all of them are listed and the
          coverage sheet shows the gap.
"""

import argparse
import glob
import json
import os
import random

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.inference import prompts as p
from src.inference.taxonomy import label_list


def read_paths(pattern):
    paths = set()
    for f in sorted(glob.glob(pattern)):
        paths |= set(pd.read_csv(f, dtype=str)["final_path"].dropna())
    return paths


def taken_paths(platform):
    """Paths that must not be used as examples: smoke, test and validation sample."""
    taken = set()
    for split in ("smoke", "test", "validation"):
        taken |= read_paths(os.path.join(config.sample_dir(split), platform, "*.csv"))
    return taken


def make_pool():
    config.require("ROOT_DIR", "DATA_DIR")
    for platform in config.PLATFORMS:
        merged = read_paths(os.path.join(config.MERGED_STRUCTURES_DIR, platform, "*.csv"))
        candidates = sorted(merged - taken_paths(platform))
        n = min(config.EXAMPLES_POOL_N, len(candidates))
        pool = pd.Series(candidates).sample(n=n, random_state=config.SEED).tolist()
        out = os.path.join(config.sample_dir("pool"), platform, f"{platform}_pool.csv")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pd.DataFrame({"final_path": pool}).to_csv(out, index=False)
        print(f"{platform}: {n} of {len(candidates)} candidate paths -> {out}")


def make_examples():
    config.require("ANNOTATION_ROOT")
    labels = label_list(p.kmetty2026())
    rng = random.Random(config.SEED)
    rows, coverage = [], []

    for platform in config.PLATFORMS:
        files = sorted(glob.glob(os.path.join(config.inference_dir("pool"), platform, "*.json")))
        if not files:
            raise SystemExit(f"{platform}: no model output for the pool in {config.inference_dir('pool')}/{platform}; "
                             "run `make taxonomy-run SPLIT=pool` first")
        records = []
        for f in files:
            with open(f, encoding="utf-8") as fh:
                records += json.load(fh)
        taken = taken_paths(platform)
        records = [r for r in records if r["path"] not in taken]
        no_output = sum(1 for r in records if not r.get("predictions"))
        by_label = {lab: [] for lab in labels}
        for r in records:
            if r.get("predictions"):
                by_label.setdefault(r["predictions"][0]["label"], []).append(r)

        for lab in labels:
            candidates = sorted(by_label.get(lab, []), key=lambda r: r["path"])   # sorted, then seeded: reproducible
            chosen = rng.sample(candidates, min(config.EXAMPLES_K, len(candidates)))
            coverage.append({"platform": platform, "category": lab, "in_pool": len(candidates),
                             "examples": len(chosen), "complete": len(chosen) == config.EXAMPLES_K})
            for r in chosen:
                top = r["predictions"][0]
                rows.append({"category": lab, "platform": platform, "path": r["path"],
                             "model_confidence": top["confidence"],
                             "second_label": r["predictions"][1]["label"],
                             "model_rationale": r.get("rationale", "")})
        if no_output:
            print(f"{platform}: {no_output} pool paths without a valid model output were ignored")

    order = {lab: i for i, lab in enumerate(labels)}
    plat = {pl: i for i, pl in enumerate(config.PLATFORMS)}
    examples = pd.DataFrame(rows)
    examples = examples.sort_values(by=["category", "platform", "path"],
                                    key=lambda c: c.map(order) if c.name == "category" else c.map(plat) if c.name == "platform" else c)
    cov = pd.DataFrame(coverage)

    # sample/examples/<platform>/<platform>_examples.csv, so 2.03 and the sample tests can keep them separate
    for platform, group in examples.groupby("platform"):
        out = os.path.join(config.sample_dir("examples"), platform, f"{platform}_examples.csv")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        group[["path"]].rename(columns={"path": "final_path"}).to_csv(out, index=False)

    out_dir = os.path.join(config.annotation_dir("examples"))
    os.makedirs(out_dir, exist_ok=True)
    with pd.ExcelWriter(os.path.join(out_dir, "annotation_examples.xlsx")) as xl:
        examples.to_excel(xl, sheet_name="examples", index=False)
        cov.to_excel(xl, sheet_name="coverage", index=False)
    with open(os.path.join(out_dir, "annotation_examples.md"), "w", encoding="utf-8") as f:
        f.write(to_markdown(examples, cov, labels))

    print(f"{len(examples)} example paths -> {out_dir}")
    gaps = cov[~cov["complete"]]
    print(f"{len(gaps)} of {len(cov)} platform/category cells have fewer than {config.EXAMPLES_K} paths in the pool:")
    for _, g in gaps.iterrows():
        print(f"   {g['platform']:10s} {g['category']}: {g['examples']}")


def to_markdown(examples, cov, labels):
    out = ["# Example paths per category", "",
           "Labels were suggested by the model and have not been checked by a person.", ""]
    for i, lab in enumerate(labels, 1):
        out.append(f"## {i}. {lab}")
        out.append("")
        for platform in config.PLATFORMS:
            sub = examples[(examples["category"] == lab) & (examples["platform"] == platform)]
            out.append(f"**{platform}**")
            if sub.empty:
                out.append("- (no example found)")
            for _, r in sub.iterrows():
                out.append(f"- `{r['path']}`")
            out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["pool", "examples"])
    args = parser.parse_args()
    make_pool() if args.step == "pool" else make_examples()
