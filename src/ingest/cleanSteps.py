"""How many paths each cleaning step explains (scripts/0_ingest/0.07_rnv_visualise_clean_steps.py).

A path is explained when the catalogue (the largest donation) has the same path. The steps make "the same" wider, one
after the other, and are applied to the paths and to the catalogue alike (see src/ingest/cleanPaths.py):

0. exact:               the path as it is in the data
1. wrapper folders:     `ig/`, `instagram_takeout_dutch/`, `takeout-<date>/`, `meta-<date>/instagram-<name>/` removed
2. part numbers:        `posts_1.json` and `posts_2.json` count as `posts.json`
3. case and separators: lower case, and spaces, `_` and `-` count as one

What is left after step 3 goes to the model (1.02). Pure functions, so they can be tested without data.
"""

from src.ingest.cleanPaths import clean_path, match_key, strip_wrappers

STEPS = (
    ("exact", "Exact", lambda p: p),
    ("wrappers", "Wrapper folders removed", lambda p: strip_wrappers(p)),
    ("parts", "Part numbers dropped", lambda p: clean_path(p)),
    ("case", "Case and separators ignored", lambda p: match_key(clean_path(p))),
)
EXAMPLES = 3   # paths shown per step


def explain(paths, catalogue):
    """For one platform: the number of paths explained by each step, those left after each step, and examples.
    -> {"total", "steps": [{"key", "name", "explained", "left", "examples": [(path, catalogue path)]}], "left_paths"}.
    Every step is wider than the one before it, so a path is counted at the first step that finds it."""
    paths = list(dict.fromkeys(p for p in paths if isinstance(p, str)))
    catalogue = [c for c in dict.fromkeys(catalogue) if isinstance(c, str)]
    todo, steps = paths, []
    for key, name, transform in STEPS:
        index = {}
        for c in catalogue:
            index.setdefault(transform(c), c)
        found = [(p, index[transform(p)]) for p in todo if transform(p) in index]
        done = {p for p, _ in found}
        todo = [p for p in todo if p not in done]
        # examples: paths that differ from their catalogue path (the exact step has nothing to show)
        shown = [(p, c) for p, c in found if p != c][:EXAMPLES]
        steps.append({"key": key, "name": name, "explained": len(found), "left": len(todo), "examples": shown})
    return {"total": len(paths), "steps": steps, "left_paths": todo}


# ---------------------------------------------------------------------------------------------------------------
# HTML (plain HTML/CSS, same look as the taxonomy report)
# ---------------------------------------------------------------------------------------------------------------

from src.inference.report import CSS, bars, card, esc, pct   # noqa: E402

COLORS = ("var(--s1)", "#2fa37a", "var(--s4)", "#7a5bd0", "var(--s2)")   # the steps, then what is left


def _stack(result):
    total = result["total"] or 1
    parts = [(s["name"], s["explained"]) for s in result["steps"]] + [("Left for the model", result["steps"][-1]["left"])]
    cells = "".join(f'<i style="width:{100 * n / total:.2f}%;background:{c}" title="{esc(name)}: {n}"></i>'
                    for (name, n), c in zip(parts, COLORS) if n)
    return f'<div class="stack">{cells}</div>'


def legend():
    names = [s[1] for s in STEPS] + ["Left for the model"]
    return '<div class="legend">' + "".join(f'<span><i style="background:{c}"></i>{esc(n)}</span>'
                                              for n, c in zip(names, COLORS)) + "</div>"


def platform_section(name, result):
    total = result["total"]
    rows = "".join(f'<tr><td>{esc(s["name"])}</td><td class="num">{s["explained"]}</td><td class="num">{s["left"]}</td>'
                   f'<td class="num">{pct(s["left"] / total) if total else "n/a"}</td></tr>' for s in result["steps"])
    funnel = bars([("Paths", total)] + [(f'after: {s["name"].lower()}', s["left"]) for s in result["steps"]], total)
    examples = "".join(
        f'<tr><td>{esc(s["name"])}</td><td><pre>{esc(p)}</pre></td><td><pre>{esc(c)}</pre></td></tr>'
        for s in result["steps"] for p, c in s["examples"])
    ex = (f'<table><tr><th>Found by</th><th>Path</th><th>Catalogue path</th></tr>{examples}</table>' if examples else "")
    return (f'<h3>{esc(name)}: {total} paths</h3>{_stack(result)}'
            f'<table><tr><th>Step</th><th>Explained</th><th>Left unexplained</th><th>Left, % of paths</th></tr>{rows}</table>'
            f'<h3 style="margin-top:8px">Paths not in the catalogue, after each step</h3>{funnel}{ex}')


def build_page(per_platform):
    """per_platform: {platform: explain(...)}; the first section is the sum over the platforms."""
    total = {"total": sum(r["total"] for r in per_platform.values()),
             "steps": [{"key": k, "name": n, "explained": sum(r["steps"][i]["explained"] for r in per_platform.values()),
                        "left": sum(r["steps"][i]["left"] for r in per_platform.values()), "examples": []}
                       for i, (k, n, _) in enumerate(STEPS)]}
    first_left = total["total"] - total["steps"][0]["explained"]
    cards = "".join([card(total["total"], "paths"), card(first_left, "not in the catalogue as they are"),
                     card(total["steps"][-1]["left"], "still unexplained after cleaning")])
    body = (f'<main><h1>Path cleaning steps</h1><p class="meta">Paths of the merged structures against the catalogue '
            f'(largest donation); every step is applied to both.</p><div class="cards">{cards}</div>{legend()}'
            f'<h2>All platforms</h2>{platform_section("All", total)}<h2>Per platform</h2>'
            + "".join(platform_section(p, r) for p, r in per_platform.items()) + "</main>")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>Path cleaning steps</title>'
            f'<style>{CSS}</style></head><body>{body}</body></html>')
