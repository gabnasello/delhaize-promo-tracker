# Telegram notifications

A second workflow (`.github/workflows/telegram-notify.yml`) sends a summary of the offers to a Telegram chat or group:
a header message with a link to the website, then one photo message per product (offer, price, end date, link).
It runs automatically after every "Weekly promo check" (and can be started manually).

## Setup (once)
1. Add repository secrets (Settings > Secrets and variables > Actions): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
   (group IDs start with `-`; supergroups with `-100`). Never put them in a file or in a chat.
2. Optional: Variables tab > `SITE_URL` (default `https://<owner>.github.io/<repo>/`).
3. Make sure the bot is a member of the group (and has sent/received at least one message there).
4. Test: Actions > "Telegram notification" > Run workflow. It sends the results of the latest weekly check.

## Change the message
Edit `notify/template.toml` (Telegram HTML; lines with an empty placeholder disappear). Preview locally:
```powershell
.\.venv\Scripts\python.exe notify\telegram_notify.py --dry-run --sample    # fake data
.\.venv\Scripts\python.exe notify\telegram_notify.py --dry-run              # your latest docs\promos.json
```
Python 3.11+ is needed locally (the Action uses 3.12). Logs show only counts, never product names.
