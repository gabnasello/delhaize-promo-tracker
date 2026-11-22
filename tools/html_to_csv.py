"""Reads saved Delhaize favorites-list pages (.htm/.html) and merges them into data/favorites.csv.
Lists found in the given files replace the same lists in the CSV; other lists are kept."""
import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).parent.parent
CSV_PATH = ROOT / "data" / "favorites.csv"
FIELDS = ["list", "name", "url", "image", "price_when_saved"]


def parse(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    h1 = soup.find("h1")
    lst = h1.get_text(strip=True) if h1 else path.stem
    rows = []
    for b in soup.select('[data-testid="product-block"]'):
        a = b.select_one('[data-testid="product-block-image-link"]')
        if not a:
            continue
        img = b.select_one('[data-testid="product-block-image"]')
        src = ""
        if img and img.get("srcset"):
            m = re.search(r"(https://static\.delhaize\.be/[^\s?]+)", img["srcset"])
            if m:
                src = m.group(1) + "?imwidth=300"
        price = ""
        pr = b.select_one('[data-testid="product-block-price"]')
        if pr:
            m = re.search(r"(\d+) euro(?: (\d+) cent)?", pr.get("aria-label", ""))
            if m:
                price = f"{m.group(1)}.{(m.group(2) or '0').zfill(2)}"
        rows.append({
            "list": lst,
            "name": re.sub(r"\s+", " ", a.get("aria-label", "")).strip(),
            "url": a["href"].split("?")[0],
            "image": src,
            "price_when_saved": price,
        })
    return lst, rows


def main():
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "saved_pages")
    files = sorted([*folder.glob("*.htm"), *folder.glob("*.html")])
    if not files:
        sys.exit(f"No .htm files in {folder}")
    existing = []
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
    new_lists = {}
    for f in files:
        lst, rows = parse(f)
        if not rows:
            print(f"SKIP {f.name}: no products found (is it the list page itself, fully scrolled?)")
            continue
        new_lists[lst] = rows
        print(f"{f.name}: list '{lst}', {len(rows)} products")
    merged = [r for r in existing if r["list"] not in new_lists] + [r for rows in new_lists.values() for r in rows]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(merged)
    print(f"Wrote {len(merged)} rows to {CSV_PATH}")


if __name__ == "__main__":
    main()
