"""
Weekly check. Reads data/favorites.csv, opens each product page once, reads the promotion tags
and writes docs/promos.json containing ONLY the favorites that are on offer (privacy: the public
page never reveals the full favorites list or your list names).

Real offers are tags with a data-promo-type other than SUBSCRIBER (e.g. MEMBER: "1+1 gratis", "-20%").
The SUBSCRIBER tag (subscription discount) is ignored: it is account-specific and not visible when logged out.
Env: LIMIT=N first N products | ONLY="a,b" names containing a or b | DEBUG=1 save page HTML to checker/debug/
In GitHub Actions nothing identifying (names, URLs) is printed, because logs of public repos are public.
"""
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
CSV_PATH = ROOT / "data" / "favorites.csv"
OUT = ROOT / "docs" / "promos.json"
FULL = Path(__file__).parent / "last_run_full.json"   # local only, git-ignored
DEBUG_DIR = Path(__file__).parent / "debug"
QUIET = bool(os.environ.get("GITHUB_ACTIONS"))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0.0.0 Safari/537.36")
SECTION = '[data-testid="product-details-section"]'

JS = """
() => {
  const root = document.querySelector('[data-testid="product-details-section"]');
  const inTile = e => !!e.closest('[data-testid="product-block"]');   // ignore other products' tiles
  const scope = root || document;
  const clean = e => e.innerText.replace(/\\s+/g, ' ').trim();
  const promos = [...scope.querySelectorAll('[data-promo-type]')].filter(e => !inTile(e))
      .map(e => ({type: e.getAttribute('data-promo-type'), label: clean(e)}));
  const extra = [...scope.querySelectorAll('[data-testid="tag-promo-label"]')].filter(e => !inTile(e))
      .map(e => ({type: 'PROMO', label: clean(e)}));
  const p = [...scope.querySelectorAll('[aria-label^="Prijs:"]')].find(e => !inTile(e));
  return {found: !!root, promos, extra, price: p ? p.getAttribute('aria-label') : ''};
}
"""


def parse_price(label):
    m = re.search(r"(\d+) euro(?: (\d+) cent)?", label or "")
    return f"{m.group(1)}.{(m.group(2) or '0').zfill(2)}" if m else ""


def clean_label(t):
    """'1+1 gratis Promotie enkel geldig met SuperPlus kaart van ... Bekijk aanbod' -> '1+1 gratis'"""
    return re.split(r"\s+Promotie\b", re.sub(r"\s*Bekijk aanbod\s*$", "", t), maxsplit=1)[0].strip()


def parse_until(t):
    m = re.search(r"tot en met (\d{2})/(\d{2})/(\d{4})", t)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def check(page, url, idx):
    rec = {"status": "none", "offers": [], "valid_until": "", "needs_card": False, "price": "", "error": ""}
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        try:
            page.wait_for_selector(SECTION, timeout=15000)
        except Exception:
            pass
        try:  # promo tags may render a moment later
            page.wait_for_selector('[data-promo-type], [data-testid="tag-promo-label"]', timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(500)
        d = page.evaluate(JS)
        if (os.environ.get("DEBUG") or not d["found"]) and not QUIET:
            DEBUG_DIR.mkdir(exist_ok=True)
            (DEBUG_DIR / f"{idx:03d}.html").write_text(page.content(), encoding="utf-8")
        if not d["found"]:
            rec["error"] = "product section not found (blocked, or layout changed)"
        seen = set()
        for pr in d["promos"] + d["extra"]:
            if pr["type"] == "SUBSCRIBER":
                continue
            label = clean_label(pr["label"])
            if not label or label in seen:
                continue
            seen.add(label)
            rec["offers"].append(label)
            rec["valid_until"] = max(rec["valid_until"], parse_until(pr["label"]))
            rec["needs_card"] = rec["needs_card"] or "SuperPlus" in pr["label"]
        rec["price"] = parse_price(d["price"])
        rec["status"] = "offer" if rec["offers"] else "none"
        if rec["error"]:
            rec["status"] = "error"
    except Exception as e:
        rec["error"] = str(e)[:200]
        rec["status"] = "error"
    return rec


def main():
    if not CSV_PATH.exists():
        sys.exit("data/favorites.csv not found. Copy your favorites file there (see README).")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    products = {}  # one visit per URL, remember all lists it belongs to
    for r in rows:
        p = products.setdefault(r["url"], {"name": r["name"], "url": r["url"], "image": r["image"], "lists": []})
        if r["list"] not in p["lists"]:
            p["lists"].append(r["list"])
    urls = list(products)
    only = [t.strip().lower() for t in os.environ.get("ONLY", "").split(",") if t.strip()]
    if only:
        urls = [u for u in urls if any(t in products[u]["name"].lower() for t in only)]
    limit = int(os.environ.get("LIMIT", "0") or 0)
    if limit:
        urls = urls[:limit]

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(locale="nl-BE", user_agent=UA)
        page = ctx.new_page()
        for i, url in enumerate(urls):
            rec = {**products[url], **check(page, url, i)}
            results.append(rec)
            if QUIET:
                print(".", end="", flush=True)
            else:
                tag = {"offer": "OFFER", "none": "     ", "error": "ERROR"}[rec["status"]]
                print(tag, rec["name"][:55], "|", "; ".join(rec["offers"]), rec["error"])
        browser.close()
    print()

    n_err = sum(r["status"] == "error" for r in results)
    n_off = sum(r["status"] == "offer" for r in results)
    if results and n_err == len(results):
        sys.exit("Every product failed: not writing promos.json (run locally with DEBUG=1 to investigate).")
    public = [{k: r[k] for k in ("name", "url", "image", "offers", "valid_until", "needs_card", "price")}
              for r in results if r["status"] == "offer"]
    public.sort(key=lambda r: r["name"].lower())
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(), "errors": n_err,
                               "items": public}, ensure_ascii=False, indent=1), encoding="utf-8")
    if not QUIET:
        FULL.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{n_off} on offer, {n_err} errors, {len(results)} products checked")


if __name__ == "__main__":
    main()
