#!/bin/bash
#SBATCH --job-name=parallel_llm
#SBATCH --output=logs/parallel_llm_%j.out
#SBATCH --error=logs/parallel_llm_%j.err
#SBATCH --ntasks-per-node=1

#--------------------------------------------------
# Config
#--------------------------------------------------

MODEL_CONFIG=${MODEL_CONFIG:-qwen_2_5_7b_tp1x4.yaml}
MODEL_YAML="$PWD/configs/$MODEL_CONFIG"

: "${MODEL_DIR:?MODEL_DIR must be set (see .env)}"
: "${SOURCE_FOLDER:?SOURCE_FOLDER must be set}"
: "${OUTPUT_FOLDER:?OUTPUT_FOLDER must be set}"
: "${DATA_TAX:?DATA_TAX must be set}"
: "${COUNTRIES:?COUNTRIES must be set}"
: "${MODULE_PATH:?MODULE_PATH must be set (python script each server runs on its files)}"

[[ -f "$MODEL_YAML" ]]  || { echo "Config not found: $MODEL_YAML" >&2; exit 1; }
[[ -f "$MODULE_PATH" ]] || { echo "Module not found: $MODULE_PATH" >&2; exit 1; }

JOB_LOG_DIR="$PWD/logs/${SLURM_JOB_NAME}_${SLURM_JOB_ID}"
mkdir -p "$JOB_LOG_DIR"
mkdir -p "$OUTPUT_FOLDER"
chmod 775 "$OUTPUT_FOLDER"
export MODEL_YAML JOB_LOG_DIR

#--------------------------------------------------
# Environment
#--------------------------------------------------

ENV=$(grep "^environment:" "$MODEL_YAML" | cut -d' ' -f2)

source "$HOME/$ENV"

module purge
module load 2023
module load CUDA/12.1.1          # TODO: other launchers use CUDA_HOME=/apps/ACC/CUDA/12.8; check with: module avail CUDA


export PYTHONPATH="$PWD:${PYTHONPATH:-}"
export TIKTOKEN_ENCODINGS_BASE="$PWD/src/agents/tiktoken_encodings"
export CUDA_HOME="$EBROOTCUDA"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

#--------------------------------------------------
# Pending files
#--------------------------------------------------

# Delete leftovers from crashed runs
rm -f "$OUTPUT_FOLDER"/*.partial

# Output name; must match scripts/2.01_rnv_run_data_classification.py
# {platform}_{n}_class_ids_{tax}_{countries}_{model}.json
PLATFORM=$(basename "$SOURCE_FOLDER")
MODEL_NAME="${MODEL_CONFIG%.yaml}"
output_name() {   # $1 = input csv file name
    local stem="${1%.csv}"
    echo "${PLATFORM}_${stem##*_}_class_ids_${DATA_TAX}_${COUNTRIES}_${MODEL_NAME}.json"
}

files=()
for file_path in "$SOURCE_FOLDER"/*.csv; do
    file_name=$(basename "$file_path")
    if [[ ! -f "$OUTPUT_FOLDER/$(output_name "$file_name")" ]]; then
        files+=("$file_name")
    fi
done
echo "Pending files: ${#files[@]}"

#--------------------------------------------------
# Split pending files across nodes
#--------------------------------------------------

node_files=()
for i in "${!files[@]}"; do
    index=$(( i % SLURM_NNODES ))
    node_files[$index]+="${files[i]} "
done

#--------------------------------------------------
# Launch one worker per node
#--------------------------------------------------

for ((i=0; i<SLURM_NNODES; i++)); do
    if [[ -n "${node_files[i]}" ]]; then
        srun --export=ALL --exclusive -N1 -n1 --gres=gpu:${GPUS_PER_NODE:-4} \
            launchers/parallel_worker.sh "$i" ${node_files[i]} &
    fi
done

#--------------------------------------------------
# Wait for all workers to finish
#--------------------------------------------------

status=0
for pid in $(jobs -p); do
    wait "$pid" || status=1
done
echo "All nodes finished."
exit $status