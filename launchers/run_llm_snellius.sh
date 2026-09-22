#!/bin/bash
#SBATCH --partition=gpu_h100
#SBATCH --nodes=1
#SBATCH --output=logs/%x.out
#SBATCH --error=logs/%x.err

#set -e

#mkdir -p logs

echo "=========================================="
echo "Job started at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Hostname: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "=========================================="
#--------------------------------------------------
# Config
#--------------------------------------------------

# Name of the YAML file (e.g. gpt_oss_20b.yaml)
#MODEL_CONFIG=${MODEL_CONFIG:-gpt-oss-20b.yaml}

MODEL_YAML="$PWD/configs/$MODEL_CONFIG"
MODEL_DIR="/projects/prjs2007/models"

LOG_DIR="$PWD/logs"

mkdir -p "$LOG_DIR"
#--------------------------------------------------
# Environment
#--------------------------------------------------

ENV=$(grep "^environment:" "$MODEL_YAML" | cut -d' ' -f2)

source "$HOME/$ENV"

export VLLM_USE_FLASHINFER_CUBIN=1
export CUDA_HOME=/apps/ACC/CUDA/12.8
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

export TIKTOKEN_ENCODINGS_BASE=${PWD}/src/agents/tiktoken_encodings
export PYTHONPATH=$PWD:$PYTHONPATH

export MODEL_YAML
export MODEL_DIR



#--------------------------------------------------
# Start vLLM servers
#--------------------------------------------------

READY_FILE="logs/servers_ready"

rm -f "$READY_FILE"

python -u src/agents/startServers.py \
    --config "$MODEL_YAML" &

SERVER_PID=$!

echo "Server launcher PID: $SERVER_PID"
#--------------------------------------------------
# Wait for servers
#--------------------------------------------------


until [ -f "$READY_FILE" ]; do
    echo "Waiting for vLLM servers..."
    sleep 5
done

echo "All servers ready"

#--------------------------------------------------
# Run inference
#--------------------------------------------------
PYTHON_SCRIPT=${PYTHON_SCRIPT}
SCRIPT_NAME=$(basename "$PYTHON_SCRIPT" .py)
INPUT_NAME=$(basename "$INPUT_FILE" .csv)

python -u "$PYTHON_SCRIPT" \
    > "$LOG_DIR/${SCRIPT_NAME}_${INPUT_NAME}.out" \
    2> "$LOG_DIR/${SCRIPT_NAME}_${INPUT_NAME}.err"


echo "Job finished at: $(date '+%Y-%m-%d %H:%M:%S')"