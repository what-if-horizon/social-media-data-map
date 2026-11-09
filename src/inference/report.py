"""HTML report for the taxonomy classification (scripts/2_classification/2.07_rnv_build_report.py).

One self-contained HTML file per phase (smoke, test, validation) with: the pytest result on the inference
outputs, a summary of the classification, the LLM judge, and, when human annotations were evaluated, the
accuracy against them. Charts are plain HTML/CSS (no external libraries), with light and dark themes.
"""

import html
from collections import Counter
from datetime import datetime

CSS = """
:root{color-scheme:light;--surface:#fcfcfb;--card:#f4f3f0;--text:#0b0b0b;--text2:#52514e;--grid:#dcdad4;
--s1:#2a78d6;--s2:#eb6834;--s4:#eda100;--none:#9a988f}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--surface:#1a1a19;--card:#242422;--text:#f0efec;
--text2:#c3c2b7;--grid:#3a3a37;--s1:#3987e5;--s2:#d95926;--s4:#c98500;--none:#77756d}}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--text);
font:15px/1.5 system-ui,sans-serif;padding:24px 16px}main{max-width:960px;margin:0 auto}
h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:32px 0 8px;padding-top:16px;border-top:1px solid var(--grid)}
h3{font-size:15px;margin:16px 0 6px}p.meta,.note{color:var(--text2);margin:2px 0 12px}
.cards{display:flex;flex-wrap:wrap;gap:12px}.card{background:var(--card);border-radius:8px;padding:12px 16px;min-width:140px}
.card b{display:block;font-size:24px}.card span{color:var(--text2);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--text2);font-weight:600}td.num{text-align:right;font-variant-numeric:tabular-nums}
.bar-row{display:grid;grid-template-columns:minmax(120px,300px) 1fr 56px;gap:8px;align-items:center;margin:3px 0;font-size:13px}
.bar-row .lab{overflow-wrap:anywhere}.track{height:14px}.fill{height:100%;background:var(--s1);border-radius:0 4px 4px 0}
.stack{display:flex;height:18px}.stack i{display:block;height:100%;border-left:2px solid var(--surface)}.stack i:first-child{border-left:0}
.legend{display:flex;flex-wrap:wrap;gap:4px 16px;font-size:13px;color:var(--text2);margin:6px 0}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}
.hist{display:flex;align-items:flex-end;gap:4px;height:110px;border-bottom:1px solid var(--grid)}
.hist div{flex:1;background:var(--s1);border-radius:4px 4px 0 0;min-height:1px;position:relative}
.hist-x{display:flex;gap:4px;font-size:11px;color:var(--text2)}.hist-x span{flex:1;text-align:center}
.ok,.bad{font-weight:600}.ok::before{content:"\\2713  "}.bad::before{content:"\\2717  "}.ok{color:var(--s1)}.bad{color:var(--s2)}
.cm td{text-align:center;padding:2px 4px;min-width:34px}.cm th.rot{font-size:11px}
.cm td.hit{color:#fff}pre{white-space:pre-wrap;margin:0;font:12px/1.4 ui-monospace,monospace}
"""

VERDICT_COLORS = {"correct": "var(--s1)", "plausible": "var(--s4)", "incorrect": "var(--s2)", None: "var(--none)"}
VERDICT_NAMES = {"correct": "correct", "plausible": "plausible", "incorrect": "incorrect", None: "no valid verdict"}


def esc(x):
    return html.escape(str(x))


def pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def card(value, label):
    return f'<div class="card"><b>{esc(value)}</b><span>{esc(label)}</span></div>'


def bars(items, total=None):
    """Horizontal bars: items = [(label, count)], sorted as given."""
    if not items:
        return '<p class="note">No data.</p>'
    top = max(c for _, c in items) or 1
    rows = []
    for lab, c in items:
        share = f" ({100 * c / total:.0f}%)" if total else ""
        rows.append(f'<div class="bar-row" title="{esc(lab)}: {c}{share}"><span class="lab">{esc(lab)}</span>'
                    f'<div class="track"><div class="fill" style="width:{100 * c / top:.1f}%"></div></div>'
                    f'<span class="num">{c}</span></div>')
    return "".join(rows)


def histogram(values, width=10):
    counts = Counter(min(int(v // width), 100 // width - 1) for v in values)
    top = max(counts.values(), default=1)
    cols = "".join(f'<div style="height:{100 * counts.get(b, 0) / top:.0f}%" '
                   f'title="{b * width}-{(b + 1) * width}: {counts.get(b, 0)}"></div>' for b in range(100 // width))
    xs = "".join(f"<span>{b * width}</span>" for b in range(100 // width))
    return f'<div class="hist">{cols}</div><div class="hist-x">{xs}</div>'


def section_pytest(res):
    if not res:
        return '<p class="note">No pytest result found. Run <code>make inference-check</code>.</p>'
    tests = res.get("tests", [])
    failed = [t for t in tests if t["outcome"] == "failed"]
    status = ('<span class="ok">passed</span>' if not failed and tests
              else '<span class="bad">failed</span>' if failed else "no tests ran")
    out = [f'<div class="cards">{card(len(tests), "checks")}{card(len(tests) - len(failed), "passed")}'
           f'{card(len(failed), "failed")}</div><p>Overall: {status}. '
           f'{"The judge is run for the failed checks." if failed else ""}</p>']
    out.append("<table><tr><th>Check</th><th>Result</th><th>Details</th></tr>")
    for t in tests:
        cls = "ok" if t["outcome"] == "passed" else "bad" if t["outcome"] == "failed" else ""
        out.append(f'<tr><td>{esc(t["nodeid"].split("::", 1)[-1])}</td><td class="{cls}">{esc(t["outcome"])}</td>'
                   f'<td><pre>{esc(t.get("message", ""))}</pre></td></tr>')
    out.append("</table>")
    return "".join(out)


def section_inference(inference):
    records = [r for recs in inference.values() for r in recs]
    valid = [r for r in records if r.get("predictions")]
    top1 = Counter(r["predictions"][0]["label"] for r in valid)
    conf = [r["predictions"][0]["confidence"] for r in valid]
    out = [f'<div class="cards">{card(len(records), "paths classified")}{card(len(valid), "with valid output")}'
           f'{card(len(records) - len(valid), "without valid output")}{card(len(inference), "platforms")}</div>',
           "<h3>Top-1 label</h3>", bars(top1.most_common(), total=len(valid)),
           "<h3>Confidence of the top-1 label</h3>", histogram(conf),
           '<p class="note">Number of paths by confidence (x axis: lower bound of each 10-point bucket).</p>']
    return "".join(out)


def section_judge(judge, inference):
    if not judge:
        return ('<p class="note">The judge has not run (it is started when the pytest fails, '
                'or with <code>make judge</code>).</p>')
    legend = "".join(f'<span><i style="background:{VERDICT_COLORS[v]}"></i>{VERDICT_NAMES[v]}</span>'
                     for v in ("correct", "plausible", "incorrect", None))
    out = [f'<div class="legend">{legend}</div>']
    for platform, rows in sorted(judge.items()):
        counts = Counter(r.get("verdict") for r in rows)
        segs = "".join(f'<i style="width:{100 * counts[v] / len(rows):.1f}%;background:{VERDICT_COLORS[v]}" '
                       f'title="{VERDICT_NAMES[v]}: {counts[v]}"></i>' for v in VERDICT_COLORS if counts[v])
        text = ", ".join(f"{counts[v]} {VERDICT_NAMES[v]}" for v in VERDICT_COLORS if counts[v])
        out.append(f'<div class="bar-row" style="grid-template-columns:100px 1fr 260px"><span class="lab">{esc(platform)}</span>'
                   f'<div class="stack">{segs}</div><span>{esc(text)}</span></div>')
    flagged = [(pl, r) for pl, rows in sorted(judge.items()) for r in rows if r.get("verdict") != "correct"]
    out.append(f"<h3>Paths the judge did not mark correct ({len(flagged)})</h3>")
    if flagged:
        out.append("<table><tr><th>Platform</th><th>Path</th><th>Classifier top-1</th><th>Verdict</th>"
                   "<th>Judge label</th><th>Judge rationale</th></tr>")
        for pl, r in flagged:
            out.append(f'<tr><td>{esc(pl)}</td><td>{esc(r["path"])}</td><td>{esc(r.get("model_top1"))}</td>'
                       f'<td>{esc(VERDICT_NAMES.get(r.get("verdict"), r.get("verdict")))}</td>'
                       f'<td>{esc(r.get("judge_label"))}</td><td>{esc(r.get("rationale", r.get("error", "")))}</td></tr>')
        out.append("</table>")
    return "".join(out)


def confusion_table(stats):
    rows = stats["confusion"]
    labels = sorted({r["truth"] for r in rows} | {r["predicted"] for r in rows if r["predicted"]})
    cells = {(r["truth"], r["predicted"]): r["count"] for r in rows}
    top = max(cells.values(), default=1)
    head = "".join(f'<th class="rot" title="{esc(l)}">{i}</th>' for i, l in enumerate(labels, 1))
    out = [f'<table class="cm"><tr><th>Human \\ model</th>{head}</tr>']
    for i, t in enumerate(labels, 1):
        tds = []
        for p in labels:
            c = cells.get((t, p), 0)
            share = c / top
            style = (f' style="background:color-mix(in srgb,var(--s1) {100 * share:.0f}%,var(--surface))"' if c else "")
            tds.append(f'<td class="{"hit" if share > .55 else ""}"{style} title="human: {esc(t)}; model: {esc(p)}; n={c}">{c or ""}</td>')
        out.append(f'<tr><th title="{esc(t)}">{i}. {esc(t)}</th>{"".join(tds)}</tr>')
    out.append("</table>")
    return "".join(out)


def section_human(human):
    if not human or not human.get("platforms"):
        return ('<p class="note">No human evaluation yet. When the annotations are in, run '
                '<code>make eval-human SPLIT=...</code> and rebuild this report.</p>')
    pooled = human["pooled"]
    out = [f'<div class="cards">{card(pooled["n"], "annotated paths")}{card(pct(pooled["top1_accuracy"]), "top-1 accuracy")}'
           f'{card(pct(pooled["top3_accuracy"]), "top-3 accuracy")}{card(pooled["n_without_prediction"], "without prediction")}</div>',
           "<h3>Top-1 accuracy per platform</h3>"]
    out.append("<table><tr><th>Platform</th><th>n</th><th>Top-1</th><th>Top-3</th><th>Unknown human labels</th></tr>")
    for pl, s in sorted(human["platforms"].items()):
        out.append(f'<tr><td>{esc(pl)}</td><td class="num">{s["n"]}</td><td class="num">{pct(s["top1_accuracy"])}</td>'
                   f'<td class="num">{pct(s["top3_accuracy"])}</td><td class="num">{len(s["unknown_gold_labels"])}</td></tr>')
    out.append("</table><h3>Recall per label (pooled)</h3>")
    rec = [(l, round(100 * v["recall"])) for l, v in pooled["per_class"].items() if v["recall"] is not None]
    out.append(bars(sorted(rec, key=lambda x: -x[1])).replace("</span></div>", "%</span></div>"))
    out.append("<h3>Confusion matrix (pooled, top-1)</h3>" + confusion_table(pooled))
    return "".join(out)


def build_report(phase, pytest_result, inference, judge, human, models=None):
    models = models or {}
    meta = " | ".join(f"{k}: {v}" for k, v in models.items())
    body = f"""<main><h1>Taxonomy classification: {esc(phase)}</h1>
<p class="meta">Generated {datetime.now():%Y-%m-%d %H:%M}{(" | " + esc(meta)) if meta else ""}</p>
<h2>1. Pytest on the inference output</h2>{section_pytest(pytest_result)}
<h2>2. Classification summary</h2>{section_inference(inference)}
<h2>3. LLM judge</h2>{section_judge(judge, inference)}
<h2>4. Comparison with human annotations</h2>{section_human(human)}</main>"""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Classification report {esc(phase)}</title><style>{CSS}</style></head><body>{body}</body></html>')
