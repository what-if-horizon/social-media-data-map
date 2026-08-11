#!/bin/bash
#SBATCH --account=bsc100
#SBATCH --qos=acc_bsccssh
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=80
#SBATCH --output=logs/%x.out
#SBATCH --error=logs/%x.err

#set -e

#mkdir -p logs

#--------------------------------------------------
# Config
#--------------------------------------------------

# Name of the YAML file (e.g. gpt_oss_20b.yaml)
MODEL_CONFIG=${MODEL_CONFIG:-gpt-oss-20b.yaml}

MODEL_YAML="$PWD/configs/$MODEL_CONFIG"
MODEL_DIR="/gpfs/projects/bsc100/models"

LOG_DIR="$PWD/logs"

mkdir -p "$LOG_DIR"
#--------------------------------------------------
# Environment
#--------------------------------------------------

ENV=$(grep "^environment:" "$MODEL_YAML" | cut -d' ' -f2)

source ~/miniforge3/etc/profile.d/conda.sh
conda activate "$ENV"

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

python -u "$PYTHON_SCRIPT" \
    > "$LOG_DIR/${SCRIPT_NAME}.out" \
    2> "$LOG_DIR/${SCRIPT_NAME}.err"

echo "Inference completed"