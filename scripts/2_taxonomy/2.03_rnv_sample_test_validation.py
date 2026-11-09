"""
Draw the test and validation sets, and an annotation sheet for each.

  python scripts/2_taxonomy/2.03_rnv_sample_test_validation.py [--force]

Per platform, TEST_N + VALIDATION_N (20 + 80) unique paths are sampled at random from the merged structures
(<ROOT_DIR>/<DATA_DIR>/00_ingest/005_merged_structures, i.e. ddd_processed), after removing the smoke
sample (2.00), so test, validation and smoke never share a path. Writes, per platform and split:

  <ANNOTATION_ROOT>/sample/<split>/<platform>/<platform>_<split>.csv                        column final_path
  <ANNOTATION_ROOT>/annotation/<split>/<platform>/<platform>_<split>_to_annotate.xlsx      final_path + empty label column

The annotators fill in the label column of the sheet (in place); 2.06 reads it. Existing files are not
overwritten unless --force is given, because re-sampling would no longer match annotations already made.
"""

import argparse
import glob
import os

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config


def read_paths(pattern):
    paths = set()
    for f in sorted(glob.glob(pattern)):
        paths |= set(pd.read_csv(f, dtype=str)["final_path"].dropna())
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="Overwrite existing test/validation files")
    args = parser.parse_args()

    config.require("ROOT_DIR", "DATA_DIR")
    sizes = {"validation": config.VALIDATION_N, "test": config.TEST_N}

    for platform in config.PLATFORMS:
        merged = read_paths(os.path.join(config.MERGED_STRUCTURES_DIR, platform, "*.csv"))
        smoke = read_paths(os.path.join(config.sample_dir("smoke"), platform, "*.csv"))
        if not smoke:
            print(f"[WARNING] {platform}: no smoke sample found, run 2.00 first")
        candidates = sorted(merged - smoke)
        need = sum(sizes.values())
        if len(candidates) < need:
            raise SystemExit(f"{platform}: {len(candidates)} candidate paths, need {need}")

        targets = {s: (os.path.join(config.sample_dir(s), platform, f"{platform}_{s}.csv"),
                      os.path.join(config.annotation_dir(s), platform, f"{platform}_{s}_to_annotate.xlsx"))
                   for s in sizes}
        existing = [f for pair in targets.values() for f in pair if os.path.exists(f)]
        if existing and not args.force:
            raise SystemExit(f"{platform}: already exists ({existing[0]}, ...); use --force to re-sample")

        drawn = pd.Series(candidates).sample(n=need, random_state=config.SEED).tolist()
        start = 0
        chosen = {}
        for split, n in sizes.items():
            chosen[split] = drawn[start:start + n]
            start += n
        assert not set(chosen["validation"]) & set(chosen["test"]), f"{platform}: validation and test overlap"
        assert not smoke & (set(chosen["validation"]) | set(chosen["test"])), f"{platform}: smoke paths drawn"

        for split, paths in chosen.items():
            csv_file, sheet_file = targets[split]
            os.makedirs(os.path.dirname(csv_file), exist_ok=True)
            os.makedirs(os.path.dirname(sheet_file), exist_ok=True)
            pd.DataFrame({"final_path": paths}).to_csv(csv_file, index=False)
            pd.DataFrame({"final_path": paths, config.LABEL_COL: ""}).to_excel(sheet_file, index=False)
            print(f"{platform}: {split:10s} {len(paths)} paths -> {csv_file}")
        print(f"{platform}: {len(merged)} merged paths, {len(smoke)} smoke paths excluded")


if __name__ == "__main__":
    main()
