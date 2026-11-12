"""Settings for the scripts, read from the environment and .env.

Precedence: real environment variables (for example the ones `make` exports, so a Makefile setting or
`make ... VAR=x` wins) > .env in the repository root > the defaults below. Copy .env.example to .env.

Importing this module has no side effects besides loading .env: it does not create folders (call
ensure_dirs() for that) and it does not fail when a variable is missing (call require() in the code that
needs it, which names the missing variables).
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJ_ROOT = Path(__file__).resolve().parents[1]

# Does not overwrite variables that are already set in the environment
load_dotenv(PROJ_ROOT / ".env")


def _join(*parts):
    """os.path.join, or None when a part is missing (unset variable)."""
    return None if any(p is None for p in parts) else os.path.join(*parts)


def require(*names):
    """Return the values of the named settings; stop with a clear message if any is unset."""
    missing = [n for n in names if not globals().get(n)]
    if missing:
        raise SystemExit(f"Missing setting(s) {', '.join(missing)}: set them in {PROJ_ROOT / '.env'} (see .env.example)")
    return tuple(globals()[n] for n in names) if len(names) > 1 else globals()[names[0]]


# ---- Paths (.env) ----
ROOT_DIR = os.getenv("ROOT_DIR")                # data root, e.g. /projects/prjs2007/data_donation
DATA_DIR = os.getenv("DATA_DIR")                # processed-data folder under ROOT_DIR, e.g. ddd_processed
MODEL_DIR = os.getenv("MODEL_DIR")              # downloaded models
DATA_SAMPLE = os.getenv("DATA_SAMPLE")

FULL_RAW_DATA_DIR = _join(ROOT_DIR, "subs_pipeline", "raw")
RAW_DATA_DIR = _join(ROOT_DIR, DATA_DIR, "raw")
FEATURES_DATA_DIR = _join(ROOT_DIR, DATA_DIR, "features")
INFERENCE_DATA_DIR = _join(ROOT_DIR, DATA_DIR, "inference")
INSIGHTS_DATA_DIR = _join(ROOT_DIR, DATA_DIR, "insights")
DOWNLOADS_DATA_DIR = _join(ROOT_DIR, DATA_DIR, "downloads")

MERGED_STRUCTURES_DIR = _join(ROOT_DIR, DATA_DIR, "00_ingest", "005_merged_structures")

# ---- Taxonomy (2_taxonomy) ----
ANNOTATION_ROOT = os.getenv("ANNOTATION_ROOT") or _join(ROOT_DIR, "ddd_annotation")
REPORT_DIR = os.getenv("REPORT_DIR") or str(PROJ_ROOT / "results" / "02_taxonomy" / "reports")
RESULTS_DIR = str(PROJ_ROOT / "results" / "02_taxonomy")

DATA_TAX = os.getenv("DATA_TAX", "kmetty2026")              # key in PROMPTS in 2.01 and 2.02
# Existing storage folder name for the output. kmetty2026 keeps the original folder; another prompt gets its own,
# so that outputs of different prompts are never mixed.
INFERENCE_SUBDIR = os.getenv("INFERENCE_SUBDIR") or "02_path_classification" + ("" if DATA_TAX == "kmetty2026" else f"_{DATA_TAX}")
COUNTRIES = os.getenv("COUNTRIES", "ES_NL")                 # tag in output file names
MODEL_CONFIG = os.getenv("MODEL_CONFIG", "")                # configs/<file>.yaml of the taxonomy model
MODEL_CONFIG_JUDGE = os.getenv("MODEL_CONFIG_JUDGE", "")    # configs/<file>.yaml of the judge
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")              # sentence-transformers model for the smoke sample
LABEL_COL = os.getenv("LABEL_COL", "label")                 # human label column in the annotation files

SMOKE_K = int(os.getenv("SMOKE_K", 5))                      # paths per platform in the smoke sample
SMOKE_MAX_SIM = float(os.getenv("SMOKE_MAX_SIM", 0.8))      # all pairs must have cosine similarity below this
SMOKE_POOL = int(os.getenv("SMOKE_POOL", 2000))             # candidates drawn per platform
SEED = int(os.getenv("SEED", 42))
TEST_N = int(os.getenv("TEST_N", 20))                     # paths per platform in the test set (2.03)
VALIDATION_N = int(os.getenv("VALIDATION_N", 80))          # paths per platform in the validation set (2.03)

EXAMPLES_POOL_N = int(os.getenv("EXAMPLES_POOL_N", 500))   # paths per platform the model labels for the examples (2.08)
EXAMPLES_K = int(os.getenv("EXAMPLES_K", 3))                # example paths per platform and category (2.08)

PLATFORMS = ["facebook", "instagram", "tiktok", "youtube", "x"]


def inference_dir(split):
    """Folder with the taxonomy output (<platform>/*.json) for smoke, test or validation."""
    return _join(ANNOTATION_ROOT, "inference", INFERENCE_SUBDIR, split)


def judge_dir(split):
    return _join(ANNOTATION_ROOT, "inference", "03_judge", split)


def sample_dir(split):
    """Folder with the sampled paths (<platform>/*.csv) for smoke, full, test or validation."""
    return _join(ANNOTATION_ROOT, "sample", split)


def annotation_dir(split):
    return _join(ANNOTATION_ROOT, "annotation", split)


def ensure_dirs():
    """Create the data folders. Not called on import."""
    for folder in (RAW_DATA_DIR, FEATURES_DATA_DIR, INFERENCE_DATA_DIR, INSIGHTS_DATA_DIR, DOWNLOADS_DATA_DIR):
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            os.chmod(folder, 0o775)  # rwxrwxr-x
