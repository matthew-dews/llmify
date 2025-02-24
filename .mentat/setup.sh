#!/usr/bin/env bash

# Install poetry if not already installed
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Set poetry path
POETRY_PATH="$HOME/.local/bin/poetry"
if [ -f "/root/.local/bin/poetry" ]; then
    POETRY_PATH="/root/.local/bin/poetry"
fi

# Verify poetry is available
"$POETRY_PATH" --version

# Install dependencies
"$POETRY_PATH" install --no-interaction
