#!/usr/bin/env python3
"""
Wrapper script to activate the virtual environment and run the auto_blog system.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    # Determine the project root directory
    project_root = Path(__file__).resolve().parent
    venv_dir = project_root / "venv"
    
    # Check if virtual environment exists
    if not venv_dir.exists():
        print("Virtual environment not found. Running setup first...")
        setup_script = project_root / "setup.py"
        if not setup_script.exists():
            print("Error: setup.py script not found.")
            sys.exit(1)
        
        try:
            subprocess.run([sys.executable, str(setup_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running setup: {e}")
            sys.exit(1)
    
    # Determine python executable path based on platform
    is_windows = platform.system() == "Windows"
    bin_dir = "Scripts" if is_windows else "bin"
    python_path = venv_dir / bin_dir / ("python.exe" if is_windows else "python")
    
    # Run the auto_blog system
    print("Running auto_blog system...")
    run_script = project_root / "run_autoblog.py"
    try:
        subprocess.run([str(python_path), str(run_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running auto_blog system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 