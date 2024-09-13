#!/usr/bin/env bash
set -euo pipefail

python3 -m venv env
source env/bin/activate
python3 -m pip install black mypy

black llmify.py
mypy llmify.py
