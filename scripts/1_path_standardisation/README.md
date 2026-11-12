# 1_path_standardisation

Some paths look different but hold the same data (another language setting, a wrapper folder around the export, a
numbered part of a file, a renamed folder). For every path, the model decides whether a path in the **catalogue** (the
largest donation of the platform, `<ROOT_DIR>/<DATA_DIR>/00_ingest/004_largest_donation/<platform>/*.csv`) holds the
same data, and returns that catalogue path, or `NA`.

## Steps

```bash
make clean_paths                     # once, ingest step 0.06: add clean_path to the merged structures and the catalogue
make path_std-run SPLIT=smoke        # smoke sample: 5 paths per platform, one GPU job
make path_std-check SPLIT=smoke      # pytest on the output
make path_std-run SPLIT=test         # test and validation sample: one GPU job per platform
make path_std-run SPLIT=validation
make path_std                        # all merged structures, one GPU job per platform
```

### 1. Cleaning (ingest, `scripts/0_ingest/0.06_rnv_clean_paths.py`)

Removes exactly two things from a path and stores the result in a new column `clean_path`, next to the unchanged
`final_path` (rules and their tests: `src/ingest/cleanPaths.py`, `tests/test_clean_paths.py`):

- wrapper folders around an export: `ig/`, `instagram_takeout_dutch/`, `meta-2025-Dec-05-…/instagram-<name>-…/`,
  `takeout-20251118T144647Z-3-001/`
- the part number of a split file: `posts_1.json`, `posts_2.json` become `posts.json`

It does not translate anything and does not change case, so it cannot merge two different fields. It writes new folders
(`006_cleaned_structures`, `006_cleaned_largest_donation`) and leaves `005_merged_structures` and the samples as they are.
On the current data, 1,061 of the 4,455 Instagram paths that are not in the catalogue are found after cleaning (24%),
36 of 1,669 for Facebook, 19 of 234 for TikTok, none for YouTube and X (their differences are language).

### 2. Matching (`1.02`, method `path_shortlist2026`, the default)

1. **exact**: the path is in the catalogue.
2. **clean**: the clean path is the same as a clean catalogue path (case, spaces, `_` and `-` do not matter).
3. **file**: the remaining paths are grouped by file. For each file the model gets a numbered shortlist of the
   `SHORTLIST_K` (15) catalogue files with the most similar names (multilingual embeddings,
   `paraphrase-multilingual-MiniLM-L12-v2`, on the CPU), each with some of its field names, and answers with a number or
   0 for none (prompt `path_file2026`). If none, every path of the file is `NA` (`file_na`).
4. **field**: in a matched file, a field with the same name is matched directly; otherwise the model chooses among the
   fields of the catalogue file (a shortlist of at most `SHORTLIST_K` if the file has more; prompt `path_field2026`).

The model answers with a number, so it can never return a path that is not in the catalogue. The prompts are a few
hundred tokens, against about 30,000 for the whole Facebook or Instagram catalogue in `path_std2026`.

The earlier method, with the whole catalogue in the prompt, stays available to compare: `make path_std-run SPLIT=smoke
PATH_STD=path_std2026`. The outputs of the two go to different folders.

## Output

One JSON per input CSV in `<ANNOTATION_ROOT>/inference/04_path_std/<PATH_STD>/<split>/<platform>/`
(production: `<ROOT_DIR>/<DATA_DIR>/01_path_standardisation/011_classified_paths/<platform>/`):

```json
{"path": "...", "match": "<catalogue path or NA>", "rationale": "...", "method": "exact|clean|llm|file_na", "file_match": "<catalogue file or NA>"}
```

Paths without a valid answer after three tries go to a `*_failed.json` next to the output. `path_std-check` runs
`tests/test_path_std_output.py`: every record has a match that is `NA` or in the catalogue, a rationale, no path failed,
and every input path has one record.

## Settings

`PATH_STD` (method, Makefile), `SHORTLIST_K`, `PATH_EMBEDDING_MODEL` (a multilingual sentence-transformers model on disk,
default `$MODEL_DIR/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; compute nodes have no internet) in
`.env`. Resources per platform: `path_std_run_NODES_*` and `path_std_run_TIME_*` in the Makefile.

## Not built yet

- A human check of the matches on the test and validation sample (an annotation sheet, and an accuracy script like
  `2_taxonomy/2.06`). Until then the checks only show that the output is well formed, not that the matches are right.
- A measure of how often the right catalogue file is in the shortlist. The model cannot pick what is not offered, so this
  caps the accuracy; it needs the human-checked matches.
- Files that sit in the wrong platform folder (Instagram data holds Facebook and TikTok files, Facebook data holds
  YouTube files). They come out as `NA` against the catalogue of the folder they are in.

| Script | What it does |
|---|---|
| `../0_ingest/0.06_rnv_clean_paths.py` | Cleaning of the paths (ingest, CPU) |
| `1.02_rnv_run_path_standardisation.py` | The model matches paths to the catalogue (GPU, parallel launcher) |
| `1.01.01`, `1.01.02` | Validation and plots of the earlier id-standardisation test run (older prompt) |
