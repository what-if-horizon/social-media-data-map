"""Paths explained and left after each cleaning step (src/ingest/cleanSteps.py)."""
from src.ingest.cleanSteps import build_page, explain

CATALOGUE = ["your_activity/likes.json/title", "Takeout/Hist/posts.json/Title", "a/b.json/x"]
PATHS = [
    "your_activity/likes.json/title",              # exact
    "ig/your_activity/likes.json/title",           # wrapper (also in the catalogue as it is: the first step finds it once)
    "Takeout/Hist/posts_2.json/Title",             # part number
    "takeout/hist/posts.json/title",               # case
    "other/file.json/z",                           # left
]


def test_each_path_is_counted_at_the_first_step_that_finds_it():
    r = explain(PATHS, CATALOGUE)
    assert r["total"] == 5
    assert [s["explained"] for s in r["steps"]] == [1, 1, 1, 1]
    assert [s["left"] for s in r["steps"]] == [4, 3, 2, 1]
    assert r["left_paths"] == ["other/file.json/z"]


def test_examples_show_the_catalogue_path():
    r = explain(PATHS, CATALOGUE)
    assert r["steps"][2]["examples"] == [("Takeout/Hist/posts_2.json/Title", "Takeout/Hist/posts.json/Title")]
    assert r["steps"][0]["examples"] == []


def test_page():
    assert "Path cleaning steps" in build_page({"x": explain(PATHS, CATALOGUE)})
