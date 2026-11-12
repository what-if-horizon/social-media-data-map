"""Helpers for the path standardisation (scripts/1_path_standardisation/1.02): is there a catalogue path with the same data?

Pure functions, so they can be tested without a model. The prompt is src/inference/prompts.py::path_std2026.
"""

from src.inference.taxonomy import extract_json_dict

NA = "NA"


def catalogue_text(paths):
    """The catalogue as it goes into the prompt: one path per line."""
    return "\n".join(paths)


def build_path_prompt(template, catalogue, path):
    """Fill {CATALOGUE} and {PATH}. Plain replace: the prompt contains JSON braces, so str.format is not usable.
    {PATH} must be last in the template, so that everything before it is the same for every path of a platform."""
    return template.replace("{CATALOGUE}", catalogue).replace("{PATH}", path)


def parse_match(raw, catalogue_set):
    """The model's JSON object if "match" is "NA" or a path from the catalogue and the rationale is filled, else None."""
    obj = extract_json_dict(raw)
    if (obj and isinstance(obj.get("match"), str) and (obj["match"] == NA or obj["match"] in catalogue_set)
            and isinstance(obj.get("rationale"), str) and obj["rationale"].strip()):
        return obj
    return None


def validate_match_record(rec, catalogue_set):
    """Problems with one output record of 1.02; empty list = valid."""
    if not isinstance(rec, dict):
        return ["record is not an object"]
    match = rec.get("match")
    if match is None:
        return [f"no valid match ({rec.get('error', 'match missing')})"]
    problems = []
    if match != NA and match not in catalogue_set:
        problems.append(f"match is not in the catalogue: {str(match)[:80]!r}")
    if not isinstance(rec.get("rationale"), str) or not rec["rationale"].strip():
        problems.append("rationale missing or empty")
    if rec.get("method") == "exact" and match != rec.get("path"):
        problems.append("exact match must be the path itself")
    if rec.get("method") == "file_na" and match != NA:
        problems.append("a path of a file without a match must be NA")
    if rec.get("method") not in (None, "exact", "clean", "llm", "file_na"):
        problems.append(f"unknown method {rec.get('method')!r}")
    return problems
