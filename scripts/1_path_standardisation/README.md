# 1_path_standardisation

Some paths look different but hold the same data (another language setting, a wrapper folder around the export, a
numbered part of a file). For every path, the model decides whether a path in the **catalogue** (the largest
donation of the platform, `<ROOT_DIR>/<DATA_DIR>/00_ingest/004_largest_donation/<platform>/*.csv`) points to the same
data, and returns that catalogue path, or `NA`.

The prompt is `path_std2026` in `src/inference/prompts.py`. It defines "the same data" (same field of the same kind of
file; different field, file or platform is not the same), lists the ways paths differ, has four worked examples and
puts the catalogue before the path, so vLLM can reuse the processed catalogue for every path of a platform
(Facebook and Instagram are about 30,000 tokens). A path that is itself in the catalogue is matched to itself without
asking the model.

```bash
make path_std-run SPLIT=smoke        # smoke sample: 5 paths per platform, one GPU job
make path_std-check SPLIT=smoke      # pytest on the output
make path_std-run SPLIT=test         # test and validation sample: one GPU job per platform
make path_std-run SPLIT=validation
make path_std                        # all merged structures, one GPU job per platform
```

Output, one JSON per input CSV, in `<ANNOTATION_ROOT>/inference/04_path_std/path_std2026/<split>/<platform>/`
(production: `<ROOT_DIR>/<DATA_DIR>/01_path_standardisation/011_classified_paths/<platform>/`):

```json
{"path": "...", "match": "<catalogue path or NA>", "rationale": "...", "method": "exact" | "llm"}
```

A "match" that is not copied exactly from the catalogue is rejected and asked again (three tries); paths that still
fail go to a `*_failed.json` next to the output. `path_std-check` runs `tests/test_path_std_output.py`: every record
has a match that is `NA` or in the catalogue, a rationale, no path failed, and every input path has one record.

The sample files are the same as for the taxonomy (`sample/<split>/<platform>/*.csv`, see `../2_taxonomy/README.md`).
Not built yet: a human check of the matches on the test and validation sample (an annotation sheet and an accuracy
script like 2.06).

| Script | What it does |
|---|---|
| `1.02_rnv_run_path_standardisation.py` | The model matches paths to the catalogue (GPU, parallel launcher) |
| `1.01.01`, `1.01.02` | Validation and plots of the earlier id-standardisation test run (older prompt) |
