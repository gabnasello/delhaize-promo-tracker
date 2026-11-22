#!/usr/bin/env bash
# Isolated environment in ./.venv (system Python untouched)
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
echo "Done."
