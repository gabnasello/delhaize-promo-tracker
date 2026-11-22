"""
Sends the weekly "favorites on offer" summary to Telegram, rendered from notify/template.toml
and docs/promos.json (written by the weekly check).

Env (GitHub secrets): TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.   Optional: SITE_URL, RUN_URL, RUN_CONCLUSION.
Local preview without sending:  python notify/telegram_notify.py --dry-run [--sample]
Logs in public repos are public, so only counts are printed in CI, never names or the token.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import tomllib
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROMOS = ROOT / "docs" / "promos.json"
TEMPLATE = Path(__file__).parent / "template.toml"
API = os.environ.get("TELEGRAM_API", "https://api.telegram.org")
PH = re.compile(r"\{(\w+)\}")

SAMPLE = {
    "checked_at": datetime.now().isoformat(), "errors": 1,
    "items": [
        {"name": "Delhaize Roodbaarsfilet", "url": "https://www.delhaize.be/", "price": "5.72",
         "image": "https://static.delhaize.be/medias/sys_master/products/hc0/h4b/13904639787038.jpg?imwidth=300",
         "offers": ["-20%"], "valid_until": "2026-11-25", "needs_card": True},
        {"name": "Delhaize Frietjes | Zoete aardappel", "url": "https://www.delhaize.be/", "price": "",
         "image": "", "offers": ["1+1 gratis"], "valid_until": "2026-11-25", "needs_card": True},
    ],
}


class TgError(Exception):
    pass


def render(text, values):
    """Fill {placeholders}; drop any line whose placeholder is empty."""
    out = []
    for line in text.strip("\n").split("\n"):
        if any(values.get(k) == "" for k in PH.findall(line)):
            continue
        out.append(PH.sub(lambda m: str(values.get(m.group(1), m.group(0))), line))
    return "\n".join(out).strip()


def dmy(iso):
    try:
        y, m, d = iso[:10].split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return ""


def site_url():
    if os.environ.get("SITE_URL"):
        return os.environ["SITE_URL"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" in repo:
        owner, name = repo.split("/", 1)
        return f"https://{owner.lower()}.github.io/{name}/"
    return "(set the SITE_URL variable)"


def tg(token, method, payload):
    req = urllib.request.Request(
        f"{API}/bot{token}/{method}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                info = json.loads(e.read().decode(errors="ignore"))
            except Exception:
                info = {}
            if e.code == 429 and attempt == 0:
                time.sleep(info.get("parameters", {}).get("retry_after", 5) + 1)
                continue
            raise TgError(f"{method}: HTTP {e.code} {info.get('description', '')}") from None
        except urllib.error.URLError:
            raise TgError(f"{method}: network error") from None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print instead of sending")
    ap.add_argument("--sample", action="store_true", help="use built-in sample data")
    a = ap.parse_args()

    cfg = tomllib.loads(TEMPLATE.read_text(encoding="utf-8"))
    st = cfg["settings"]
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not a.dry_run and not (token and chat):
        sys.exit("Secrets TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")
    delay = float(os.environ.get("NOTIFY_DELAY", "3.1"))

    sent = []

    def send(method, payload):
        if a.dry_run:
            print(f"--- {method} ---")
            print(payload.get("caption") or payload.get("text"))
            if payload.get("photo"):
                print(f"[photo: {payload['photo']}]")
            return
        payload["chat_id"] = chat
        tg(token, method, payload)
        sent.append(method)
        time.sleep(delay)

    def message(text):
        send("sendMessage", {"text": text, "parse_mode": "HTML", "link_preview_options": {"is_disabled": True}})

    conclusion = os.environ.get("RUN_CONCLUSION", "")
    if conclusion in ("cancelled", "skipped"):
        print(f"Weekly check {conclusion}: nothing to send.")
        return
    base = {"site_url": html.escape(site_url()), "run_url": html.escape(os.environ.get("RUN_URL", ""))}

    if conclusion == "failure":
        if st.get("send_on_failure", True):
            message(render(cfg["failed"]["text"], base))
        print("Sent failure notice." if not a.dry_run else "")
        return

    d = SAMPLE if a.sample else json.loads(PROMOS.read_text(encoding="utf-8"))
    if str(d.get("checked_at", "1970"))[:4] < "2000":
        sys.exit("No data yet: run the 'Weekly promo check' workflow first.")
    items = d["items"]
    errors = d.get("errors", 0)
    common = {**base, "count": str(len(items)), "checked_date": dmy(d["checked_at"]),
              "errors_note": f"⚠️ {errors} product(s) could not be checked." if errors else ""}

    if not items:
        if st.get("send_when_empty", True):
            message(render(cfg["empty"]["text"], common))
        print("Sent: nothing on offer.")
        return

    message(render(cfg["header"]["text"], common))
    shown = items[: int(st.get("max_items", 15))]
    for i in shown:
        vals = {**base,
                "name": html.escape(i["name"]),
                "offers": html.escape(", ".join(i["offers"])),
                "price": html.escape(i.get("price", "")),
                "until": dmy(i["valid_until"]) if i.get("valid_until") else "",
                "card_note": "SuperPlus card required" if i.get("needs_card") else "",
                "url": html.escape(i["url"], quote=True)}
        text = render(cfg["item"]["text"], vals)
        if st.get("photos", True) and i.get("image", "").startswith("http"):
            try:
                send("sendPhoto", {"photo": i["image"], "caption": text, "parse_mode": "HTML"})
                continue
            except TgError:
                pass  # image not fetchable by Telegram: fall back to plain text
        message(text)
    if len(items) > len(shown):
        message(render(cfg["more"]["text"], {**common, "remaining": str(len(items) - len(shown))}))
    print(f"Sent {len(shown)} product message(s) for {len(items)} offers." if not a.dry_run else "")


if __name__ == "__main__":
    try:
        main()
    except TgError as e:
        sys.exit(f"Telegram error: {e}")
