import sys
import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

DATA_SAMPLE         = os.getenv("DATA_SAMPLE")
DATA_DIR            = os.getenv("DATA_DIR")
ROOT_DIR            = os.getenv("ROOT_DIR")

logger.info(f"DATA_DIR path is: {DATA_DIR}")

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

FULL_RAW_DATA_DIR   = os.path.join(ROOT_DIR, 'subs_pipeline', 'raw')
RAW_DATA_DIR        = os.path.join(ROOT_DIR, DATA_DIR, 'raw')
FEATURES_DATA_DIR   = os.path.join(ROOT_DIR, DATA_DIR, 'features')
INFERENCE_DATA_DIR  = os.path.join(ROOT_DIR, DATA_DIR, 'inference')
INSIGHTS_DATA_DIR   = os.path.join(ROOT_DIR, DATA_DIR, 'insights')
DOWNLOADS_DATA_DIR  = os.path.join(ROOT_DIR, DATA_DIR, 'downloads')


#MODELS_DIR  = os.path.join(PROJ_ROOT, 'models')
#REPORTS_DIR = os.path.join(PROJ_ROOT, 'reports')
#FIGURES_DIR = os.path.join(REPORTS_DIR, 'figures')


# Ensure the directories exist
folder_list = [
    DATA_DIR,
    RAW_DATA_DIR,
    FEATURES_DATA_DIR,
    INFERENCE_DATA_DIR,
    INSIGHTS_DATA_DIR,
    DOWNLOADS_DATA_DIR]

for folder in folder_list:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        os.chmod(folder, 0o775)  # Set permissions to rwxrwxr-x

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end="", file=sys.stderr), colorize=sys.stderr.isatty())
except ModuleNotFoundError:
    pass

