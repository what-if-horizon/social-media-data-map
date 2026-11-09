#!/bin/bash
# Per-node worker for parallel_llm.sh.
#
# Starts this node's vLLM servers (one per entry in $MODEL_YAML, typically
# one per GPU), waits until they are all ready, then splits this node's
# bucket of files across those servers and runs one $MODULE_PATH process
# per server, each independent of the others:
#
#   parallel_llm.sh:    files -> one bucket per node
#   parallel_worker.sh: node bucket -> one bucket per server
#   MODULE_PATH:        loops over its bucket on its one server

# treat unset variables as an error
set -u      

NODE_RANK=$1
shift
files=("$@")

#--------------------------------------------------
# Config
#--------------------------------------------------

SERVER_TIMEOUT=1200   # seconds to wait for the vLLM servers

# This node's logs (read by startServers.py)
export VLLM_LOG_DIR="$JOB_LOG_DIR/node${NODE_RANK}"
export SERVERS_READY_FILE="$VLLM_LOG_DIR/servers_ready"
mkdir -p "$VLLM_LOG_DIR"

#--------------------------------------------------
# Start servers
#--------------------------------------------------

echo "[node $NODE_RANK] $(hostname): starting vLLM servers"
python -u src/agents/startServers.py --config "$MODEL_YAML" &
server_pid=$! # process ID of the startServers.py process

# Kill the servers when this worker exits, however it exits
trap 'pkill -P $server_pid; kill $server_pid 2>/dev/null' EXIT

waited=0
until [[ -f "$SERVERS_READY_FILE" ]]; do
    if ! kill -0 "$server_pid" 2>/dev/null; then
        echo "[node $NODE_RANK] Server launcher died, see $VLLM_LOG_DIR" >&2
        exit 1
    fi
    if (( waited >= SERVER_TIMEOUT )); then
        echo "[node $NODE_RANK] Servers not ready after ${SERVER_TIMEOUT}s, see $VLLM_LOG_DIR" >&2
        exit 1
    fi
    sleep 5
    waited=$(( waited + 5 ))
done
echo "[node $NODE_RANK] All servers ready"

#--------------------------------------------------
# Split this node's files across servers
#--------------------------------------------------

# One server per model entry in the YAML, named by its `id:`
server_ids=($(awk '/^ *- id:/ {print $3}' "$MODEL_YAML"))
num_servers=${#server_ids[@]}
(( num_servers > 0 )) || { echo "[node $NODE_RANK] No '- id:' entries in $MODEL_YAML" >&2; exit 1; }

server_files=()
for i in "${!files[@]}"; do
    index=$(( i % num_servers ))
    server_files[$index]+="${files[i]} "
done
echo "[node $NODE_RANK] ${#files[@]} files across $num_servers servers"

#--------------------------------------------------
# Launch one module process per server
#--------------------------------------------------

pids=()
for i in "${!server_ids[@]}"; do
    if [[ -n "${server_files[i]:-}" ]]; then
        server_id=${server_ids[i]}
        python -u "$MODULE_PATH" \
            --source_folder "$SOURCE_FOLDER" \
            --output_folder "$OUTPUT_FOLDER" \
            --agent_id "$server_id" \
            --files ${server_files[i]} \
            > "$VLLM_LOG_DIR/${server_id}.out" \
            2> "$VLLM_LOG_DIR/${server_id}.err" &
        pids+=($!)
    fi
done

#--------------------------------------------------
# Wait for all module processes to finish
#--------------------------------------------------

status=0
for pid in "${pids[@]}"; do
    wait "$pid" || status=1
done
echo "[node $NODE_RANK] Done."
exit $status
