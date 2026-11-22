# Delhaize Tracker

<p align="center">
  <img src="Radar%20Lion%20Emblem.png" alt="Delhaize Tracker logo" width="220">
</p>

<p align="center">
  <strong>Your Delhaize favourites, only when they're on offer.</strong><br>
  <a href="https://gabnasello.github.io/delhaize-promo-tracker/">Open the live tracker</a>
</p>

Every Thursday morning a GitHub Action checks your saved Delhaize favourites and publishes a small page
(GitHub Pages) with **only the favourites that are on offer**, with image, offer text and end date.

## Privacy design
- The repo is public (needed for free GitHub Pages) but contains **no personal data**: your favorites live in the
  encrypted Actions secret `FAVORITES_CSV` (compressed copy of the CSV); `data/favorites.csv` and saved pages are git-ignored.
- The published page and `promos.json` show only products currently on offer: no full favorites list, no list names.
- Action logs print no product names or links. The page has `noindex`; it is still reachable by anyone with the URL.
- Uploading through the GitHub web UI ignores `.gitignore`: never drag `data/favorites.csv` or `saved_pages/` there.

## 1. Build your favorites file (local)
1. On delhaize.be open one favorites list, **scroll to the bottom**, save the page (Ctrl+S, "Webpage, Complete").
   Put the `.htm` files in `saved_pages/` (the list page itself, not the overview "Mijn boodschappenlijsten").
2. Convert (isolated `.venv`, system Python untouched):
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\\setup.ps1     # once
   powershell -ExecutionPolicy Bypass -File .\\extract.ps1
   ```
   (Mac/Linux: `./setup.sh`, `./extract.sh`.) This creates `data/favorites.csv` and `data/favorites_secret.txt` (a compressed copy for the GitHub secret). Alternatively attach the `.htm` files
   to an AI such as Claude with the prompt in `tools/ai_prompt.md`.
`data/favorites.example.csv` shows the format.

## 2. Test locally
```powershell
powershell -ExecutionPolicy Bypass -File .\\test_local.ps1 5            # first 5 products
powershell -ExecutionPolicy Bypass -File .\\test_local.ps1 -Only "zoete aardappel"
```
Runs the same checker as the Action, then serves http://localhost:8000. Full results (incl. non-offers and errors)
are in `checker/last_run_full.json`; page HTML in `checker/debug/` (both git-ignored).

## 3. Publish on GitHub
See `SETUP_WITH_CHATGPT.md`, or by hand:
1. Create a public repo and upload the project (without `data/favorites.csv`).
2. Settings > Secrets and variables > Actions > New repository secret: `FAVORITES_CSV` = full content of `data/favorites_secret.txt` (the raw CSV is usually over GitHub's 48 KB secret limit, so it is compressed).
3. Settings > Pages > Build and deployment > Source: **GitHub Actions**.
4. Actions tab > "Weekly promo check" > Run workflow (manual test). The page URL appears in the run summary.
5. After that it runs by itself every Thursday (cron in `.github/workflows/weekly-promos.yml`).
GitHub disables scheduled workflows in a public repo after 60 days without repository activity; the weekly
commit of `docs/promos.json` normally prevents that. If it happens, re-enable it in the Actions tab.
