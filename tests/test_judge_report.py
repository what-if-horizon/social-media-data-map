"""Judge prompt/parsing, human evaluation and the report builder (no model needed)."""
from src.inference import prompts
from src.inference.evaluation import canonical_label, evaluate
from src.inference.judge import build_judge_prompt, parse_verdict, taxonomy_section
from src.inference.report import build_report
from src.inference.taxonomy import valid_labels, validate_record

PROMPT = prompts.kmetty2026()
LABELS = valid_labels(PROMPT)


def rec(path="a/b.json", labels=("Login data", "Connection / device telemetry", "Network (ego ties)"),
        scores=(70, 20, 10), rationale="because"):
    return {"path": path, "rationale": rationale,
            "predictions": [{"label": l, "confidence": c} for l, c in zip(labels, scores)]}


def test_validate_record():
    assert validate_record(rec(), LABELS) == []
    assert validate_record(rec(scores=(50, 30, 30)), LABELS)               # sums to 110
    assert validate_record(rec(scores=(10, 20, 70)), LABELS)               # not descending
    assert validate_record(rec(labels=("Login data", "Login data", "Network (ego ties)")), LABELS)
    assert validate_record(rec(labels=("Nope", "Login data", "Network (ego ties)")), LABELS)
    assert validate_record(rec(rationale=""), LABELS)
    assert validate_record({"path": "x", "predictions": None, "error": "invalid output"}, LABELS)


def test_judge_prompt_uses_the_same_taxonomy():
    section = taxonomy_section(PROMPT)
    assert '"Login data"' in section and "# Confidence scoring" not in section
    out = build_judge_prompt(PROMPT, rec(path="x/y.json"))
    assert section in out and "x/y.json" in out and "{PATH}" not in out and "{PREDICTIONS}" not in out
    assert "no valid output" in build_judge_prompt(PROMPT, {"path": "z", "predictions": None})


def test_parse_verdict():
    ok = '{"verdict": "plausible", "judge_label": "Login data", "rationale": "r"}'
    assert parse_verdict("</think> " + ok, LABELS)["verdict"] == "plausible"
    assert parse_verdict(ok.replace("plausible", "maybe"), LABELS) is None
    assert parse_verdict(ok.replace("Login data", "Nope"), LABELS) is None


def test_evaluate_against_human_labels():
    records = [rec("a"), rec("b", labels=("Network (ego ties)", "Login data", "Location and GPS traces")),
               {"path": "c", "predictions": None}]
    gold = {"a": " login DATA ", "b": "Login data", "c": "Login data", "d": "not a label"}
    s = evaluate(records, gold, LABELS)
    assert s["n"] == 3 and s["top1_accuracy"] == 1 / 3 and s["top3_accuracy"] == 2 / 3
    assert s["n_without_prediction"] == 1 and len(s["unknown_gold_labels"]) == 0   # "d" has no record
    assert canonical_label("nope", LABELS) is None


def test_report_builds_with_and_without_parts():
    empty = build_report("smoke", None, {}, {}, None)
    assert "No pytest result" in empty and "has not run" in empty and "No human evaluation" in empty
    inference = {"facebook": [rec("a"), {"path": "b", "predictions": None}]}
    pytest_result = {"tests": [{"nodeid": "t::x", "outcome": "failed", "message": "<bad>"},
                               {"nodeid": "t::y", "outcome": "passed"}]}
    judge = {"facebook": [{"path": "a", "verdict": "correct", "model_top1": "Login data"},
                          {"path": "b", "verdict": None, "model_top1": None, "error": "invalid output"}]}
    human = {"platforms": {"facebook": evaluate(inference["facebook"], {"a": "Login data"}, LABELS)},
             "pooled": evaluate(inference["facebook"], {"a": "Login data"}, LABELS)}
    page = build_report("test", pytest_result, inference, judge, human, {"taxonomy model": "m"})
    assert "&lt;bad&gt;" in page and "<bad>" not in page          # escaped
    assert "Confusion matrix" in page and "no valid verdict" in page
