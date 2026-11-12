# Scripts

Run everything through the Makefile (`make help`). Data paths come from `ROOT_DIR` in `.env` (see `.env.example`).
File names are `<stage>.<step>[.<substep>]_rnv_<name>.py`.

## Layout

| Folder | Stage |
|---|---|
| `0_ingest/` | Ingest, unique paths, merge, sampling |
| `1_path_standardisation/` | Map paths to the reference catalogue, validate and plot |
| `2_taxonomy/` | Taxonomy labelling, split, judge, validate, report |
| `legacy/` | Not ported to the current launchers, and partly out of date; see below |

## Scripts

| Script | Make target | Launcher | What it does |
|---|---|---|---|
| `0_ingest/0.00` ingest_dd_structures | `ingest_dd` | CPU | Ingest donated data structures |
| `0_ingest/0.01` get_unique_paths | `get_unique_paths` | CPU | Unique paths per file |
| `0_ingest/0.02` find_largest_donation | `find_largest_donation` | CPU | Largest donation per participant |
| `0_ingest/0.03` merge_structures | `merge_csv` | CPU | Merge into `005_merged_structures` |
| `0_ingest/0.04` sample_for_inference | `sample` | CPU | Sample for inference |
| `0_ingest/0.05` sample_annotation | `annotation_sample` | CPU | Sample for annotation |
| `0_ingest/0.06` clean_paths | `clean_paths` | CPU | `clean_path` column (no wrapper folders, no part numbers) for the merged structures and the catalogue |
| `1_path_standardisation/1.02` run_path_standardisation | `path_std-run SPLIT=smoke\|test\|validation`, `path_std-check`, `path_std-<platform>`, `path_std` | GPU (parallel) | **Path standardisation**: does the path hold the same data as a path in the catalogue (largest donation)? Shortlists of files and fields, then the model decides (needs `clean_paths`) |
| `1_path_standardisation/1.01.01` validate_test_id_standardisation | `id_std_val` | CPU | Validate the id-standardisation test run |
| `1_path_standardisation/1.01.02` visualisation_validation_id_standardisation | `id_std_viz` | CPU | Plots for the above |
| `2_taxonomy/2.00` select_smoke_sample | `smoke-select` | CPU | 5 mutually dissimilar paths per platform (embeddings), not in the annotation sample |
| `2_taxonomy/2.01` run_taxonomy | `taxonomy-<platform>`, `taxonomy`, `taxonomy-run-<platform>` | GPU (parallel) | **Taxonomy** (production, and smoke/test/validation via `SPLIT=`) |
| `2_taxonomy/2.02` run_judge | `judge-<platform>`, `judge` | GPU (parallel) | LLM judge (a different model) on the taxonomy outputs |
| `2_taxonomy/2.03` sample_test_validation | `taxonomy-sample` | CPU | Test and validation sets (and annotation sheets) from the merged structures, without the smoke paths |
| `2_taxonomy/2.04` test_validate_taxonomy | `taxonomy-accuracy` | CPU | Accuracy against annotations (verduyn2020) |
| `2_taxonomy/2.05` visualisation_results_taxonomy | `taxonomy-viz` | CPU | Plots for the above (verduyn2020) |
| `2_taxonomy/2.06` evaluate_human_annotations | `eval-human` | CPU | Accuracy of the kmetty2026 taxonomy against human annotations |
| `2_taxonomy/2.07` build_report | `report` | CPU | HTML report per phase |
| `2_taxonomy/2.08` annotation_examples | `examples-pool`, `examples` | CPU | 3 example paths per platform and category, for the annotation instructions |

`src/ingest/*_json_to_csv.py` (`flatten_dd`, `flatten_dd_<fb|ig|tt|x|yt>`) also run on the CPU launcher.

## Taxonomy phases

Smoke, then test, then validation. `SPLIT=smoke|test|validation` selects the phase; the sample folders are
`<ANNOTATION_ROOT>/sample/<split>/<platform>/`.

1. **Smoke sample.** `make smoke-select` (2.00) draws a pool of paths per platform from the merged structures (`ddd_processed`)
   that are not in test or validation, embeds them (`EMBEDDING_MODEL` in `.env`) and keeps 5 whose pairwise cosine similarity is below
   `SMOKE_MAX_SIM` (0.8). `make sample-check` (pytest) verifies this: 5 unique paths, similarity below the
   threshold, and that smoke, test and validation come from the merged structures and share no path.
2. **Test and validation sets.** `make taxonomy-sample` (2.03) samples both from the merged structures, leaving the smoke paths out, and writes an annotation sheet for each.
3. **Run the taxonomy.** `make taxonomy-run SPLIT=smoke` (GPU).
4. **Check.** `make inference-check SPLIT=smoke` runs `tests/test_inference_output.py` (pytest) on the output: three
   distinct taxonomy labels, confidences summing to 100 in descending order, a rationale, and one record per input
   path. If it fails, the LLM judge (`MODEL_CONFIG_JUDGE`, a different model than the taxonomy model) is submitted on
   the output and the target exits non-zero. `make judge SPLIT=...` runs the judge on its own.
5. **Report.** `make report SPLIT=smoke` writes `results/02_taxonomy/reports/<split>_report.html`:
   pytest result, taxonomy summary, judge verdicts and, when available, the comparison with human annotations.
6. **Test and validation.** Repeat 3-5 with `SPLIT=test` and `SPLIT=validation`. When the annotations are in,
   `make eval-human SPLIT=test` (2.06; label column via `LABEL_COL`, default `label`) adds accuracy, a per-label
   recall chart and the confusion matrix to the report.

pytest: `make test` runs the unit tests; the data checks skip unless their options are given (the `make` targets
pass them). pytest is in `environments/datamap_env.yml`.

## Launchers

- **GPU, `launchers/parallel_llm.sh` + `parallel_worker.sh`:** vLLM servers on N nodes, one worker process per
  server. Scripts here (2.01, 1.02) are built on `src/inference/parallel.py`: the Makefile sets `OUTPUT_PATTERN`
  (placeholders `{platform}`, `{n}`, `{stem}`), the launcher uses it to find pending files and the script uses it
  to name its output. `INPUT_GLOB='*/*.csv'` lets one job cover several platform folders (used for `SPLIT=smoke`). To port a script, copy the structure of 1.02: a `make_process_file(agent)` that returns
  `process_file(source_file, output_file)`, and `parallel.main(...)` in `__main__`.
- **CPU, `launchers/cpu_job.sh`:** `make <target>` submits it with sbatch. Override resources per run with
  `CPU_TIME`, `CPU_CPUS`, `CPU_PARTITION`, or use `LOCAL=1` to run in the current shell on an interactive node.

## legacy/

Still uses the old sequential or interactive-server workflow, and no longer matches the code it calls (the old 2.02 LLM judge was replaced by the new 2.02):

- `1.01` test_id_standardisation: works per platform inside one CSV; its outputs feed 1.01.01 and 1.01.02.
- `1.03` process_disagreements_path_std: calls an undefined `non_class_dir`.

