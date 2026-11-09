"""Pure helpers for the taxonomy classification (scripts/2.01_rnv_run_data_classification.py).

No heavy imports, so they are easy to unit test (tests/test_taxonomy.py).
"""

import json
import os
import re


def output_name(platform, filename, data_tax, countries, model_config):
    """{platform}_{n}_class_ids_{tax}_{countries}_{model}.json

    Must match output_name() in launchers/parallel_llm.sh, which uses the same
    name to decide which files are already done.
    """
    n = os.path.splitext(filename)[0].split("_")[-1]
    model = re.sub(r"\.yaml$", "", model_config)
    return f"{platform}_{n}_class_ids_{data_tax}_{countries}_{model}.json"


def build_prompt(template, path):
    # str.format would choke on the JSON braces in the prompt, so plain replace
    return template.replace("{PATH}", path)


def valid_labels(template):
    """The numbered labels in the prompt, e.g. 1. "Login data"."""
    return set(re.findall(r'^\s*\d+\.\s+"(.+?)"\s*$', template, flags=re.MULTILINE))


def parse_prediction(raw, labels):
    """Return the parsed dict if raw holds {"predictions": [{"label": <valid label>, ...}, ...]}, else None."""
    if not isinstance(raw, str):
        return None
    raw = raw.split("</think>", 1)[-1]   # drop reasoning block if present
    decoder = json.JSONDecoder()
    # LLMs often add text around the JSON object; try every '{' as a start
    for m in re.finditer(r"\{", raw):
        try:
            obj, _ = decoder.raw_decode(raw[m.start():])
        except Exception:
            continue
        preds = obj.get("predictions") if isinstance(obj, dict) else None
        if (isinstance(preds, list) and preds
                and all(isinstance(x, dict) and x.get("label") in labels for x in preds)):
            return obj
    return None
