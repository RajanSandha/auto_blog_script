#!/bin/bash
# Activate virtual environment and run the auto_blog system

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
source "${SCRIPT_DIR}/venv/bin/activate"

# Run the auto_blog system
python "${SCRIPT_DIR}/run.py" "$@"
