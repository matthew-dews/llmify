#!/usr/bin/env bash

# Install poetry if not already installed
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="/root/.local/bin:$PATH"
    # For non-root users
    export PATH="$HOME/.local/bin:$PATH"
fi

# Verify poetry is available
command -v poetry

# Install dependencies
poetry install --no-interaction
