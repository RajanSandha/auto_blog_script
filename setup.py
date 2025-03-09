#!/usr/bin/env python3
"""
Setup script for the auto_blog system.
Creates a virtual environment and installs all dependencies.
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

    # Create virtual environment
    print(f"Creating virtual environment at {venv_dir}...")
    try:
        # First attempt to create the virtual environment
        result = subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            # Check if this is a Debian/Ubuntu system with missing venv package
            if "ensurepip is not available" in result.stderr or "No module named 'venv'" in result.stderr:
                # Get Python version
                python_version = platform.python_version().split('.')
                python_major_minor = f"{python_version[0]}.{python_version[1]}"
                
                print("\nError: Cannot create virtual environment.")
                print(f"It looks like you need to install the Python venv package.\n")
                print("On Debian/Ubuntu systems, run one of these commands:")
                print(f"    sudo apt install python3-venv")
                print(f"    sudo apt install python{python_major_minor}-venv")
                
                # Ask if they want to try to install it automatically
                install_choice = input("\nWould you like me to try to install it for you? (y/n): ").strip().lower()
                if install_choice == 'y':
                    try:
                        # Try both package names
                        pkg_names = [f"python{python_major_minor}-venv", "python3-venv"]
                        installed = False
                        
                        for pkg in pkg_names:
                            print(f"\nAttempting to install {pkg}...")
                            sudo_result = subprocess.run(["sudo", "apt", "install", "-y", pkg], 
                                                        capture_output=True, text=True)
                            
                            if sudo_result.returncode == 0:
                                print(f"Successfully installed {pkg}")
                                installed = True
                                break
                            else:
                                print(f"Failed to install {pkg}")
                                if "command not found" in sudo_result.stderr:
                                    print("Sudo is not available or not in PATH")
                                    break
                        
                        if installed:
                            print("\nTrying to create virtual environment again...")
                            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
                            print("Virtual environment created successfully.")
                        else:
                            print("\nFailed to install required packages automatically.")
                            print("Please install the Python venv package manually and run this script again.")
                            sys.exit(1)
                            
                    except Exception as e:
                        print(f"Error during automatic installation: {e}")
                        print("Please install the Python venv package manually and run this script again.")
                        sys.exit(1)
                else:
                    print("\nPlease install the Python venv package manually and run this script again.")
                    sys.exit(1)
            else:
                # Other venv creation error
                print(f"Error creating virtual environment:\n{result.stderr}")
                sys.exit(1)
        else:
            print("Virtual environment created successfully.")
    except Exception as e:
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