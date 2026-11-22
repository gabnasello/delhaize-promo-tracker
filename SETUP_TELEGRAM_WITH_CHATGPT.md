# Setup prompt for ChatGPT: Telegram notifications (paste it together with the link to this repo)

My repo: <PASTE LINK>. The weekly "Delhaize favorites on offer" tracker already works (workflow "Weekly promo check",
Pages site). I added Telegram notifications: `.github/workflows/telegram-notify.yml`, `notify/telegram_notify.py`,
`notify/template.toml`, `TELEGRAM.md`. The notify workflow runs after every "Weekly promo check" (workflow_run) and
can be started manually; it reads docs/promos.json and posts a header message plus one photo message per offer.
Read these files first, then help me one step at a time:

1. Review the new files: YAML validity, that workflow_run references the exact name "Weekly promo check", permissions,
   and that nothing prints product names, the bot token or the chat ID in logs. Never ask me for the token or chat ID,
   and never put them in a file, commit or chat. Fix problems with a commit.
2. Give me the click path for what your access can't do, and wait for my "done": Settings > Secrets and variables >
   Actions > New repository secret `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (I paste them myself); optionally the
   variable `SITE_URL`. Remind me the bot must be a member of the group.
3. Manual test: Actions > "Telegram notification" > Run workflow (it uses the latest docs/promos.json from the last
   weekly run). Read the run result. If it failed, diagnose from the log and propose a fix. Typical causes: missing
   secret, wrong chat ID (groups start with "-", supergroups "-100"), bot not in the group, "chat not found",
   Python version. Ask me whether the messages arrived and how they look.
4. If I want a different message, edit only notify/template.toml (Telegram HTML; lines with empty placeholders vanish)
   and commit it; then re-run the manual test.
5. Confirm the chaining: after the next run of "Weekly promo check" (scheduled Thursday, or a manual run now), the
   "Telegram notification" workflow starts by itself. Both workflow files must be on the default branch. Tell me what
   to check in the Actions tab to verify it.
Keep answers short and do not change anything outside this scope without asking me.
