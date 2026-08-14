#!/bin/bash
#SBATCH --account=bsc100
#SBATCH --qos=acc_debug
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=80
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

# To ask for an interactive node srun --partition=gpu_h100 --gpus=2 --time=01:00:00 --pty bash
MODEL_YAML="${MODEL_YAML:-$PWD/configs/gpt-oss-20b.yaml}"

ENV=$(grep "^environment:" "$MODEL_YAML" | cut -d' ' -f2)

source "$HOME/$ENV"

export VLLM_USE_FLASHINFER_CUBIN=1
export CUDA_HOME=/apps/ACC/CUDA/12.8


# Necessary when running gpt-oss-20b
export TIKTOKEN_ENCODINGS_BASE=${PWD}/src/agents/tiktoken_encodings
export PYTHONPATH=$PWD:$PYTHONPATH

mkdir -p logs

#--------------------------------------------------
# Inject compute-node hostname into YAML
#--------------------------------------------------

python src/agents/startServers.py --config "$MODEL_YAML"

