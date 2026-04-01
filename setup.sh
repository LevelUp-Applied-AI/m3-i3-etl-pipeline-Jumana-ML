#!/usr/bin/env bash
set -euo pipefail

# Initialize virtual environment
python -m venv .venv

# Activate and install dependencies
# Works for Git Bash on Windows
source .venv/Scripts/activate
pip install -r requirements.txt

echo "--------------------------------"
echo "Setup complete!"