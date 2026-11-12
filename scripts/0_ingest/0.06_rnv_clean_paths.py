"""
Clean the paths of the merged structures and of the catalogue (the largest donation).

Donations of one platform differ in wrapper folders (ig/, meta-2025-…/instagram-…/, takeout-…/) and in part
numbers of split files (posts_1.json, posts_2.json). This step removes exactly those two things (see
src/ingest/cleanPaths.py) and stores the result as a new column `clean_path` next to the original `final_path`.
Nothing is overwritten and `final_path` is never changed, so the samples drawn from the merged structures stay valid.

  <DATA_DIR>/00_ingest/005_merged_structures/<platform>/*.csv     ->  006_cleaned_structures/<platform>/*.csv
  <DATA_DIR>/00_ingest/004_largest_donation/<platform>/*.csv      ->  006_cleaned_largest_donation/<platform>/*.csv

The path standardisation (1.02) reads the cleaned files. Per platform this prints how many paths changed, how many
different paths now share one clean path, and how many paths that were not in the catalogue now are.
"""

import glob
import os

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.ingest.cleanPaths import clean_path, drop_part_number, match_key, strip_wrappers


def clean_folder(src_root, dst_root, platform):
    """Clean every csv of src_root/platform; returns the concatenated cleaned data."""
    parts = []
    for f in sorted(glob.glob(os.path.join(src_root, platform, "*.csv"))):
        df = pd.read_csv(f, dtype=str)
        df["clean_path"] = df["final_path"].map(lambda p: clean_path(p) if isinstance(p, str) else p)
        out = os.path.join(dst_root, platform, os.path.basename(f))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        df.to_csv(out, index=False)
        parts.append(df)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["final_path", "clean_path"])


def main():
    config.require("ROOT_DIR", "DATA_DIR")
    for platform in config.PLATFORMS:
        merged = clean_folder(config.MERGED_STRUCTURES_DIR, config.CLEANED_STRUCTURES_DIR, platform)
        cat = clean_folder(config.REF_DIR, config.CLEANED_CATALOGUE_DIR, platform)

        paths = merged["final_path"].dropna().drop_duplicates()
        wrapped = sum(strip_wrappers(p) != p.strip() for p in paths)
        parted = sum(drop_part_number(strip_wrappers(p)) != strip_wrappers(p) for p in paths)
        clean = paths.map(clean_path)
        shared = int(clean.duplicated(keep=False).sum())          # different paths that now share a clean path

        cat_raw = set(cat["final_path"].dropna())
        cat_keys = {match_key(x) for x in cat["clean_path"].dropna()}
        outside = [p for p in paths if p not in cat_raw]
        now_in = sum(match_key(clean_path(p)) in cat_keys for p in outside)
        cat_dupes = int(cat["clean_path"].dropna().duplicated().sum())

        print(f"{platform:10s} {len(paths):6d} paths | wrapper removed: {wrapped:5d} | part number dropped: {parted:5d} | "
              f"paths sharing a clean path: {shared:5d} | catalogue: {len(cat_raw)} paths, {cat_dupes} lost to part numbers | "
              f"not in catalogue: {len(outside)}, of which now found after cleaning: {now_in}", flush=True)
    print("written to", config.CLEANED_STRUCTURES_DIR, "and", config.CLEANED_CATALOGUE_DIR)


if __name__ == "__main__":
    main()
