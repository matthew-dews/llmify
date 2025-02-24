#!/usr/bin/env bash

# Set poetry path
POETRY_PATH="$HOME/.local/bin/poetry"
if [ -f "/root/.local/bin/poetry" ]; then
    POETRY_PATH="/root/.local/bin/poetry"
fi

# Format with black
"$POETRY_PATH" run black .

# Type check only changed files with mypy
CHANGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.py$' || true)
if [ -n "$CHANGED_PY_FILES" ]; then
    "$POETRY_PATH" run mypy $CHANGED_PY_FILES
fi

# Run tests since they're not in CI
"$POETRY_PATH" run pytest
