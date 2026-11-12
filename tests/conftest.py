"""pytest options and a JSON result file for the report (scripts/2_taxonomy/2.07)."""
import glob
import json
import os
from datetime import datetime

import pytest

PLATFORMS = ["facebook", "instagram", "tiktok", "youtube", "x"]
_results = []


def pytest_addoption(parser):
    parser.addoption("--inference-dir", default=os.environ.get("INFERENCE_DIR"),
                     help="Folder with <platform>/*.json taxonomy outputs (2.01)")
    parser.addoption("--input-dir", default=os.environ.get("INPUT_DIR"),
                     help="Folder with the <platform>/*.csv that was labelled (checks that every path got an output)")
    parser.addoption("--sample-root", default=os.environ.get("SAMPLE_ROOT"),
                     help="<ANNOTATION_ROOT>/sample, holding smoke/, test/ and validation/")
    parser.addoption("--merged-dir", default=os.environ.get("MERGED_DIR"),
                     help="Merged structures (<ROOT_DIR>/ddd_processed/00_ingest/005_merged_structures) the samples must come from")
    parser.addoption("--ref-dir", default=os.environ.get("REF_DIR"),
                     help="Catalogue of paths (largest donation): <platform>/*.csv with a final_path column")
    parser.addoption("--results-json", default=None, help="Write the outcome of every test to this file")


@pytest.fixture(scope="session")
def inference_dir(request):
    value = request.config.getoption("--inference-dir")
    if not value:
        pytest.skip("--inference-dir not given")
    return value


@pytest.fixture(scope="session")
def input_dir(request):
    return request.config.getoption("--input-dir")


@pytest.fixture(scope="session")
def ref_dir(request):
    value = request.config.getoption("--ref-dir")
    if not value:
        pytest.skip("--ref-dir not given")
    return value


@pytest.fixture(scope="session")
def sample_root(request):
    value = request.config.getoption("--sample-root")
    if not value:
        pytest.skip("--sample-root not given")
    return value


def pytest_generate_tests(metafunc):
    if "inference_file" in metafunc.fixturenames:
        root = metafunc.config.getoption("--inference-dir")
        files = sorted(glob.glob(os.path.join(root, "*", "*.json"))) if root else []
        metafunc.parametrize("inference_file", files,
                             ids=[os.path.relpath(f, root) for f in files] if root else None)
    if "platform" in metafunc.fixturenames:
        metafunc.parametrize("platform", PLATFORMS)


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        message = ""
        if report.failed:
            message = report.longrepr.reprcrash.message if hasattr(report.longrepr, "reprcrash") else str(report.longrepr)
        _results.append({"nodeid": report.nodeid, "outcome": report.outcome, "message": message[:2000]})


def pytest_sessionfinish(session, exitstatus):
    path = session.config.getoption("--results-json")
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"created": datetime.now().isoformat(timespec="seconds"), "exit_status": int(exitstatus),
                       "tests": _results}, f, indent=2)
