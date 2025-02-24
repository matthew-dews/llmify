#!/usr/bin/env bash

# Set poetry path
POETRY_PATH="$HOME/.local/bin/poetry"
if [ -f "/root/.local/bin/poetry" ]; then
    POETRY_PATH="/root/.local/bin/poetry"
fi

# Format with black
"$POETRY_PATH" run black .

# Type check with mypy
"$POETRY_PATH" run mypy .

# Run tests since they're not in CI
"$POETRY_PATH" run pytest
