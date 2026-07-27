


LOG_DIR="$PWD/logs"

mkdir -p "$LOG_DIR"

#--------------------------------------------------
# Config
#--------------------------------------------------

# Name of the YAML file (e.g. gpt_oss_20b.yaml)
MODEL_CONFIG=${MODEL_CONFIG:-gpt_oss_20b.yaml}

MODEL_YAML="$PWD/configs/$MODEL_CONFIG"
MODEL_DIR="/gpfs/projects/bsc100/models"
export MODEL_YAML
export MODEL_DIR

#--------------------------------------------------
# Environment
#--------------------------------------------------

ENV=$(grep "^environment:" "$MODEL_YAML" | cut -d' ' -f2)

source ~/miniforge3/etc/profile.d/conda.sh
conda activate "$ENV"

export VLLM_USE_FLASHINFER_CUBIN=1
export CUDA_HOME=/apps/ACC/CUDA/12.8
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

export TIKTOKEN_ENCODINGS_BASE=${PWD}/src/RbLib/agents/tiktoken_encodings

#--------------------------------------------------
# Run inference
#--------------------------------------------------
PYTHON_SCRIPT=${PYTHON_SCRIPT}
SCRIPT_NAME=$(basename "$PYTHON_SCRIPT" .py)

python -u "$PYTHON_SCRIPT" \
    > "$LOG_DIR/${SCRIPT_NAME}.out" \
    2> "$LOG_DIR/${SCRIPT_NAME}.err"

echo "Inference completed"