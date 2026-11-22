#!/usr/bin/env bash
# Same steps as the GitHub Action, locally. Usage: ./test_local.sh [N] ["name1,name2"]
set -e
cd "$(dirname "$0")"
[ -d .venv ] || ./setup.sh
LIMIT="${1:-0}" ONLY="${2:-}" DEBUG=1 .venv/bin/python checker/check_promos.py
echo "Preview: http://localhost:8000  (Ctrl+C to stop)"
cd docs && ../.venv/bin/python -m http.server 8000
