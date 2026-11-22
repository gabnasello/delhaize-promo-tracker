#!/usr/bin/env bash
# Turns saved Delhaize list pages (.htm) in saved_pages/ into data/favorites.csv
cd "$(dirname "$0")"
.venv/bin/python tools/html_to_csv.py "${1:-saved_pages}"
