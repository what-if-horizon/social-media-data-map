"""Pure helpers for the LLM scripts (2.01 taxonomy, 1.02 path standardisation).

No heavy imports, so they are easy to unit test (tests/test_taxonomy.py).
"""

import json
import re


def label_list(template):
    """The numbered labels of the prompt in their order, e.g. ['Login data', 'Connection / device telemetry', ...]."""
    return re.findall(r'^\s*\d+\.\s+"(.+?)"\s*$', template, flags=re.MULTILINE)


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


def validate_record(rec, labels, n=None):
    """Problems with one taxonomy record from scripts/2_taxonomy/2.01; empty list = valid.

    Valid means: exactly n predictions (default config.N_PREDICTIONS: 3, or 5 for kmetty2026_simple), distinct labels from the taxonomy, confidences between
    0 and 100 that sum to 100 in descending order, and a non-empty rationale.
    """
    if n is None:
        from src import config
        n = config.N_PREDICTIONS
    if not isinstance(rec, dict):
        return ["record is not an object"]
    preds = rec.get("predictions")
    if preds is None:
        return [f"no valid prediction ({rec.get('error', 'predictions missing')})"]
    if not isinstance(preds, list) or len(preds) != n:
        return [f"expected {n} predictions, got {len(preds) if isinstance(preds, list) else type(preds).__name__}"]

    problems = []
    names = [x.get("label") if isinstance(x, dict) else None for x in preds]
    scores = [x.get("confidence") if isinstance(x, dict) else None for x in preds]
    for name in names:
        if name not in labels:
            problems.append(f"unknown label {name!r}")
    if len(set(names)) != n:
        problems.append("labels are not distinct")
    if not all(isinstance(c, (int, float)) and not isinstance(c, bool) and 0 <= c <= 100 for c in scores):
        problems.append(f"confidences must be numbers in [0, 100], got {scores}")
    else:
        if abs(sum(scores) - 100) > 1e-6:
            problems.append(f"confidences sum to {sum(scores)}, expected 100")
        if scores != sorted(scores, reverse=True):
            problems.append(f"confidences not in descending order: {scores}")
    rationale = rec.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        problems.append("rationale missing or empty")
    return problems
