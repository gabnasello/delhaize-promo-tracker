# Setup prompt for ChatGPT (paste it together with the link to this repo)

I created this GitHub repo: <PASTE LINK>. It is a weekly "Delhaize favorites on offer" tracker: the GitHub Actions
workflow `.github/workflows/weekly-promos.yml` reads my private favorites from the Actions secret `FAVORITES_CSV`,
checks each product page on delhaize.be, and deploys a small GitHub Pages site (`docs/`) listing only the favorites
that are on offer. Read README.md and the workflow first, then help me bring it live, one step at a time:

1. Review: check the workflow (YAML, cron, permissions), and that the repo contains no personal data (no
   favorites.csv, no .htm saved pages, no names, addresses or emails). Fix problems with a commit. Never add my
   real favorites, saved pages or secrets to the repo, to commits, or to logs.
2. Do whatever your GitHub access allows. For anything it does not (secrets, Pages settings, clicking Run workflow),
   give me the exact click path and wait for my "done":
   a. Settings > Secrets and variables > Actions > New repository secret: name FAVORITES_CSV, value = the full
      content of my local favorites.csv (I paste it myself; do not ask me to share it with you).
   b. Settings > Pages > Build and deployment > Source = GitHub Actions.
   c. Actions tab > "Weekly promo check" > Run workflow (manual run first).
3. Read the manual run's result. If it fails, diagnose from the logs (they intentionally show no product names) and
   propose a fix as a commit. Typical causes: missing secret, Pages not enabled, delhaize.be blocking GitHub's
   servers (all products fail), playwright install errors.
4. When the manual run succeeds, open the Pages URL, confirm it loads and shows a "checked" date, and tell me the URL.
5. Confirm the automatic schedule: cron "0 5 * * 4" (every Thursday 05:00 UTC = 06:00/07:00 Belgian time), workflow on
   the default branch, Actions enabled. Tell me when the next run is expected, and remind me that GitHub may disable
   scheduled workflows after 60 days without repository activity and how to re-enable them.
Keep answers short and do not change anything outside this scope without asking me.
