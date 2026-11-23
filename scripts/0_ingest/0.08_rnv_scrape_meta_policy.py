"""
Scrape one section of the Meta Privacy Policy, with all its nested pop-ups, into readable text, HTML and JSON.

  make meta_policy                                   # on your own machine (needs internet and Playwright)
  python -I scripts/0_ingest/0.08_rnv_scrape_meta_policy.py [--section "..."] [--version ID] [--max-depth N]

Setup (once): pip install playwright && playwright install chromium

The policy is rendered by JavaScript, so a headless Chromium loads it. Section headings are
div[role=heading][aria-level=2]; the section runs from its heading up to the next one. The details sit in pop-ups
(a [role=dialog]). Every pop-up has its own URL (?subpage=<id> or ?annotations[0]=<id>), so instead of clicking
through the dialogs the script opens each pop-up URL directly and follows the pop-up links it finds there
(breadth first, up to --max-depth levels deep). A "story" pop-up with a Next button has pages (&story_page=N);
they are joined into one pop-up. Links to other pages are kept as links, not followed.

Writes to data/meta_policy/<version>_<section-slug>.{txt,html,json}:
  .txt   Markdown-style text: the section, then every pop-up as its own part, with [text](#popup-id) references
  .html  The same as one clean standalone page (no Meta CSS or scripts); pop-up links jump to the pop-up
  .json  Blocks (heading / paragraph / list item, with their links) per part, plus the source URLs and scrape time
"""

import argparse
import html
import json
import re
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse

# -I (isolated mode) ignores PYTHONPATH, so add the repo root for `src`
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src import config  # noqa: E402

VERSION = "5407378522724295"
SECTION = "What information do we collect?"
POLICY_URL = "https://www.facebook.com/privacy/policy/version/{version}/"

# Turns a DOM subtree into blocks: {type: heading|p|li, level, depth, inline: [{text, href?}]}.
# Only nodes that intersect `range` are kept (the whole subtree when range is null).
BLOCKS_JS = r"""
([root, range]) => {
  const SKIP = new Set(['SVG', 'IMG', 'VIDEO', 'SOURCE', 'TRACK', 'SCRIPT', 'STYLE', 'HR', 'BUTTON']);
  const BLOCK = new Set(['block', 'flex', 'grid', 'list-item', 'table']);
  const blocks = [];
  let cur = null;
  const flush = () => {
    if (cur) {
      cur.inline = cur.inline.filter(x => x.text.length);
      if (cur.inline.length) blocks.push(cur);
    }
    cur = null;
  };
  const open = (type, extra) => { flush(); cur = Object.assign({type, inline: []}, extra); };
  const add = (text, href) => {
    text = text.replace(/\s+/g, ' ');
    if (!text.trim()) { if (cur && cur.inline.length) cur.inline.push({text: ' '}); return; }
    if (!cur) open('p', {});
    cur.inline.push(href ? {text, href} : {text});
  };
  const skip = e => SKIP.has(e.tagName.toUpperCase()) || e.getAttribute('aria-hidden') === 'true'
    || e.getAttribute('role') === 'button' || (range && !range.intersectsNode(e));
  const walk = (node, depth) => {
    for (const n of node.childNodes) {
      if (n.nodeType === 3) { if (!range || range.intersectsNode(n)) add(n.textContent); continue; }
      if (n.nodeType !== 1 || skip(n)) continue;
      const role = n.getAttribute('role'), tag = n.tagName;
      if (role === 'heading') {
        open('heading', {level: +(n.getAttribute('aria-level') || 2)});
        add(n.innerText.trim()); flush(); continue;
      }
      if (tag === 'A') { add(n.innerText, n.getAttribute('href')); continue; }
      if (tag === 'LI') { open('li', {depth}); walk(n, depth + 1); flush(); continue; }
      const isBlock = BLOCK.has(getComputedStyle(n).display);
      if (isBlock) flush();
      walk(n, depth);
      if (isBlock) flush();
    }
  };
  walk(root, 0); flush();
  for (const b of blocks) {   // trim and merge neighbouring plain text
    const m = [];
    for (const x of b.inline) {
      const last = m[m.length - 1];
      if (last && !last.href && !x.href) last.text += x.text; else m.push({...x});
    }
    if (m.length) { m[0].text = m[0].text.replace(/^\s+/, ''); m[m.length - 1].text = m[m.length - 1].text.replace(/\s+$/, ''); }
    b.inline = m.filter(x => x.text.length);
  }
  return blocks.filter(b => b.inline.length);
}
"""

# The section: from its level-2 heading up to the next level-2 heading
SECTION_JS = r"""
(title) => {
  const hs = [...document.querySelectorAll('[role=heading][aria-level="2"]')];
  const i = hs.findIndex(h => h.innerText.trim() === title);
  if (i < 0) return null;
  const r = document.createRange();
  r.setStartBefore(hs[i]);
  if (hs[i + 1]) r.setEndBefore(hs[i + 1]); else r.setEndAfter(hs[i].parentElement.lastChild);
  return r;
}
"""


# ---- links ----

def popup_key(href, policy_url):
    """The pop-up id a policy link opens (the annotation on top, else the subpage), or None for other links."""
    url = urlparse(urljoin(policy_url, href))
    if url.path.rstrip("/") != urlparse(policy_url).path.rstrip("/"):
        return None
    q = parse_qs(url.query)
    return (q.get("annotations[0]") or q.get("subpage") or [None])[0]


def popup_url(key, policy_url):
    param = "subpage" if ".subpage." in key else "annotations[0]"
    return f"{policy_url}?{param}={key}"


def clean_href(href, policy_url):
    """Absolute URL without Facebook's l.php redirect wrapper."""
    url = urljoin(policy_url, href)
    p = urlparse(url)
    if p.netloc == "l.facebook.com" and p.path == "/l.php":
        url = unquote(parse_qs(p.query).get("u", [url])[0])
    return url


def resolve_links(blocks, policy_url):
    """Set `popup` (pop-up id) or a clean absolute `href` on every link; return the pop-up ids in order."""
    keys = []
    for b in blocks:
        for x in b["inline"]:
            if "href" not in x:
                continue
            key = popup_key(x["href"], policy_url)
            if key:
                x["popup"] = key
                del x["href"]
                keys.append(key)
            else:
                x["href"] = clean_href(x["href"], policy_url)
    return list(dict.fromkeys(keys))


# ---- scraping ----

def load(page, url, selector, retries=3):
    for attempt in range(1, retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.locator(selector).last.wait_for(timeout=30_000)
            page.wait_for_timeout(1500)                    # let the dialog content settle
            return
        except Exception as e:                             # noqa: BLE001 - network or render hiccup: retry
            print(f"  attempt {attempt}/{retries} failed for {url}: {type(e).__name__}")
            if attempt == retries:
                raise
            time.sleep(5 * attempt)


def scrape_section(page, policy_url, title):
    load(page, policy_url, '[role=heading][aria-level="2"]')
    rng = page.evaluate_handle(SECTION_JS, title)
    if page.evaluate("r => r === null", rng):
        found = page.eval_on_selector_all('[role=heading][aria-level="2"]', "hs => hs.map(h => h.innerText.trim())")
        raise SystemExit(f"Section {title!r} not found. Sections on the page: {found}")
    root = page.evaluate_handle("r => r.commonAncestorContainer", rng)
    return page.evaluate(BLOCKS_JS, [root, rng])


def scrape_popup(page, url, delay):
    """Blocks of one pop-up. A story (Next button) has pages ?...&story_page=N: all pages are joined."""
    blocks, n = [], 0
    while True:
        load(page, url + (f"&story_page={n}" if n else ""), "[role=dialog] [role=heading]")
        dialog = page.locator("[role=dialog]").last
        part = dialog.evaluate(f"d => ({BLOCKS_JS})([d, null])")
        has_next = any(f"story_page={n + 1}" in x.get("href", "") for b in part for x in b["inline"])
        for b in part:                                     # drop the Next/Previous links of a story
            b["inline"] = [x for x in b["inline"] if "story_page=" not in x.get("href", "")]
        blocks += [b for b in part if b["inline"]]
        if not has_next:
            return blocks
        n += 1
        time.sleep(delay)


def crawl(page, policy_url, title, max_depth, delay):
    print(f"Section: {title}")
    section = scrape_section(page, policy_url, title)
    queue = deque((k, 1, None) for k in resolve_links(section, policy_url))
    popups, seen = {}, {k for k, _, _ in queue}
    while queue:
        key, depth, parent = queue.popleft()
        url = popup_url(key, policy_url)
        print(f"  [{len(popups) + 1}] depth {depth}: {key}")
        time.sleep(delay)
        blocks = scrape_popup(page, url, delay)
        children = resolve_links(blocks, policy_url)
        heading = next((b for b in blocks if b["type"] == "heading"), None)
        popups[key] = {"id": key, "url": url, "depth": depth, "opened_from": parent,
                       "title": "".join(x["text"] for x in heading["inline"]) if heading else key, "blocks": blocks}
        if depth < max_depth:
            for c in children:
                if c not in seen:
                    seen.add(c)
                    queue.append((c, depth + 1, key))
        else:
            popups[key]["not_followed"] = [c for c in children if c not in seen]
    return section, popups


# ---- output ----

def anchor(key):
    return "popup-" + re.sub(r"[^A-Za-z0-9_-]+", "-", key)


def inline_text(inline):
    out = []
    for x in inline:
        if "popup" in x:
            out.append(f"[{x['text']}](#{anchor(x['popup'])})")
        elif "href" in x:
            out.append(f"[{x['text']}]({x['href']})")
        else:
            out.append(x["text"])
    return "".join(out)


def inline_html(inline):
    out = []
    for x in inline:
        t = html.escape(x["text"])
        if "popup" in x:
            out.append(f'<a href="#{anchor(x["popup"])}" class="popup">{t}</a>')
        elif "href" in x:
            out.append(f'<a href="{html.escape(x["href"])}">{t}</a>')
        else:
            out.append(t)
    return "".join(out)


def blocks_text(blocks, shift=0):
    lines = []
    for b in blocks:
        if b["type"] == "heading":
            lines += ["", "#" * min(6, b["level"] + shift) + " " + inline_text(b["inline"]), ""]
        elif b["type"] == "li":
            lines.append("  " * b.get("depth", 0) + "- " + inline_text(b["inline"]))
        else:
            lines += ["", inline_text(b["inline"]), ""]
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def blocks_html(blocks, shift=0):
    out, in_list = [], False
    for b in blocks:
        if b["type"] == "li" and not in_list:
            out.append("<ul>")
            in_list = True
        if b["type"] != "li" and in_list:
            out.append("</ul>")
            in_list = False
        body = inline_html(b["inline"])
        if b["type"] == "heading":
            n = min(6, b["level"] + shift)
            out.append(f"<h{n}>{body}</h{n}>")
        elif b["type"] == "li":
            out.append(f"<li>{body}</li>")
        else:
            out.append(f"<p>{body}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def write_outputs(out_dir, stem, meta, section, popups):
    out_dir.mkdir(parents=True, exist_ok=True)
    order = list(popups.values())

    # .txt (Markdown-style)
    head = [f"# Meta Privacy Policy: {meta['section']}", "",
            f"Source: {meta['policy_url']}", f"Scraped: {meta['scraped_at']}",
            f"Pop-ups: {len(order)} (each below as its own part; [text](#popup-...) links point to them)", "",
            "---", "", "# Section", ""]
    parts = [blocks_text(section)]
    for p in order:
        parent = f" (opened from {p['opened_from']})" if p["opened_from"] else " (opened from the section)"
        parts.append("\n".join(["", "---", "", f"# Pop-up {p['id']}{parent}", f"<a id=\"{anchor(p['id'])}\"></a>",
                                f"URL: {p['url']}", "", blocks_text(p["blocks"], shift=1)]))
    (out_dir / f"{stem}.txt").write_text("\n".join(head) + "\n".join(parts) + "\n", encoding="utf-8")

    # .html (one standalone page)
    css = ("body{font:16px/1.5 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem;color:#1c1e21}"
           "section{border-top:1px solid #ccc;margin-top:2rem}.meta{color:#555;font-size:.9em}"
           "a.popup{text-decoration:underline dotted}a.popup::after{content:' \\2197';font-size:.8em}")
    body = [f"<h1>Meta Privacy Policy: {html.escape(meta['section'])}</h1>",
            f'<p class="meta">Source: <a href="{meta["policy_url"]}">{meta["policy_url"]}</a><br>'
            f"Scraped: {meta['scraped_at']} &middot; {len(order)} pop-ups, each below the section</p>",
            '<section id="section">', blocks_html(section), "</section>"]
    for p in order:
        frm = (f'<a href="#{anchor(p["opened_from"])}">{html.escape(p["opened_from"])}</a>'
               if p["opened_from"] else '<a href="#section">the section</a>')
        body += [f'<section id="{anchor(p["id"])}">',
                 f'<p class="meta">Pop-up <code>{html.escape(p["id"])}</code>, opened from {frm} &middot; '
                 f'<a href="{html.escape(p["url"])}">source</a></p>',
                 blocks_html(p["blocks"], shift=1), "</section>"]
    page = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f"<title>{html.escape(meta['section'])} - Meta Privacy Policy</title><style>{css}</style></head>\n"
            f"<body>\n" + "\n".join(body) + "\n</body></html>\n")
    (out_dir / f"{stem}.html").write_text(page, encoding="utf-8")

    # .json
    data = {**meta, "section_blocks": section, "popups": order}
    (out_dir / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return [out_dir / f"{stem}.{ext}" for ext in ("txt", "html", "json")]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--version", default=VERSION, help="policy version id in the URL")
    ap.add_argument("--section", default=SECTION, help="level-2 heading of the section")
    ap.add_argument("--max-depth", type=int, default=5, help="pop-up nesting levels to follow")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between page loads")
    ap.add_argument("--headed", action="store_true", help="show the browser")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    policy_url = POLICY_URL.format(version=args.version)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        page = browser.new_page(locale="en-US", viewport={"width": 1280, "height": 900})
        section, popups = crawl(page, policy_url, args.section, args.max_depth, args.delay)
        browser.close()

    meta = {"policy_url": policy_url, "version": args.version, "section": args.section,
            "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "max_depth": args.max_depth}
    files = write_outputs(Path(config.META_POLICY_DIR), f"{args.version}_{slug(args.section)}", meta, section, popups)
    print(f"{len(popups)} pop-ups")
    for f in files:
        print(f"Wrote {f}")


if __name__ == "__main__":
    main()
