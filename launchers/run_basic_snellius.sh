#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err

set -e

#ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$PWD"
PYTHON_SCRIPT=$1

LOG_DIR="$ROOT/logs"

echo "0=$0"
echo "PWD=$PWD"
echo "dirname=$(dirname "$0")"

mkdir -p "$LOG_DIR"

SCRIPT_NAME=$(basename "$PYTHON_SCRIPT" .py)

module load 2025
module load Python/3.13.5-GCCcore-14.3.0
source ~/venvs/social-media-data-map/bin/activate

export PROJECT_ROOT="$ROOT"
export PYTHONPATH=$PWD:$PYTHONPATH

echo "Running $PYTHON_SCRIPT"
echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "Python=$(which python)"

python -u "$ROOT/$PYTHON_SCRIPT" \
    > "$LOG_DIR/${SCRIPT_NAME}.out" \
    2> "$LOG_DIR/${SCRIPT_NAME}.err"
