#--------------------------------------------------------------------
# Libraries
#--------------------------------------------------------------------

import yaml                  # Load YAML configuration files
import subprocess            # Launch background vLLM processes
import os                    # Environment variables and filesystem utilities
import argparse              # Command-line argument parsing
import time                  # Sleep while waiting for servers
from pathlib import Path     # Object-oriented filesystem paths
import requests


#--------------------------------------------------------------------
# Global log directory
#--------------------------------------------------------------------

# Directory where vLLM stdout/stderr logs are stored
LOG_DIR = "logs"

# Create directory if it does not exist
os.makedirs(LOG_DIR, exist_ok=True)


#--------------------------------------------------------------------
# launch_model()
#--------------------------------------------------------------------

def launch_model(cfg, model_dir, max_model_len, gpu_memory_utilization):

    # Model name from YAML
    name = cfg["name"]

    # OpenAI server port
    port = cfg["port"]

    # Server already fully running
    if server_ready(port):
        print(f"{name} already running and ready on port {port}")
        return

    # Convert GPU list to CUDA_VISIBLE_DEVICES format
    # Example: [0,1] -> "0,1"
    gpus = ",".join(map(str, cfg["gpus"]))

    # Tensor parallelism size
    tp = cfg["tensor_parallel"]

    # Full model path
    model_path = f"{model_dir}/{name}"

    # Log filename
    # "/" replaced because it cannot appear in filenames
    log_file = Path(LOG_DIR) / f"{name.replace('/', '_')}.log"

    # Copy current environment
    env = os.environ.copy()

    # Restrict visible GPUs for this process
    env["CUDA_VISIBLE_DEVICES"] = gpus

    # vLLM launch command
    cmd = [
        "python", "-m", "vllm.entrypoints.openai.api_server",

        # Model path
        "--model", model_path,

        # Model name exposed through OpenAI API
        "--served-model-name", name,

        # API port
        "--port", str(port),

        # Tensor parallel size
        "--tensor-parallel-size", str(tp),

        # Maximum sequence length
        "--max-model-len", str(max_model_len),

        # Fraction of GPU memory to use
        "--gpu-memory-utilization", str(gpu_memory_utilization),

        # Disable CUDA graph capture
        "--enforce-eager",
    ]

    print(f"Launching {name} on GPUs {gpus} (TP={tp}) port={port}")

    # Launch process in background
    # stdout/stderr redirected to log file
    f = open(log_file, "w")

    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=f,
        stderr=f
    )

    return proc


#--------------------------------------------------------------------
# server_ready()
#--------------------------------------------------------------------


def server_ready_old(logfile):

    # Log does not exist yet
    if not logfile.exists():
        return False

    try:

        # Read entire log file
        with open(logfile, "r") as f:
            content = f.read()

        # vLLM prints this when startup succeeds
        return "Application startup complete" in content

    except Exception:

        # Any read/parsing failure -> not ready
        return False


def server_ready(port):

    url = f"http://localhost:{port}/v1/models"

    try:
        r = requests.get(url, timeout=2)

        if r.status_code != 200:
            return False

        data = r.json()

        return "data" in data

    except Exception:
        return False


#--------------------------------------------------------------------
# wait_for_servers()
#--------------------------------------------------------------------

def wait_for_servers(config, interval=5):

    print("Waiting for vLLM servers to start...")

    # Expected logfiles for all models
    logfiles = [
        Path(LOG_DIR) / f"{m['name'].replace('/', '_')}.log"
        for m in config["models"]
    ]

    # Poll until all servers are ready
    while True:

        """
        
        # Check if every logfile contains startup success message
        ready = all(
            server_ready(logfile)
            for logfile in logfiles
        )
        """
        ready = all(
            server_ready(model["port"])
            for model in config["models"]
        )

        # Exit loop when all servers are ready
        if ready:
            print("All vLLM servers are ready.")

            Path("logs/servers_ready").touch()
            return

        # Wait before checking again
        time.sleep(interval)


#--------------------------------------------------------------------
# main()
#--------------------------------------------------------------------

def main():

    # Command-line parser
    parser = argparse.ArgumentParser()

    # YAML configuration path
    parser.add_argument(
        "--config",
        required=True
    )

    # Parse CLI arguments
    args = parser.parse_args()

    # Load YAML configuration
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    # Global settings from YAML
    model_dir = config["model_dir"]
    max_model_len = config["max_model_len"]
    gpu_memory_utilization = config["gpu_memory_utilization"]

    #--------------------------------------------------------
    # Remove old log files
    #--------------------------------------------------------

    for logfile in Path(LOG_DIR).glob("*.log"):
        logfile.unlink()

    #--------------------------------------------------------
    # Launch all configured models
    #--------------------------------------------------------

    processes = []

    for model in config["models"]:

        proc = launch_model(
            model,
            model_dir,
            max_model_len,
            gpu_memory_utilization
        )

        # launch_model returns None if server already exists
        if proc is not None:
            processes.append(proc)

    print("All servers launched.")

    #--------------------------------------------------------
    # Wait until all servers are ready
    #--------------------------------------------------------

    wait_for_servers(config)
    
    

    #--------------------------------------------------------
    # Keep parent process alive
    #--------------------------------------------------------

    print("Waiting on vLLM processes...")

    for proc in processes:
        proc.wait()
#--------------------------------------------------------------------
# Entry point
#--------------------------------------------------------------------

if __name__ == "__main__":
    main()