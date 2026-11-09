"""Does the classification output look right? Run on the output of 2.01:

    pytest tests/test_inference_output.py --inference-dir <dir> [--input-dir <dir>] [--results-json out.json]

If this fails, the LLM judge (2.02) is run on the output (make inference-check).
"""
import glob
import json
import os

import pandas as pd
import pytest

from src.inference import prompts
from src.inference.taxonomy import valid_labels, validate_record

LABELS = valid_labels(prompts.kmetty2026())


def test_there_are_outputs(inference_dir):
    files = glob.glob(os.path.join(inference_dir, "*", "*.json"))
    assert files, f"no classification outputs in {inference_dir}/<platform>/"


def test_every_input_platform_has_output(inference_dir, input_dir):
    if not input_dir:
        pytest.skip("--input-dir not given")
    expected = {p for p in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, p))}
    got = {p for p in os.listdir(inference_dir) if glob.glob(os.path.join(inference_dir, p, "*.json"))}
    assert expected <= got, f"no output for platforms: {sorted(expected - got)}"


def test_records_are_valid(inference_file):
    with open(inference_file, encoding="utf-8") as f:
        records = json.load(f)
    assert isinstance(records, list) and records, "file is empty or not a list"
    bad = [(r.get("path") if isinstance(r, dict) else r, validate_record(r, LABELS)) for r in records]
    bad = [(p, problems) for p, problems in bad if problems]
    assert not bad, f"{len(bad)}/{len(records)} invalid records, e.g. " + "; ".join(f"{p}: {pr}" for p, pr in bad[:3])


def test_every_input_path_has_a_record(inference_file, input_dir):
    if not input_dir:
        pytest.skip("--input-dir not given")
    platform = os.path.basename(os.path.dirname(inference_file))
    stem_n = os.path.basename(inference_file).split("_")[1]
    inputs = sorted(glob.glob(os.path.join(input_dir, platform, f"*_{stem_n}.csv")))
    assert inputs, f"no input csv for {os.path.basename(inference_file)} in {input_dir}/{platform}"
    expected = set(pd.read_csv(inputs[0], dtype=str)["final_path"].dropna())
    with open(inference_file, encoding="utf-8") as f:
        got = [r["path"] for r in json.load(f)]
    assert set(got) == expected and len(got) == len(set(got)), (
        f"missing {len(expected - set(got))}, unexpected {len(set(got) - expected)}, "
        f"duplicates {len(got) - len(set(got))}")
