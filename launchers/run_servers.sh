#!/bin/bash
#SBATCH --account=bsc100
#SBATCH --qos=acc_debug
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=80
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

MODEL_YAML="$PWD/configs/gpt_oss_20b.yaml"

ENV=$(grep "^environment:" "$MODEL_YAML" | cut -d' ' -f2)

source ~/miniforge3/etc/profile.d/conda.sh
conda activate "$ENV"

export VLLM_USE_FLASHINFER_CUBIN=1
export CUDA_HOME=/apps/ACC/CUDA/12.8
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# Necessary when running gpt-oss-20b
export TIKTOKEN_ENCODINGS_BASE=${PWD}/src/RbLib/agents/tiktoken_encodings

mkdir -p logs

#--------------------------------------------------
# Inject compute-node hostname into YAML
#--------------------------------------------------

python src/RbLib/agents/startServers.py --config "$MODEL_YAML"