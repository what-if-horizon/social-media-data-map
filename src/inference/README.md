# src/inference

Code behind the LLM steps: path standardisation (`scripts/1_path_standardisation`) and the taxonomy
(`scripts/2_taxonomy`). The scripts are thin; the logic is here, so it can be tested without a model (`tests/`).

Nothing in this folder starts a model. A script gets an `agent` (a vLLM server, `src/agents`) from the launcher
(`launchers/parallel_worker.sh`) and passes it in, or, for the shortlist method, passes an `ask` function and an
`embedder`.

## Path standardisation

For every path, find the path of the catalogue (the largest donation of a platform) that holds the same data, or `NA`.
Three methods, chosen with `PATH_STD`; details and output format in
[scripts/1_path_standardisation/README.md](../../scripts/1_path_standardisation/README.md).

| File | What it does |
|---|---|
| [pathembed.py](pathembed.py) | Default method (`path_embed2026`): exact and clean as in the other shortlist method, but no split between file and field. The model chooses among the `SHORTLIST_K` whole catalogue paths most similar to the path (`EmbedMatcher`, a subclass of `ShortlistMatcher`). Records hold the `shortlist` shown. |
| [pathshortlist.py](pathshortlist.py) | Method `path_shortlist2026`, with a split between file and field. Steps exact, clean, file, field. The model only sees a numbered shortlist and answers with a number, so it cannot return a path that is not in the catalogue. `Catalogue` holds the catalogue, `ShortlistMatcher.match` does the work. Records of paths that needed the model also hold the shortlists that were shown (`file_shortlist`, `field_shortlist`; development). |
| [retrieval.py](retrieval.py) | `Embedder` (multilingual sentence embeddings on the CPU, so it does not compete with the vLLM servers for GPU memory), `embed_text`, and `top_k` (plain numpy). |
| [pathmatch.py](pathmatch.py) | Method `path_std2026`: the whole catalogue goes in the prompt. Kept to compare with the shortlist method. Also `validate_match_record`, used by the output test. |

Prompts: `path_file2026` (which catalogue file), `path_field2026` (which field), `path_embed2026` (which whole path), `path_std2026` (whole catalogue).

## Taxonomy

Classify a path into the DDP topology (15 labels) with the three most likely labels and confidence scores.

| File | What it does |
|---|---|
| [taxonomy.py](taxonomy.py) | Pure helpers: build the prompt for a path, read the labels from the prompt (`valid_labels`), parse and validate the model output, `extract_json_dict` (also used by the path standardisation). |
| [judge.py](judge.py) | LLM judge: a different model reads the taxonomy, the path and the ranked predictions and says whether the top label is correct, plausible or incorrect. |
| [evaluation.py](evaluation.py) | Accuracy and confusion of the taxonomy model against human annotations. |
| [report.py](report.py) | One self-contained HTML report per phase (smoke, test, validation): pytest result, summary, judge, human evaluation. |
| [similarity.py](similarity.py) | Cosine similarity helpers to pick a small, diverse smoke sample (`select_diverse`). |

Prompt: `kmetty2026` (`kmetty2026_simple` is a shorter variant).

## Shared

| File | What it does |
|---|---|
| [prompts.py](prompts.py) | All current prompts. Prompts contain JSON braces, so they are filled with plain `replace`, not `str.format`. |
| [parallel.py](parallel.py) | Plumbing for scripts started by `launchers/parallel_worker.sh`: argument parsing, the loop over the files of a bucket, output file names (`OUTPUT_PATTERN`) and atomic JSON writing. A script supplies `process_file(source_file, output_file, agent)`. |
| [utils.py](utils.py) | `run_llm`: one request to an agent (temperature 0, seed 42; overrides allowed). |

## Legacy

Used only by the old ID standardisation (`scripts/legacy`, `1.01.01_rnv_validate_test_id_standardisation.py`). Not
used by the current pipeline.

- [idStandardisation.py](idStandardisation.py), [dataTaxonomy.py](dataTaxonomy.py), [generateInference.py](generateInference.py)
- [legacy/prompts.py](legacy/prompts.py): the prompts of the ID standardisation.

## Tests

`tests/test_path_shortlist.py` and `tests/test_path_std.py` (path standardisation, with a fake model and a fake
embedder), `tests/test_taxonomy.py`, `tests/test_judge_report.py`, `tests/test_similarity.py`, and the output tests
`tests/test_path_std_output.py` and `tests/test_inference_output.py` (run by `make path_std-check` and
`make inference-check`).
