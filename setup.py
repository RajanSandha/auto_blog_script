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

    # Create virtual environment - try multiple methods
    print(f"Creating virtual environment at {venv_dir}...")
    
    # Method 1: Try using venv module directly
    try:
        print("Trying to create venv using built-in venv module...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print("Virtual environment created successfully with venv module.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment with venv: {e}")
        print("Trying alternative method...")
        
        # Method 2: Try using virtualenv if available
        try:
            # First check if virtualenv is installed
            try:
                subprocess.run(["virtualenv", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                virtualenv_installed = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                virtualenv_installed = False
                
            if not virtualenv_installed:
                print("virtualenv not found. Attempting to install virtualenv...")
                subprocess.run([sys.executable, "-m", "pip", "install", "virtualenv"], check=True)
                print("virtualenv installed successfully.")
                
            # Create virtual environment using virtualenv
            print("Creating virtual environment using virtualenv...")
            subprocess.run(["virtualenv", str(venv_dir)], check=True)
            print("Virtual environment created successfully with virtualenv.")
        except Exception as ve:
            print(f"Error creating virtual environment with virtualenv: {ve}")
            
            # Method 3: Try creating it manually
            try:
                print("Trying to create venv structure manually...")
                os.makedirs(venv_dir, exist_ok=True)
                bin_dir = venv_dir / ('Scripts' if platform.system() == 'Windows' else 'bin')
                os.makedirs(bin_dir, exist_ok=True)
                
                # Create a symbolic link to python or copy the python executable
                python_exec = sys.executable
                print(f"Using Python executable from: {python_exec}")
                
                if platform.system() == 'Windows':
                    target_python = bin_dir / 'python.exe'
                    # On Windows, copy the Python executable
                    shutil.copy(python_exec, target_python)
                else:
                    target_python = bin_dir / 'python'
                    # On Unix, create a symbolic link
                    if not target_python.exists():
                        os.symlink(python_exec, target_python)
                        
                # Create python3 symlink on Unix systems
                if platform.system() != 'Windows':
                    target_python3 = bin_dir / 'python3'
                    if not target_python3.exists():
                        os.symlink(python_exec, target_python3)
                
                print("Created virtual environment structure manually.")
                
                # Install pip in the virtual environment
                print("Installing pip in the virtual environment...")
                get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
                get_pip_script = venv_dir / "get-pip.py"
                
                # Download get-pip.py
                import urllib.request
                urllib.request.urlretrieve(get_pip_url, get_pip_script)
                
                # Run get-pip.py with the virtual environment's Python
                subprocess.run([str(target_python), str(get_pip_script)], check=True)
                
                print("pip installed in the virtual environment.")
                
            except Exception as me:
                print(f"Error creating virtual environment manually: {me}")
                print("\nTips to resolve this issue:")
                print("1. Try installing virtualenv: pip install virtualenv")
                print("2. Try using the alternative setup script: ./setup_alt.py")
                print("3. Create a virtual environment manually:")
                print("   python -m venv venv  # or")
                print("   virtualenv venv")
                print("4. Check your Python installation for any issues")
                sys.exit(1)
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
        try:
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            print("Upgraded pip successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not upgrade pip: {e}")
            print("Continuing with existing pip version...")
        
        # Then install requirements
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    
    # Clone al-folio repository
    github_repo_dir = project_root / "github_repo"
    if not github_repo_dir.exists():
        print("\nCloning al-folio Jekyll theme repository...")
        try:
            import git
            git.Repo.clone_from("https://github.com/alshedivat/al-folio.git", str(github_repo_dir))
            print("Successfully cloned al-folio repository.")
            
            # Remove .git directory to disconnect from original repository
            git_dir = github_repo_dir / ".git"
            if git_dir.exists():
                import shutil
                shutil.rmtree(git_dir)
                print("Removed .git directory from the cloned repository.")
        except Exception as e:
            print(f"Error cloning al-folio repository: {e}")
            print("You'll need to clone it manually after completing setup:")
            print("  git clone https://github.com/alshedivat/al-folio.git github_repo")
            print("  rm -rf github_repo/.git")
    else:
        print(f"\nFound existing directory at {github_repo_dir}")
        print("Skipping al-folio repository cloning.")
    
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
    
    # Print al-folio specific instructions
    print("\nAl-Folio Theme Setup:")
    print("1. Edit the _config.yml file in the github_repo directory")
    print("2. Run the system with ./run.py to generate posts")
    print("3. Posts will be added to the _posts directory in the al-folio theme")

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