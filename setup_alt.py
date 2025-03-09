#!/usr/bin/env python3
"""
Alternative setup script for the auto_blog system.
Uses virtualenv instead of venv to create a virtual environment.
Use this if you have issues with the regular setup.py script.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def main():
    # Determine the project root directory
    project_root = Path(__file__).resolve().parent
    venv_dir = project_root / "venv"
    
    # Check if virtual environment already exists
    if venv_dir.exists():
        print(f"Virtual environment already exists at {venv_dir}")
        choice = input("Do you want to recreate it? (y/n): ").strip().lower()
        if choice == 'y':
            print(f"Removing existing virtual environment...")
            shutil.rmtree(venv_dir)
        else:
            print("Using existing virtual environment.")
            activate_and_setup(project_root, venv_dir)
            return

    # Check for virtualenv command
    print("Checking for virtualenv...")
    try:
        # Try to run virtualenv to see if it's installed
        result = subprocess.run(["virtualenv", "--version"], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("virtualenv is not installed. Trying to install it...")
            
            # Try to install virtualenv
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "virtualenv"], check=True)
                print("virtualenv installed successfully.")
            except subprocess.CalledProcessError:
                print("Could not install virtualenv with pip.")
                print("Please install virtualenv manually:")
                print("    pip install virtualenv")
                print("Or on Debian/Ubuntu:")
                print("    sudo apt install python3-virtualenv")
                sys.exit(1)
        else:
            print(f"Found virtualenv version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("virtualenv command not found. Trying to install it...")
        
        # Try to install virtualenv
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "virtualenv"], check=True)
            print("virtualenv installed successfully.")
        except subprocess.CalledProcessError:
            print("Could not install virtualenv with pip.")
            print("Please install virtualenv manually:")
            print("    pip install virtualenv")
            print("Or on Debian/Ubuntu:")
            print("    sudo apt install python3-virtualenv")
            sys.exit(1)
    
    # Create virtual environment using virtualenv
    print(f"Creating virtual environment at {venv_dir} using virtualenv...")
    try:
        # Use either the virtualenv command or the module
        try:
            subprocess.run(["virtualenv", str(venv_dir)], check=True)
        except FileNotFoundError:
            # Fall back to using the module if command not found
            subprocess.run([sys.executable, "-m", "virtualenv", str(venv_dir)], check=True)
            
        print("Virtual environment created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)
    
    activate_and_setup(project_root, venv_dir)

def activate_and_setup(project_root, venv_dir):
    # Determine pip and python executable paths based on platform
    is_windows = platform.system() == "Windows"
    bin_dir = "Scripts" if is_windows else "bin"
    python_path = venv_dir / bin_dir / ("python.exe" if is_windows else "python")
    pip_path = venv_dir / bin_dir / ("pip.exe" if is_windows else "pip")
    
    # Check if the virtual environment is properly created
    if not python_path.exists():
        print(f"Error: Python executable not found in the virtual environment at {python_path}")
        print("The virtual environment may not have been created correctly.")
        sys.exit(1)
    
    # Install dependencies
    print("Installing dependencies...")
    requirements_file = project_root / "requirements.txt"
    try:
        # First upgrade pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # Then install requirements
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    
    # Create activation scripts
    create_activation_scripts(project_root, venv_dir)
    
    print("\nSetup completed successfully!")
    print("\nTo activate the virtual environment:")
    if is_windows:
        print("    run_blog.bat")
    else:
        print("    source ./run_blog.sh")
    print("\nTo run the auto blog system once the environment is activated:")
    print("    python run_autoblog.py")
    print("\nOr use the all-in-one run script:")
    if is_windows:
        print("    python run.py")
    else:
        print("    ./run.py")
    
def create_activation_scripts(project_root, venv_dir):
    """Create scripts to activate the virtual environment on different platforms."""
    
    # Create bash activation script (for Linux/Mac)
    bash_script = project_root / "run_blog.sh"
    with open(bash_script, 'w') as f:
        f.write(f"""#!/bin/bash
# Activate virtual environment and set up environment for auto_blog
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"
source "$SCRIPT_DIR/venv/bin/activate"
echo "Virtual environment activated. You can now run:"
echo "    python run_autoblog.py"
echo ""
echo "Or to start a shell in the virtual environment:"
echo "    $SHELL"
""")
    
    # Make the bash script executable
    os.chmod(bash_script, 0o755)
    
    # Create batch script (for Windows)
    bat_script = project_root / "run_blog.bat"
    with open(bat_script, 'w') as f:
        f.write(f"""@echo off
:: Activate virtual environment and set up environment for auto_blog
set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%venv\\Scripts\\activate.bat"
echo Virtual environment activated. You can now run:
echo     python run_autoblog.py
echo.
echo Or to start a command prompt in the virtual environment:
echo     cmd
""")

if __name__ == "__main__":
    main() 