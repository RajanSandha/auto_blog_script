#!/bin/bash
# Activation script for the auto_blog virtual environment

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment
source "/var/www/html/github/auto_blog_script/venv/bin/activate"

# Inform the user
echo "Virtual environment activated. Run 'python run_autoblog.py' to start the system."
