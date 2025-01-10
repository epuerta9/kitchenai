#!/bin/bash

# Ensure the virtual environment path is set correctly
VENV_PATH="/opt/pysetup/.venv"
ACTIVATE_PATH="$VENV_PATH/bin/activate"

# Activate the virtual environment
source $ACTIVATE_PATH

echo "🔍 Capturing additional packages installed inside the dev container..."
# Compare current installed packages with the base container packages
uv pip freeze > /tmp/all-packages.txt

# Find the difference (new packages only)
comm -23 <(sort /tmp/all-packages.txt) <(sort "$VENV_PATH/base-requirements.txt") > /app/kitchenai/dynamic/updated-requirements.txt

# Clean up temporary files
rm /tmp/all-packages.txt

echo "✅ New packages exported to /app/kitchenai/dynamic/updated-requirements.txt"
