# 2_taxonomy

Labels every data-donation path with the DDP taxonomy (the `kmetty2026` prompt in `src/inference/prompts.py`:
15 labels, three ranked predictions with confidences, and a rationale), and checks the result in three phases:
**smoke** (a handful of paths), **test** and **validation** (the human-annotated sample).

Run everything through the Makefile; `make help` lists the targets. Settings come from `.env` (copy `.env.example`).

## The three phases

```
smoke-select ──► taxonomy-eval SPLIT=smoke ──► inference-check ──► report        smoke:      5 paths per platform
                        │                          │ fails
taxonomy-sample         │                          └─► judge (other model)
      │                 ▼
      └──► taxonomy-eval SPLIT=test / validation ──► inference-check ──► eval-human ──► report
```

| Phase | Sample | Purpose |
|---|---|---|
| `smoke` | 5 mutually dissimilar paths per platform | Quick end-to-end check that the model, prompt and output format work |
| `test` | 20 paths per platform (`TEST_N`), to be annotated | Tune on this |
| `validation` | 80 paths per platform (`VALIDATION_N`), to be annotated | Final numbers |

All three are drawn from the merged structures and share no path.

### 1. Smoke sample

```bash
make smoke-select            # 2.00, CPU job
make sample-check            # pytest
```

All samples come from the merged structures, `<ROOT_DIR>/<DATA_DIR>/00_ingest/005_merged_structures` (that is,
`ddd_processed`). 2.00 draws up to `SMOKE_POOL` (2000) candidate paths per platform from there, minus any path
already in the test or validation set. It embeds them with the sentence-transformers model in `EMBEDDING_MODEL`,
then picks `SMOKE_K` (5) paths by farthest-point selection and fails if any pair has cosine similarity of
`SMOKE_MAX_SIM` (0.8) or more. Look at the printed paths once to see that they really are different.

Output, per platform, in `<ANNOTATION_ROOT>/sample/smoke/<platform>/`:
`<platform>_smoke_5.csv` (column `final_path`) and `smoke_similarity.json` (model, threshold, similarity matrix).

`sample-check` runs `tests/test_samples.py`: every sample path exists in the merged structures; smoke has 5 unique
paths with pairwise similarity below the threshold; smoke, test and validation share no path.

### 2. Test and validation sets

```bash
make taxonomy-sample         # 2.03, CPU job
```

Samples `TEST_N` (20) and `VALIDATION_N` (80) unique paths per platform at random (`SEED`) from the merged
structures, after removing the smoke paths, and asserts that the three sets are disjoint. Per platform and split it
writes `<ANNOTATION_ROOT>/sample/<split>/<platform>/<platform>_<split>.csv` and an annotation sheet
`<ANNOTATION_ROOT>/annotation/<split>/<platform>/<platform>_<split>_to_annotate.xlsx` (columns `final_path` and an
empty label column). The annotators fill in the sheet in place; 2.06 reads it. Existing files are not overwritten
unless you pass `--force` (`python scripts/2_taxonomy/2.03_rnv_sample_test_validation.py --force`), because
re-sampling would no longer match annotations already made.

### 3. Run the taxonomy

```bash
make taxonomy-eval SPLIT=smoke            # all five platforms, GPU jobs
make taxonomy-eval-youtube SPLIT=test     # one platform
make taxonomy                             # production: all merged structures, no SPLIT
```

2.01 starts through `launchers/parallel_llm.sh`: vLLM servers on the requested nodes, one worker process per server,
each labelling its share of the input CSVs. Output is one JSON per input CSV, named
`{platform}_{n}_class_ids_{DATA_TAX}_{COUNTRIES}_{model}.json`, in
`<ANNOTATION_ROOT>/inference/<INFERENCE_SUBDIR>/<SPLIT>/<platform>/` (production: `<ROOT_DIR>/<DATA_DIR>/<INFERENCE_SUBDIR>/021_classified_paths/<platform>/`).
A record looks like:

```json
{"path": "...", "predictions": [{"label": "...", "confidence": 85}, {"label": "...", "confidence": 10}, {"label": "...", "confidence": 5}], "rationale": "..."}
```

A path whose output is invalid after three attempts gets `"predictions": null`, an `"error"` and the `"raw_output"`.
Files that already exist in the output folder are skipped, so a job can be resubmitted after a crash.
Nodes and time per platform are in the Makefile (`taxonomy_NODES_*`, `taxonomy_TIME_*`, and the same for
`taxonomy_eval_`); override them with `make taxonomy-eval-x SPLIT=test NODES=2 TIME=00:30:00`.

### 4. Check the output, and the judge

```bash
make inference-check SPLIT=smoke
```

Runs `tests/test_inference_output.py` on the output and writes `results/02_taxonomy/reports/<SPLIT>_pytest.json`.
It checks that each record has three distinct labels from the taxonomy, confidences between 0 and 100 that sum to
100 in descending order, a non-empty rationale, and that every input path has exactly one record.

If any check fails, the target submits the **judge** (2.02) and exits non-zero. The judge is a different model
(`MODEL_CONFIG_JUDGE` in the Makefile, currently `qwen_2_5_7b_tp1x4.yaml`; the Makefile refuses to run it with
the same config as the taxonomy model). It sees the same taxonomy text, the path and the three predictions, and
answers:

- `correct`: the top label is the best fit
- `plausible`: defensible, but another label fits as well or better
- `incorrect`: the top label does not fit

plus the label it would choose and a rationale. Output goes to `<ANNOTATION_ROOT>/inference/03_judge/<SPLIT>/<platform>/`.
You can also run it on its own with `make judge SPLIT=...`.

### 5. Human annotations and the report

```bash
make eval-human SPLIT=test   # 2.06, once the annotations are in
make report SPLIT=smoke      # 2.07
```

2.06 compares the top-1 and top-3 labels with the human labels in
`<ANNOTATION_ROOT>/annotation/<SPLIT>/<platform>/*.xlsx` (columns `final_path` and the label column, `LABEL_COL`,
default `label`; matching ignores case and whitespace). It writes `results/02_taxonomy/reports/<SPLIT>_human_eval.json`
and skips platforms that have no annotations yet.

2.07 writes `results/02_taxonomy/reports/<SPLIT>_report.html`, a single file that opens in any browser:
the pytest result, a summary of the output (top-1 labels, confidence), the judge verdicts per platform with the
paths it did not mark correct, and, if the human evaluation exists, accuracy per platform, recall per label and a
confusion matrix. Parts that have not been run yet are marked as such, so the report can be built at any stage.

## Scripts

| Script | Target | What it does |
|---|---|---|
| `2.00_rnv_select_smoke_sample.py` | `smoke-select` | Smoke sample (CPU) |
| `2.01_rnv_run_taxonomy.py` | `taxonomy`, `taxonomy-<platform>`, `taxonomy-eval`, `taxonomy-eval-<platform>` | Taxonomy labelling (GPU, parallel launcher) |
| `2.02_rnv_run_judge.py` | `judge`, `judge-<platform>` | LLM judge (GPU, parallel launcher) |
| `2.03_rnv_sample_test_validation.py` | `taxonomy-sample` | Test and validation sets + annotation sheets, from the merged structures (CPU) |
| `2.04_rnv_test_validate_taxonomy.py` | `taxonomy-accuracy` | Accuracy against annotations for the older **verduyn2020** scheme (CPU) |
| `2.05_rnv_visualisation_results_taxonomy.py` | `taxonomy-viz` | Plots for 2.04 (CPU) |
| `2.06_rnv_evaluate_human_annotations.py` | `eval-human` | Accuracy against human labels, kmetty2026 (CPU) |
| `2.07_rnv_build_report.py` | `report` | HTML report per phase (CPU) |

2.04 and 2.05 belong to the earlier Verduyn active/passive scheme and are not part of the flow above.

## Tests

`make test` runs all unit tests. The data checks skip unless they are given a folder; the Makefile targets
`sample-check` and `inference-check` pass the right ones. To run them by hand:

```bash
pytest tests/test_inference_output.py --inference-dir <dir> [--input-dir <dir>] [--results-json out.json]
pytest tests/test_samples.py --sample-root <ANNOTATION_ROOT>/sample --merged-dir <merged structures>
```

Shared code is in `src/inference/`: `taxonomy.py` (prompt filling, label list, output parsing and validation),
`parallel.py` (worker plumbing and output naming), `similarity.py`, `judge.py`, `evaluation.py`, `report.py`.

## Settings

All scripts read their settings from `src/config.py`, which loads `.env` from the repository root. Order of precedence: environment variables (including what `make` exports, so a Makefile value or `make ... VAR=x` wins) over `.env` over the defaults in `config.py`. The scripts therefore also work when started directly, for example `python scripts/2_taxonomy/2.07_rnv_build_report.py --split smoke`, as long as `.env` is filled in. A missing required setting stops the script with a message naming it.

| Variable | Where | Meaning |
|---|---|---|
| `ROOT_DIR`, `DATA_DIR`, `MODEL_DIR` | `.env` | Data root, processed-data folder, models |
| `EMBEDDING_MODEL` | `.env` | Sentence-transformers model for 2.00 |
| `LABEL_COL` | `.env` or environment | Human label column in the annotation files (2.06) |
| `ANNOTATION_ROOT` | Makefile (`$(ROOT_DIR)/ddd_annotation`) | Annotation sample, annotations and inference outputs |
| `SMOKE_K`, `SMOKE_MAX_SIM`, `SMOKE_POOL`, `TEST_N`, `VALIDATION_N`, `SEED` | `.env` | Smoke sample size, similarity limit, candidate pool, test and validation sizes, random seed |
| `MODEL_CONFIG`, `MODEL_CONFIG_JUDGE` | Makefile | Config in `configs/` for the taxonomy model and the judge |
| `DATA_TAX`, `COUNTRIES` | Makefile | Prompt to use (`kmetty2026`) and the tag used in output file names |
| `INFERENCE_SUBDIR` | Makefile | Existing storage folder for outputs (`02_path_classification`) |

To use another prompt, add it to `PROMPTS` in 2.01 and 2.02, and set `DATA_TAX`.
