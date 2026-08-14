


LOG_DIR="$PWD/logs"

mkdir -p "$LOG_DIR"

#--------------------------------------------------
# Config
#--------------------------------------------------

# Name of the YAML file (e.g. gpt_oss_20b.yaml)
MODEL_CONFIG=${MODEL_CONFIG}

MODEL_YAML="$PWD/configs/$MODEL_CONFIG"
MODEL_DIR="/projects/prjs2007/models"
export MODEL_YAML
export MODEL_DIR

#--------------------------------------------------
# Environment
#--------------------------------------------------

ENV=$(grep "^environment:" "$MODEL_YAML" | cut -d' ' -f2)

source "$HOME/$ENV"

export VLLM_USE_FLASHINFER_CUBIN=1
export CUDA_HOME=/apps/ACC/CUDA/12.8


export TIKTOKEN_ENCODINGS_BASE=${PWD}/src/agents/tiktoken_encodings
export PYTHONPATH=$PWD:$PYTHONPATH
#--------------------------------------------------
# Run inference
#--------------------------------------------------
PYTHON_SCRIPT=${PYTHON_SCRIPT}
SCRIPT_NAME=$(basename "$PYTHON_SCRIPT" .py)

python -u "$PYTHON_SCRIPT" \
    > "$LOG_DIR/${SCRIPT_NAME}.out" \
    2> "$LOG_DIR/${SCRIPT_NAME}.err"

echo "Inference completed"