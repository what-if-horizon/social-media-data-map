"""The smoke sample (2.00) is small, diverse and kept out of test and validation.

    pytest tests/test_smoke_sample.py --sample-root <ANNOTATION_ROOT>/sample
"""
import glob
import json
import os

import pandas as pd
import pytest

from src.inference.similarity import max_pairwise

K = int(os.environ.get("SMOKE_K", 5))


def paths_in(root, split, platform):
    paths = set()
    for f in glob.glob(os.path.join(root, split, platform, "*.csv")):
        paths |= set(pd.read_csv(f, dtype=str)["final_path"].dropna())
    return paths


@pytest.fixture
def smoke(sample_root, platform):
    paths = paths_in(sample_root, "smoke", platform)
    if not paths:
        pytest.fail(f"no smoke sample for {platform} in {sample_root}/smoke (run 2.00)")
    return paths


def test_has_k_unique_paths(smoke, sample_root, platform):
    rows = sum(len(pd.read_csv(f)) for f in glob.glob(os.path.join(sample_root, "smoke", platform, "*.csv")))
    assert len(smoke) == rows == K


def test_paths_are_dissimilar(sample_root, platform, smoke):
    with open(os.path.join(sample_root, "smoke", platform, "smoke_similarity.json"), encoding="utf-8") as f:
        info = json.load(f)
    assert set(info["paths"]) == smoke, "similarity file does not match the smoke csv"
    worst = max_pairwise(info["similarity"])
    assert worst < info["max_allowed"], f"max pairwise cosine {worst:.3f} >= {info['max_allowed']}"


@pytest.mark.parametrize("other", ["full", "test", "validation"])
def test_disjoint_from(sample_root, platform, smoke, other):
    other_paths = paths_in(sample_root, other, platform)
    if not other_paths:
        pytest.skip(f"no {other} sample yet")
    assert not smoke & other_paths, f"smoke paths also in {other}: {sorted(smoke & other_paths)}"
