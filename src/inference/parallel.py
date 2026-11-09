"""Shared plumbing for scripts started by launchers/parallel_worker.sh.

The worker starts one process per vLLM server and calls it as

    python script.py --source_folder S --output_folder O --agent_id ID --files a.csv b.csv

The script supplies `process_file(source_file, output_file, agent)`; this
module handles the argument parsing, the loop over the bucket and the output
file naming. Output names come from the OUTPUT_PATTERN environment variable,
which the launcher uses for the same name when it decides which files are
still pending, so there is a single definition of the name.

Pattern placeholders: {platform} (name of the source folder), {n} (last "_"
part of the input file stem), {stem} (input file stem).
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Callable, List


def output_name(pattern: str, platform: str, filename: str) -> str:
    stem = os.path.splitext(filename)[0]
    return (pattern.replace("{platform}", platform)
                   .replace("{n}", stem.split("_")[-1])
                   .replace("{stem}", stem))


def write_json_atomic(path: str, obj) -> None:
    """Write to .partial, then rename: the launcher only treats complete files as done."""
    partial = f"{path}.partial"
    with open(partial, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(partial, path)


def run_bucket(files: List[str], source_folder: str, output_folder: str, agent_id: str,
               process_file: Callable, pattern: str) -> None:
    """Process this server's bucket of files one after another. A failing file is reported and skipped."""
    os.makedirs(output_folder, exist_ok=True)

    failed = []
    for idx, filename in enumerate(files):
        # filename is relative to source_folder: "file.csv", or "<platform>/file.csv" when one job covers
        # several platforms (INPUT_GLOB='*/*.csv'); the output then goes to output_folder/<platform>/
        rel_dir = os.path.dirname(filename)
        platform = os.path.basename(rel_dir) if rel_dir else os.path.basename(os.path.normpath(source_folder))
        source_file = os.path.join(source_folder, filename)
        output_file = os.path.join(output_folder, rel_dir, output_name(pattern, platform, os.path.basename(filename)))
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        try:
            process_file(source_file, output_file)
            print(f"[{agent_id}] {idx + 1}/{len(files)}: wrote {output_file}", flush=True)
        except Exception as e:
            failed.append(filename)
            print(f"[{agent_id}] FAILED {filename}: {e!r}", file=sys.stderr, flush=True)

    print(f"[{agent_id}] finished: {len(files) - len(failed)} ok, {len(failed)} failed", flush=True)
    if failed:
        print(f"[{agent_id}] failed files: {' '.join(failed)}", file=sys.stderr, flush=True)
        sys.exit(1)


def main(process_file_factory: Callable, description: str = "") -> None:
    """Entry point. `process_file_factory(agent)` returns the process_file function for this server."""
    print("START ", datetime.now(), flush=True)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--files", nargs="+", required=True, help="File names to process in source_folder.")
    parser.add_argument("--source_folder", required=True)
    parser.add_argument("--output_folder", required=True)
    parser.add_argument("--agent_id", required=True, help="Model 'id' from the YAML to send requests to.")
    args = parser.parse_args()

    os.environ["AGENT_ID"] = args.agent_id   # for code that goes through generateInference
    pattern = os.environ["OUTPUT_PATTERN"]

    from src.agents.initAgents import AgentManager   # heavy import, keep out of module load
    manager = AgentManager()                         # reads MODEL_YAML and MODEL_DIR from the environment
    if args.agent_id not in manager.agents:
        raise RuntimeError(f"No model with id '{args.agent_id}' in MODEL_YAML ({list(manager.agents)}).")
    agent = manager.get(args.agent_id)

    print(f"[{args.agent_id}] processing {len(args.files)} file(s).", flush=True)
    run_bucket(args.files, args.source_folder, args.output_folder, args.agent_id,
               process_file_factory(agent), pattern)
    print("FINISH ", datetime.now(), flush=True)
