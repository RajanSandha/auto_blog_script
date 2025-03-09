#!/usr/bin/env python3
"""
Script to fix the virtual environment and reinstall dependencies.
This script will completely remove the existing virtual environment
and recreate it with the correct dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("===== Auto-Blog Environment Fixer =====")
    print("This will remove the existing virtual environment and create a new one.")
    confirmation = input("Do you want to continue? (y/n): ").strip().lower()
    
    if confirmation != 'y':
        print("Operation cancelled.")
        return
    
    project_root = Path(__file__).resolve().parent
    venv_dir = project_root / "venv"
    
    # Remove existing venv
    if venv_dir.exists():
        print(f"Removing existing virtual environment at {venv_dir}...")
        shutil.rmtree(venv_dir)
        print("Virtual environment removed.")
    
    # Try setup_alt.py first as it tends to be more reliable
    print("\nAttempting to set up the environment using setup_alt.py...")
    setup_alt = project_root / "setup_alt.py"
    
    try:
        subprocess.run([sys.executable, str(setup_alt)], check=True)
        print("\nVirtual environment successfully created using setup_alt.py!")
        print("You should now be able to run the system using:")
        print("./run.py")
        return
    except subprocess.CalledProcessError:
        print("\nFailed to set up using setup_alt.py. Trying setup.py...")
    
    # Fall back to setup.py
    setup_script = project_root / "setup.py"
    try:
        subprocess.run([sys.executable, str(setup_script)], check=True)
        print("\nVirtual environment successfully created using setup.py!")
        print("You should now be able to run the system using:")
        print("./run.py")
    except subprocess.CalledProcessError:
        print("\nBoth setup scripts failed.")
        print("Please try the manual setup process described in the README.md:")
        print("1. Install virtualenv: pip install virtualenv")
        print("2. Create a virtual environment: virtualenv venv")
        print("3. Activate the environment and install dependencies")

if __name__ == "__main__":
    main() 