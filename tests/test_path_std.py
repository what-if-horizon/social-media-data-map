"""Prompt, parsing and validation of the path standardisation (no model needed)."""
from src.inference import prompts
from src.inference.pathmatch import (NA, build_path_prompt, catalogue_text, parse_match, validate_match_record)

CAT = ["a/posts_1.json/timestamp", "a/profile.json/name"]
CATSET = set(CAT)


def test_prompt_fills_catalogue_and_path_and_path_is_last():
    out = build_path_prompt(prompts.path_std2026(), catalogue_text(CAT), "x/posts_2.json/timestamp")
    assert "{CATALOGUE}" not in out and "{PATH}" not in out
    assert "a/posts_1.json/timestamp\na/profile.json/name" in out
    assert out.rstrip().endswith("x/posts_2.json/timestamp")
    # prefix caching: everything before the path is identical for two different paths
    other = build_path_prompt(prompts.path_std2026(), catalogue_text(CAT), "y/z.json/q")
    cut = out.rindex("x/posts_2.json/timestamp")
    assert out[:cut] == other[:other.rindex("y/z.json/q")]


def test_parse_match():
    ok = '{"path": "p", "match": "a/profile.json/name", "rationale": "same field"}'
    assert parse_match("</think> " + ok, CATSET)["match"] == "a/profile.json/name"
    assert parse_match(ok.replace("a/profile.json/name", "NA"), CATSET)["match"] == NA
    assert parse_match(ok.replace("a/profile.json/name", "a/invented.json/x"), CATSET) is None   # not in the catalogue
    assert parse_match(ok.replace("same field", " "), CATSET) is None                              # no rationale
    assert parse_match("no json", CATSET) is None


def test_validate_match_record():
    assert validate_match_record({"path": "p", "match": "a/profile.json/name", "rationale": "r"}, CATSET) == []
    assert validate_match_record({"path": "p", "match": NA, "rationale": "r"}, CATSET) == []
    assert validate_match_record({"path": "p", "match": "a/other", "rationale": "r"}, CATSET)
    assert validate_match_record({"path": "p", "match": NA, "rationale": ""}, CATSET)
    assert validate_match_record({"path": "p", "match": None, "error": "invalid output"}, CATSET)
    assert validate_match_record({"path": "p", "match": CAT[0], "rationale": "r", "method": "exact"}, CATSET)  # not itself
    assert validate_match_record({"path": CAT[0], "match": CAT[0], "rationale": "r", "method": "exact"}, CATSET) == []


def test_examples_in_the_prompt_are_valid_json_answers():
    """The examples of the prompt must themselves be in the output format."""
    import json
    import re
    for line in re.findall(r"^Output: (\{.*\})$", prompts.path_std2026(), flags=re.MULTILINE):
        obj = json.loads(line)
        assert set(obj) == {"path", "match", "rationale"} and obj["rationale"]
