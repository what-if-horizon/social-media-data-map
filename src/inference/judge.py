"""LLM judge for the taxonomy classification (scripts/2_classification/2.02_rnv_run_judge.py).

The judge is a different model from the one that classified. It sees the same taxonomy, the path and the
classifier's three predictions, and says whether the top prediction is correct.
"""

from src.inference.taxonomy import extract_json_dict

VERDICTS = ("correct", "plausible", "incorrect")

_HEAD = "# DDP topology"
_TAIL = "# Confidence scoring"

_TEMPLATE = """Reasoning: medium

# Role
You are an independent reviewer of a classification of Digital Data Package (DDP) paths. Another model
classified the path below into the DDP topology and gave three ranked labels. Decide whether its top label
is correct, using only the topology definitions and decision rules below.

{TAXONOMY}

# Verdicts
- "correct": the top label is the best fit.
- "plausible": the top label is defensible, but another label (possibly one of its alternatives) fits as well or better.
- "incorrect": the top label does not fit the definition.

# Output format
Return only valid JSON, with no text before or after it:
{"verdict": "correct" | "plausible" | "incorrect", "judge_label": "<the label you consider best; one of the 15 numbered labels>", "rationale": "<one or two sentences>"}

# Path
{PATH}

# Classifier output
{PREDICTIONS}
"""


def taxonomy_section(classifier_prompt: str) -> str:
    """The topology and decision rules, cut out of the classifier prompt so the two cannot drift apart."""
    start = classifier_prompt.index(_HEAD)
    end = classifier_prompt.index(_TAIL)
    return classifier_prompt[start:end].strip()


def build_judge_prompt(classifier_prompt: str, record: dict) -> str:
    preds = record.get("predictions")
    if preds:
        lines = [f'{i}. "{p.get("label")}" ({p.get("confidence")})' for i, p in enumerate(preds, 1)]
        shown = "\n".join(lines) + f'\nRationale: {record.get("rationale", "")}'
    else:
        shown = "The classifier produced no valid output. Classify the path yourself."
    # Plain replace: the template and the topology contain JSON braces, so str.format is not usable
    return (_TEMPLATE.replace("{TAXONOMY}", taxonomy_section(classifier_prompt))
                     .replace("{PATH}", str(record["path"]))
                     .replace("{PREDICTIONS}", shown))


def parse_verdict(raw, labels):
    """Return the judge's JSON object if it has a valid verdict and a label from the taxonomy, else None."""
    obj = extract_json_dict(raw)
    if (obj and obj.get("verdict") in VERDICTS and obj.get("judge_label") in labels
            and isinstance(obj.get("rationale"), str)):
        return obj
    return None
