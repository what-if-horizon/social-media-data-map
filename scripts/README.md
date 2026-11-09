# Scripts

Numbering: `<stage>.<step>[.<substep>]_rnv_<name>.py`. Run them through the Makefile (`make help`).
Data paths come from `ROOT_DIR` in `.env` (see `.env.example`).

| Script | Make target | What it does |
|---|---|---|
| 0.00 ingest_dd_structures | `ingest_dd` | Ingest donated data structures |
| 0.01 get_unique_paths | `get_unique_paths` | Unique paths per file |
| 0.02 find_largest_donation | `find_largest_donation` | Largest donation per participant |
| 0.03 merge_structures | `merge_csv` | Merge structures into `005_merged_structures` |
| 0.04 sample_for_inference | `sample` | Sample for inference |
| 0.05 sample_annotation | `annotation_sample` | Sample for annotation |
| 1.01 test_id_standardisation | (legacy launcher, no target) | Id standardisation test run |
| 1.01.01 validate_test_id_standardisation | `id_std_val` | Validate the above |
| 1.01.02 visualisation_validation_id_standardisation | `id_std_viz` | Plots for the above |
| **1.02 run_path_standardisation** | `path_std-<platform>`, `path_std` | **Path standardisation** (`launchers/parallel_llm.sh`) |
| 1.02.01 run_path_standardisation_seq | (none) | Sequential variant, superseded by 1.02; can be deleted |
| 1.03 process_disagreements_path_std | (legacy launcher, no target) | Resolve disagreements |
| **2.01 run_data_classification** | `taxonomy-<platform>`, `taxonomy` | **Production taxonomy classification** (`launchers/parallel_llm.sh`) |
| 2.01.01 run_test_data_classification | (none) | Superseded by `taxonomy-eval-<platform> SPLIT=test|validation` (runs 2.01 on the annotation sample); can be deleted |
| 2.02 test_data_classification_LLM | (no target) | LLM judge on classification output |
| 2.03 split_data_data_classification | `data_class_split` | Split into test/validation |
| 2.04 test_validate_data_classification | `data_class_test_val` | Accuracy against annotations |
| 2.05 visualisation_results_data_classification | `data_class_viz` | Plots for the above |

Scripts on the parallel launcher (2.01, 1.02) are all built on `src/inference/parallel.py`: the Makefile sets
`OUTPUT_PATTERN` (placeholders `{platform}`, `{n}`, `{stem}`), the launcher uses it to find pending files and the script
uses it to name its output. Not yet ported (still need an interactive server via `make start_servers`):
1.01 (id standardisation test), 1.03 (disagreement resolution) and 2.02 (LLM judge); 1.01 and 2.02 are also out of
date with the code they call.

Tests: `make test`.
