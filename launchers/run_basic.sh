# To run this script: 
# make scrape_links
# make scrape_docs


#!/bin/bash

set -e

ROOT=$1
PYTHON_SCRIPT=$2

LOG_DIR="$ROOT/logs"

mkdir -p "$LOG_DIR"

SCRIPT_NAME=$(basename "$PYTHON_SCRIPT" .py)

# Activate conda
source ~/miniforge3/etc/profile.d/conda.sh
conda activate datamap_env

#pip install e .

export PROJECT_ROOT="$ROOT"

echo "Running $PYTHON_SCRIPT"
echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "Python=$(which python)"

python -u "$PYTHON_SCRIPT" \
    > "$LOG_DIR/${SCRIPT_NAME}.out" \
    2> "$LOG_DIR/${SCRIPT_NAME}.err"