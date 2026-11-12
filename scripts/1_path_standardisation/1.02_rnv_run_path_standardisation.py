"""
Path standardisation: does a path point to the same data as a path in the catalogue?

The catalogue of a platform is its largest donation. For every input path the result is the catalogue path that holds
the same data, or "NA". Two methods, chosen with PATH_STD (config / Makefile):

  path_shortlist2026 (default)  src/inference/pathshortlist.py. The paths are cleaned in the ingest step (0.06, `make
                    clean_paths`: no wrapper folders, no part numbers). Exact and clean matches need no model. For the
                    rest the model matches files and then fields, each time from a numbered shortlist of candidates
                    chosen with multilingual embeddings (PATH_EMBEDDING_MODEL, SHORTLIST_K).
  path_std2026      The whole catalogue is put in the prompt (prompt path_std2026 in src/inference/prompts.py). Kept
                    to compare with the shortlist method.

Runs as one process per vLLM server, started by launchers/parallel_worker.sh:
  make path_std-run SPLIT=smoke|test|validation    the smoke, test or validation sample
  make path_std                                    all merged structures
Each input CSV (`final_path` column) is processed against the one server given by --agent_id; output is one JSON per
input CSV, named by OUTPUT_PATTERN (set by the Makefile). Output records:
  {"path", "match" (catalogue path or NA), "rationale", "method"}   (the shortlist method adds "file_match")
  method: exact | clean | llm | file_na  (path_std2026: exact | llm)
A path without a valid answer after three tries goes to a sibling "_failed" file. tests/test_path_std_output.py checks
the output.
"""

import glob
import os
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

# PYTHONPATH is the repo root (set by the launcher)
from src import config
from src.inference import parallel
from src.inference import prompts as p
from src.inference import utils as u
from src.inference.pathmatch import NA, build_path_prompt, catalogue_text, parse_match
from src.inference.pathshortlist import Catalogue, ShortlistMatcher
from src.inference.retrieval import Embedder

COL_PATH = "final_path"
MAX_RETRIES = 3
CONCURRENCY = 100

PATH_STD = config.PATH_STD
METHODS = ("path_shortlist2026", "path_std2026")
if PATH_STD not in METHODS:
    raise SystemExit(f"Unknown PATH_STD '{PATH_STD}', expected one of {list(METHODS)}")


def first_csv(folder):
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    if not files:
        raise SystemExit(f"No csv in {folder}")
    return files[0]


# -------------------------------------------------------------------------------------------------------------
# path_shortlist2026
# -------------------------------------------------------------------------------------------------------------

def load_cleaned_catalogue(platform):
    """(paths, clean paths) of the catalogue, from the ingest step 0.06."""
    config.require("CLEANED_CATALOGUE_DIR")
    folder = os.path.join(config.CLEANED_CATALOGUE_DIR, platform)
    if not os.path.isdir(folder):
        raise SystemExit(f"{folder} does not exist: run `make clean_paths` (ingest step 0.06) first")
    df = pd.read_csv(first_csv(folder), dtype=str).dropna(subset=[COL_PATH, "clean_path"]).drop_duplicates(COL_PATH)
    return df[COL_PATH].tolist(), df["clean_path"].tolist()


def load_clean_map(platform):
    """{path: clean path} for all merged structures of the platform, from the ingest step 0.06."""
    folder = os.path.join(config.CLEANED_STRUCTURES_DIR, platform)
    mapping = {}
    for f in sorted(glob.glob(os.path.join(folder, "*.csv"))):
        df = pd.read_csv(f, dtype=str).dropna(subset=[COL_PATH, "clean_path"])
        mapping.update(zip(df[COL_PATH], df["clean_path"]))
    return mapping


def make_shortlist_process_file(agent):
    embedder = Embedder(config.require("PATH_EMBEDDING_MODEL"))
    ask = lambda prompt: u.run_llm(prompt, agent)
    matchers = {}   # per platform: catalogue and its embeddings are built once per process

    def process_file(source_file, output_file):
        platform = os.path.basename(os.path.dirname(source_file))
        if platform not in matchers:
            raw, clean = load_cleaned_catalogue(platform)
            matchers[platform] = (ShortlistMatcher(Catalogue(raw, clean), embedder, ask, p.path_file2026(),
                                                   p.path_field2026(), k=config.SHORTLIST_K, workers=CONCURRENCY,
                                                   retries=MAX_RETRIES),
                                  load_clean_map(platform))
        matcher, clean_of = matchers[platform]

        paths = pd.read_csv(source_file, dtype=str)[COL_PATH].dropna().drop_duplicates().tolist()
        print(f" {os.path.basename(source_file)}: {len(paths)} paths, catalogue of {len(matcher.cat.raw_set)} paths "
              f"in {len(matcher.cat.units)} files", flush=True)
        t0 = time.time()
        ok, failed = matcher.match(paths, clean_of)
        methods = pd.Series([r["method"] for r in ok]).value_counts().to_dict()
        n_na = sum(r["match"] == NA for r in ok)
        print(f" done in {time.time() - t0:.0f}s | {len(ok)} ok ({n_na} NA), {len(failed)} failed | methods: {methods}",
              flush=True)

        parallel.write_json_atomic(output_file.replace(".json", "_failed.json"), failed)
        parallel.write_json_atomic(output_file, ok)

    return process_file


# -------------------------------------------------------------------------------------------------------------
# path_std2026: the whole catalogue in the prompt
# -------------------------------------------------------------------------------------------------------------

def load_catalogue(platform):
    """Paths of the largest donation of the platform: the first file in REF_DIR/<platform>/."""
    config.require("REF_DIR")
    ref_file = first_csv(os.path.join(config.REF_DIR, platform))
    return pd.read_csv(ref_file, dtype=str)[COL_PATH].dropna().drop_duplicates().tolist()


def run_one(path, template, catalogue, catalogue_set, agent):
    if path in catalogue_set:
        return {"path": path, "match": path, "rationale": "The path is in the catalogue.", "method": "exact"}, None
    prompt = build_path_prompt(template, catalogue, path)
    last_raw = None
    for attempt in range(1, MAX_RETRIES + 1):
        last_raw = u.run_llm(prompt, agent)
        parsed = parse_match(last_raw, catalogue_set)
        if parsed is not None:
            return {"path": path, "match": parsed["match"], "rationale": parsed["rationale"], "method": "llm"}, None
        print(f"  Invalid output (attempt {attempt}/{MAX_RETRIES}) for {path}", flush=True)
        time.sleep(1)
    return None, {"path": path, "error": "invalid output", "raw": str(last_raw)}


def make_full_catalogue_process_file(agent):
    template = p.path_std2026()

    def process_file(source_file, output_file):
        platform = os.path.basename(os.path.dirname(source_file))
        catalogue_list = load_catalogue(platform)
        catalogue, catalogue_set = catalogue_text(catalogue_list), set(catalogue_list)

        paths = pd.read_csv(source_file, dtype=str)[COL_PATH].dropna().drop_duplicates().tolist()
        print(f" {os.path.basename(source_file)}: {len(paths)} paths, {sum(x in catalogue_set for x in paths)} in the "
              f"catalogue, catalogue of {len(catalogue_list)} paths", flush=True)

        t0 = time.time()
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            results = list(pool.map(lambda x: run_one(x, template, catalogue, catalogue_set, agent), paths))  # order kept
        ok = [r for r, _ in results if r is not None]
        failed = [f for _, f in results if f is not None]
        print(f" done in {time.time() - t0:.0f}s | {len(ok)} ok ({sum(r['match'] == NA for r in ok)} NA), "
              f"{len(failed)} failed", flush=True)

        parallel.write_json_atomic(output_file.replace(".json", "_failed.json"), failed)
        parallel.write_json_atomic(output_file, ok)

    return process_file


def make_process_file(agent):
    return make_shortlist_process_file(agent) if PATH_STD == "path_shortlist2026" else make_full_catalogue_process_file(agent)


if __name__ == "__main__":
    parallel.main(make_process_file, "Path standardisation")
