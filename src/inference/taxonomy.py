"""Pure helpers for the LLM scripts (2.01 taxonomy classification, 1.02 path standardisation).

No heavy imports, so they are easy to unit test (tests/test_taxonomy.py).
"""

import json
import re


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


def extract_json_dict(raw):
    """First JSON object found in raw (after any </think>), or None. Also finds objects inside a JSON array."""
    if not isinstance(raw, str):
        return None
    raw = raw.split("</think>", 1)[-1]
    decoder = json.JSONDecoder()
    for m in re.finditer(r"\{", raw):
        try:
            obj, _ = decoder.raw_decode(raw[m.start():])
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return None
