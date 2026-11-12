"""The shortlist path standardisation (src/inference/pathshortlist.py) with a fake model and a fake embedder."""
import json
import re

import numpy as np
import pytest

from src.inference import prompts
from src.inference.pathmatch import NA
from src.inference.pathshortlist import Catalogue, ShortlistMatcher, build_choice_prompt, parse_choice
from src.inference.retrieval import embed_text, top_k
from src.ingest.cleanPaths import clean_path

Y = "Takeout/YouTube y YouTube Music"
CATALOGUE = [
    f"{Y}/historial/historial-de-reproducciones.json/title",
    f"{Y}/historial/historial-de-reproducciones.json/header",
    f"{Y}/historial/historial-de-búsquedas.json/title",
    f"{Y}/historial/historial-de-búsquedas.json/header",
    f"{Y}/suscripciones/suscripciones.json/snippet/title",
]


def fake_embedder(texts):
    """Character trigram counts: texts that share letters are close. Deterministic, no model."""
    out = np.zeros((len(texts), 128))
    for i, t in enumerate(texts):
        t = t.lower()
        for j in range(len(t) - 2):
            out[i, hash(t[j:j + 3]) % 128] += 1
    norm = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.where(norm == 0, 1, norm)


class FakeModel:
    """Answers the prompts of the matcher: `pick` gets (kind, query, candidates) and returns a candidate number."""

    def __init__(self, pick):
        self.pick, self.calls = pick, []

    def __call__(self, prompt):
        kind = "file" if "# File to match" in prompt else "field"
        block = prompt.split("# Candidates")[1].split("\n# ")[0]
        candidates = re.findall(r"^\d+\. (.*)$", block, flags=re.MULTILINE)
        query = prompt.split("# File to match\n" if kind == "file" else "# Field to match\n")[-1].strip()
        self.calls.append((kind, query, candidates))
        answer = self.pick(kind, query, candidates)
        if isinstance(answer, str):
            return answer
        return json.dumps({"choice": answer, "rationale": "fake model"})


def matcher(model, k=15, retries=3, catalogue=None):
    cat = Catalogue(catalogue or CATALOGUE, [clean_path(p) for p in (catalogue or CATALOGUE)])
    return ShortlistMatcher(cat, fake_embedder, model, prompts.path_file2026(), prompts.path_field2026(),
                            k=k, workers=4, retries=retries)


def pick_containing(word):
    def pick(kind, query, candidates):
        return next((i for i, c in enumerate(candidates, 1) if word in c), 0)
    return pick


def test_exact_and_clean_matches_need_no_model():
    model = FakeModel(lambda *a: 0)
    wrapped = "takeout-20251118T144647Z-3-001/" + CATALOGUE[0]
    records, failed = matcher(model).match([CATALOGUE[1], wrapped])
    assert [(r["method"], r["match"]) for r in records] == [("exact", CATALOGUE[1]), ("clean", CATALOGUE[0])]
    assert model.calls == [] and failed == []


def test_other_language_file_is_matched_by_the_model_and_the_field_by_name():
    path = "Takeout/YouTube en YouTube Music/geschiedenis/zoekgeschiedenis.json/header"
    model = FakeModel(pick_containing("búsquedas"))
    (rec,), failed = matcher(model).match([path])
    assert rec["match"] == CATALOGUE[3] and rec["method"] == "llm" and failed == []
    assert [c[0] for c in model.calls] == ["file"]                    # the field has the same name: no second call
    assert "historial-de-búsquedas.json" in rec["file_match"]


def test_field_with_another_name_is_asked_and_can_be_na():
    path = "Takeout/YouTube en YouTube Music/geschiedenis/zoekgeschiedenis.json/titel"

    def pick(kind, query, candidates):
        if kind == "file":
            return pick_containing("búsquedas")(kind, query, candidates)
        return next((i for i, c in enumerate(candidates, 1) if c == "title"), 0)

    (rec,), _ = matcher(FakeModel(pick)).match([path])
    assert rec["match"] == CATALOGUE[2]
    (rec,), _ = matcher(FakeModel(lambda kind, q, c: pick_containing("búsquedas")(kind, q, c) if kind == "file" else 0)).match([path])
    assert rec["match"] == NA and rec["method"] == "llm"


def test_file_without_a_match_makes_all_its_paths_na_with_one_model_call():
    paths = [f"Takeout/YouTube y YouTube Music/otro/otro.json/campo{i}" for i in range(5)]
    model = FakeModel(lambda *a: 0)
    records, failed = matcher(model).match(paths)
    assert [r["match"] for r in records] == [NA] * 5 and {r["method"] for r in records} == {"file_na"}
    assert [c[0] for c in model.calls] == ["file"]                    # one decision for the whole file


def test_invalid_answers_are_retried_then_reported_as_failed():
    path = "Takeout/YouTube en YouTube Music/geschiedenis/zoekgeschiedenis.json/header"
    for bad in ("no json", json.dumps({"choice": 99, "rationale": "x"}), json.dumps({"choice": 1}),
                json.dumps({"choice": True, "rationale": "x"})):
        model = FakeModel(lambda *a, bad=bad: bad)
        records, failed = matcher(model, retries=3).match([path])
        assert records == [] and [f["path"] for f in failed] == [path]
        assert len(model.calls) == 3


def test_the_model_only_sees_a_shortlist_and_never_a_path_outside_the_catalogue():
    big = [f"{Y}/historial/f{i}.json/title" for i in range(60)] + CATALOGUE
    model = FakeModel(lambda kind, q, cands: 1)
    records, _ = matcher(model, k=5, catalogue=big).match(["otra/ruta/zoek.json/x", "otra/ruta/zoek2.json/title"])
    assert all(len(c) <= 5 for _, _, c in model.calls)
    assert all(r["match"] == NA or r["match"] in big for r in records)


def test_field_shortlist_is_limited_to_k_fields_of_the_matched_file():
    fields = [f"{Y}/historial/grande.json/campo_{i:02d}" for i in range(40)] + [f"{Y}/historial/grande.json/title"]
    path = "Takeout/YouTube en YouTube Music/geschiedenis/groot.json/titel"

    def pick(kind, query, candidates):
        return 1

    model = FakeModel(pick)
    (rec,), _ = matcher(model, k=6, catalogue=fields).match([path])
    field_calls = [c for c in model.calls if c[0] == "field"]
    assert field_calls and all(len(c[2]) <= 6 for c in field_calls)
    assert rec["match"] in fields


def test_order_of_the_input_is_kept():
    paths = [CATALOGUE[4], "x/y/z.json/a", CATALOGUE[0], "takeout-20251118T144647Z-3-001/" + CATALOGUE[2]]
    records, _ = matcher(FakeModel(lambda *a: 0)).match(paths)
    assert [r["path"] for r in records] == paths


def test_prompts_and_parsing():
    out = build_choice_prompt(prompts.path_file2026(), ["a.json", "b.json"], "q.json  [fields: x]")
    assert "1. a.json\n2. b.json" in out and out.rstrip().endswith("q.json  [fields: x]")
    assert "{CANDIDATES}" not in out and "{QUERY}" not in out
    for template in (prompts.path_file2026(), prompts.path_field2026()):
        for line in re.findall(r"^Output: (\{.*\})$", template, flags=re.MULTILINE):
            assert parse_choice(line, 9) is not None                # the examples are valid answers
    assert parse_choice('{"choice": 0, "rationale": "none"}', 3)["choice"] == 0
    assert parse_choice('{"choice": 4, "rationale": "x"}', 3) is None
    assert parse_choice('{"choice": "2", "rationale": "x"}', 3) is None


def test_top_k_and_embed_text():
    emb = np.eye(4)
    assert top_k(np.array([[0.0, 1, 0, 0]]), emb, 2)[0][0] == 1
    assert top_k(np.zeros((1, 4)), np.zeros((0, 1)), 3) == [[]]
    assert embed_text(f"{Y}/historial/historial-de-búsquedas.json") == "historial / historial de búsquedas"
    assert embed_text("a/b/c/d", last=3) == "b / c / d"
