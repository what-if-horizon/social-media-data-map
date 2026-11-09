"""The smoke, test and validation samples (2.00, 2.03): drawn from the merged structures, disjoint, and the
smoke sample is small and diverse.

    pytest tests/test_samples.py --sample-root <ANNOTATION_ROOT>/sample --merged-dir <...>/00_ingest/005_merged_structures
"""
import glob
import json
import os

import pandas as pd
import pytest

from src.inference.similarity import max_pairwise

K = int(os.environ.get("SMOKE_K", 5))
SPLITS = ["smoke", "test", "validation"]


def paths_in(root, split, platform):
    paths = set()
    for f in glob.glob(os.path.join(root, split, platform, "*.csv")):
        paths |= set(pd.read_csv(f, dtype=str)["final_path"].dropna())
    return paths


def n_rows(root, split, platform):
    return sum(len(pd.read_csv(f)) for f in glob.glob(os.path.join(root, split, platform, "*.csv")))


@pytest.fixture
def smoke(sample_root, platform):
    paths = paths_in(sample_root, "smoke", platform)
    if not paths:
        pytest.fail(f"no smoke sample for {platform} in {sample_root}/smoke (run 2.00)")
    return paths


def test_smoke_has_k_unique_paths(smoke, sample_root, platform):
    assert len(smoke) == n_rows(sample_root, "smoke", platform) == K


def test_smoke_paths_are_dissimilar(sample_root, platform, smoke):
    with open(os.path.join(sample_root, "smoke", platform, "smoke_similarity.json"), encoding="utf-8") as f:
        info = json.load(f)
    assert set(info["paths"]) == smoke, "similarity file does not match the smoke csv"
    worst = max_pairwise(info["similarity"])
    assert worst < info["max_allowed"], f"max pairwise cosine {worst:.3f} >= {info['max_allowed']}"


@pytest.mark.parametrize("split", SPLITS)
def test_paths_come_from_merged_structures(request, sample_root, platform, split):
    merged_dir = request.config.getoption("--merged-dir")
    if not merged_dir:
        pytest.skip("--merged-dir not given")
    paths = paths_in(sample_root, split, platform)
    if not paths:
        pytest.skip(f"no {split} sample yet")
    merged = set()
    for f in glob.glob(os.path.join(merged_dir, platform, "*.csv")):
        merged |= set(pd.read_csv(f, dtype=str, usecols=["final_path"])["final_path"].dropna())
    assert merged, f"no merged structures for {platform} in {merged_dir}"
    assert paths <= merged, f"{len(paths - merged)} {split} paths are not in {merged_dir}: {sorted(paths - merged)[:3]}"


@pytest.mark.parametrize("split", ["test", "validation"])
def test_split_has_unique_paths(sample_root, platform, split):
    paths = paths_in(sample_root, split, platform)
    if not paths:
        pytest.skip(f"no {split} sample yet")
    assert len(paths) == n_rows(sample_root, split, platform)


@pytest.mark.parametrize("a,b", [("smoke", "test"), ("smoke", "validation"), ("test", "validation")])
def test_samples_are_disjoint(sample_root, platform, a, b):
    pa, pb = paths_in(sample_root, a, platform), paths_in(sample_root, b, platform)
    if not pa or not pb:
        pytest.skip(f"{a} or {b} sample not made yet")
    assert not pa & pb, f"{a} and {b} share paths: {sorted(pa & pb)[:3]}"
