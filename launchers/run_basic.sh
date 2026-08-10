#!/bin/bash

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_SCRIPT=$1

LOG_DIR="$ROOT/logs"

mkdir -p "$LOG_DIR"

SCRIPT_NAME=$(basename "$PYTHON_SCRIPT" .py)

source ~/miniforge3/etc/profile.d/conda.sh
conda activate datamap_env

export PROJECT_ROOT="$ROOT"
export PYTHONPATH=$PWD:$PYTHONPATH

echo "Running $PYTHON_SCRIPT"
echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "Python=$(which python)"

python -u "$ROOT/$PYTHON_SCRIPT" \
    > "$LOG_DIR/${SCRIPT_NAME}.out" \
    2> "$LOG_DIR/${SCRIPT_NAME}.err"
