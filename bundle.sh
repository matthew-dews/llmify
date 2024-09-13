#!/usr/bin/env bash
set -euo pipefail

python3 -m venv env
source env/bin/activate
python3 -m pip install wheel pyinstaller

pyinstaller --onefile llmify.py
