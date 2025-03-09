#!/bin/bash
# Activate virtual environment and set up environment for auto_blog
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source "$SCRIPT_DIR/venv/bin/activate"
echo "Virtual environment activated. You can now run:"
echo "    python run_autoblog.py"
echo ""
echo "Or to start a shell in the virtual environment:"
echo "    $SHELL"
