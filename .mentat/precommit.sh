#!/usr/bin/env bash

# Format with black
poetry run black .

# Type check with mypy
poetry run mypy .

# Run tests since they're not in CI
poetry run pytest
