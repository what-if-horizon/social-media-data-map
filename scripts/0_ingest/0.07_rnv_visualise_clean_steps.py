"""
How many paths does each cleaning step explain, and how many are left unexplained?

  make clean_steps

A path is explained when the catalogue (the largest donation of the platform) has the same path. The steps are applied
one after the other to the paths of the merged structures and to the catalogue: exact, wrapper folders removed, part
numbers dropped, case and separators ignored (src/ingest/cleanSteps.py, rules in src/ingest/cleanPaths.py). Writes
results/00_ingest/clean_steps.html, with per platform the paths explained by each step, the paths left for the model
(1.02) and example paths for every step.
"""

import glob
import os

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.ingest.cleanSteps import build_page, explain

COL_PATH = "final_path"


def read_paths(folder):
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    if not files:
        raise SystemExit(f"No csv in {folder}")
    return pd.concat([pd.read_csv(f, dtype=str, usecols=[COL_PATH]) for f in files])[COL_PATH].dropna().drop_duplicates().tolist()


def main():
    config.require("ROOT_DIR", "DATA_DIR")
    per_platform = {}
    for platform in config.PLATFORMS:
        paths = read_paths(os.path.join(config.MERGED_STRUCTURES_DIR, platform))
        catalogue = read_paths(os.path.join(config.REF_DIR, platform))
        per_platform[platform] = explain(paths, catalogue)
        r = per_platform[platform]
        print(f"{platform:10s} {r['total']:6d} paths | " +
              " | ".join(f"{s['name']}: +{s['explained']} (left {s['left']})" for s in r["steps"]), flush=True)

    out_dir = os.path.join(str(config.PROJ_ROOT), "results", "00_ingest")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "clean_steps.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_page(per_platform))
    print("written to", out)


if __name__ == "__main__":
    main()
