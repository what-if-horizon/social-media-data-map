"""
Select the smoke sample: a few paths per platform that are semantically dissimilar.

For every platform a pool of candidate paths is drawn from the merged structures
(<ROOT_DIR>/<DATA_DIR>/00_ingest/005_merged_structures, i.e. ddd_processed), minus any path already in the
test or validation set, so those sets (2.03) cannot share a path with the smoke sample. The pool is embedded with a
sentence-transformer and K mutually dissimilar paths are chosen (farthest-point selection; every pair must have cosine similarity below SMOKE_MAX_SIM).

Writes, per platform:
  <ANNOTATION_ROOT>/sample/smoke/<platform>/<platform>_smoke_<K>.csv     final_path column
  <ANNOTATION_ROOT>/sample/smoke/<platform>/smoke_similarity.json        model, threshold, similarity matrix

tests/test_smoke_sample.py checks these files (from the merged structures, dissimilar, disjoint from test and validation).

Settings (src/config.py, from .env): ROOT_DIR, DATA_DIR, EMBEDDING_MODEL (path or name of a sentence-transformers
model); optional ANNOTATION_ROOT, SMOKE_K (5), SMOKE_MAX_SIM (0.8), SMOKE_POOL (2000), SEED (42).
"""

import glob
import json
import os

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.inference.similarity import select_diverse

PLATFORMS = config.PLATFORMS
ANNOTATION_ROOT = config.ANNOTATION_ROOT
MERGED_ROOT = config.MERGED_STRUCTURES_DIR
K = config.SMOKE_K
MAX_SIM = config.SMOKE_MAX_SIM
POOL = config.SMOKE_POOL
SEED = config.SEED


def read_paths(pattern):
    paths = []
    for f in sorted(glob.glob(pattern)):
        paths += pd.read_csv(f, dtype=str)["final_path"].dropna().tolist()
    return paths


def main():
    from sentence_transformers import SentenceTransformer   # heavy, only needed here

    config.require("ROOT_DIR", "DATA_DIR")
    model_name = config.require("EMBEDDING_MODEL")
    model = SentenceTransformer(model_name)

    for platform in PLATFORMS:
        merged = read_paths(os.path.join(MERGED_ROOT, platform, "*.csv"))
        taken = set()
        for split in ("test", "validation"):
            taken |= set(read_paths(os.path.join(ANNOTATION_ROOT, "sample", split, platform, "*.csv")))
        pool = sorted(set(merged) - taken)
        print(f"{platform}: {len(merged)} merged paths, {len(taken)} already in test/validation, "
              f"{len(pool)} candidates", flush=True)
        if len(pool) < K:
            raise SystemExit(f"{platform}: only {len(pool)} candidates")

        pool = pd.Series(pool).sample(n=min(POOL, len(pool)), random_state=SEED).tolist()
        emb = model.encode(pool, batch_size=128, show_progress_bar=False)
        idx, sim = select_diverse(emb, K, MAX_SIM, seed=SEED)
        chosen = [pool[i] for i in idx]

        out_dir = os.path.join(ANNOTATION_ROOT, "sample", "smoke", platform)
        os.makedirs(out_dir, exist_ok=True)
        pd.DataFrame({"final_path": chosen}).to_csv(os.path.join(out_dir, f"{platform}_smoke_{K}.csv"), index=False)
        with open(os.path.join(out_dir, "smoke_similarity.json"), "w", encoding="utf-8") as f:
            json.dump({"embedding_model": model_name, "max_allowed": MAX_SIM, "paths": chosen,
                       "similarity": sim.round(4).tolist()}, f, indent=2)
        print(f"{platform}: chose {K} paths -> {out_dir}", flush=True)
        for pth in chosen:
            print("   ", pth, flush=True)


if __name__ == "__main__":
    main()
