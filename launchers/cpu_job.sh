#!/bin/bash
# Launcher for jobs that do not need a GPU (ingest, sampling, validation, plots, ...).
#
#   sbatch [resources] launchers/cpu_job.sh scripts/0_ingest/0.01_rnv_get_unique_paths.py [args...]
#   bash launchers/cpu_job.sh scripts/...py     # run directly, e.g. on an interactive node
#
# Resources (time, cpus, partition, account) are given to sbatch by the Makefile
# (`make help`), so they can be set per job. The defaults below only apply when
# this file is submitted without them.
#
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=01:00:00

set -euo pipefail

SCRIPT=${1:?usage: cpu_job.sh <python script> [args...]}
shift

# sbatch runs a copy of this file, so locate the repo from the submit directory
ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$ROOT"
[[ -f "$SCRIPT" ]] || { echo "Script not found: $ROOT/$SCRIPT" >&2; exit 1; }

#--------------------------------------------------
# Environment
#--------------------------------------------------

module load 2025
module load Python/3.13.5-GCCcore-14.3.0
source "$HOME/venvs/social-media-data-map/bin/activate"

export PROJECT_ROOT="$ROOT"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

echo "Job:    ${SLURM_JOB_ID:-local} on $(hostname)"
echo "Script: $SCRIPT $*"
echo "Python: $(which python)"
echo "Start:  $(date '+%Y-%m-%d %H:%M:%S')"

python -u "$SCRIPT" "$@"

echo "Finish: $(date '+%Y-%m-%d %H:%M:%S')"
