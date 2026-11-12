"""Does the path standardisation output look right? Run on the output of 1.02:

    pytest tests/test_path_std_output.py --inference-dir <dir> --ref-dir <catalogue dir> [--input-dir <dir>]

Every record needs a "match" that is "NA" or a path from the catalogue of the platform, and a rationale, and every
input path needs exactly one record.
"""
import glob
import json
import os

import pandas as pd
import pytest

from src.inference.pathmatch import validate_match_record


def catalogue(ref_dir, platform):
    files = sorted(glob.glob(os.path.join(ref_dir, platform, "*.csv")))
    assert files, f"no catalogue for {platform} in {ref_dir}"
    return set(pd.read_csv(files[0], dtype=str)["final_path"].dropna())


def test_there_are_outputs(inference_dir):
    files = glob.glob(os.path.join(inference_dir, "*", "*.json"))
    assert files, f"no path standardisation outputs in {inference_dir}/<platform>/"


def test_records_are_valid(inference_file, ref_dir):
    if inference_file.endswith("_failed.json"):
        pytest.skip("failed paths are checked below")
    platform = os.path.basename(os.path.dirname(inference_file))
    cat = catalogue(ref_dir, platform)
    with open(inference_file, encoding="utf-8") as f:
        records = json.load(f)
    assert isinstance(records, list) and records, "file is empty or not a list"
    bad = [(r.get("path"), validate_match_record(r, cat)) for r in records]
    bad = [(p, problems) for p, problems in bad if problems]
    assert not bad, f"{len(bad)}/{len(records)} invalid records, e.g. " + "; ".join(f"{p}: {pr}" for p, pr in bad[:3])


def test_no_failed_paths(inference_file):
    if not inference_file.endswith("_failed.json"):
        pytest.skip("not a failed-paths file")
    with open(inference_file, encoding="utf-8") as f:
        failed = json.load(f)
    assert not failed, f"{len(failed)} paths without a valid answer, e.g. {[x['path'] for x in failed[:3]]}"


def test_every_input_path_has_a_record(inference_file, input_dir):
    if not input_dir:
        pytest.skip("--input-dir not given")
    if inference_file.endswith("_failed.json"):
        pytest.skip("failed paths are checked above")
    platform = os.path.basename(os.path.dirname(inference_file))
    n = os.path.basename(inference_file).split("_")[1]
    inputs = sorted(glob.glob(os.path.join(input_dir, platform, f"*_{n}.csv")))
    assert inputs, f"no input csv for {os.path.basename(inference_file)} in {input_dir}/{platform}"
    expected = set(pd.read_csv(inputs[0], dtype=str)["final_path"].dropna())
    with open(inference_file, encoding="utf-8") as f:
        got = [r["path"] for r in json.load(f)]
    assert set(got) == expected and len(got) == len(set(got)), (
        f"missing {len(expected - set(got))}, unexpected {len(set(got) - expected)}, duplicates {len(got) - len(set(got))}")
