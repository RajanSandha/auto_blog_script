#!/usr/bin/env python3
"""
Alternative setup script for the auto_blog system.
Uses multiple fallback methods for creating a virtual environment.
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

    # Check if virtualenv is installed
    virtualenv_installed = False
    print("Checking for virtualenv...")
    try:
        subprocess.run(["virtualenv", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        virtualenv_installed = True
        print("virtualenv is installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("virtualenv is not installed.")

    # Try to install virtualenv if not installed
    if not virtualenv_installed:
        print("Attempting to install virtualenv...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "virtualenv"], check=True)
            virtualenv_installed = True
            print("virtualenv installed successfully.")
        except subprocess.CalledProcessError:
            print("Failed to install virtualenv with pip.")
            print("Continuing with alternative methods...")

    # Method 1: Create virtual environment using virtualenv command
    print(f"Creating virtual environment at {venv_dir}...")
    venv_created = False
    
    if virtualenv_installed:
        try:
            print("Creating virtual environment using virtualenv command...")
            subprocess.run(["virtualenv", str(venv_dir)], check=True)
            print("Virtual environment created successfully with virtualenv command.")
            venv_created = True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment with virtualenv command: {e}")
    
    # Method 2: Create virtual environment using virtualenv module
    if not venv_created:
        try:
            print("Trying to create virtual environment using virtualenv module...")
            subprocess.run([sys.executable, "-m", "virtualenv", str(venv_dir)], check=True)
            print("Virtual environment created successfully with virtualenv module.")
            venv_created = True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment with virtualenv module: {e}")
    
    # Method 3: Create virtual environment using venv module
    if not venv_created:
        try:
            print("Trying to create virtual environment using built-in venv module...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            print("Virtual environment created successfully with venv module.")
            venv_created = True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment with venv module: {e}")
    
    # Method 4: Create virtual environment structure manually
    if not venv_created:
        try:
            print("Trying to create virtual environment structure manually...")
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
            venv_created = True
            
        except Exception as me:
            print(f"Error creating virtual environment manually: {me}")
    
    if not venv_created:
        print("\nFailed to create virtual environment with all methods.")
        print("Tips for resolving this issue:")
        print("1. Ensure you have permission to write to the directory")
        print("2. Check your Python installation (Python 3.6+ is required)")
        print("3. Try installing Python venv package manually:")
        print("   sudo apt-get install python3-venv  # Debian/Ubuntu")
        print("4. Create a virtual environment manually and activate it:")
        print("   python -m venv venv  # or")
        print("   virtualenv venv")
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
        python_path_str = str(python_path)
        print(f"Warning: Expected Python executable not found at {python_path_str}")
        
        # Try to find the actual Python executable in the bin directory
        if is_windows:
            potential_paths = list(bin_dir.glob("python*.exe"))
        else:
            potential_paths = list(bin_dir.glob("python*"))
            
        if potential_paths:
            python_path = potential_paths[0]
            print(f"Found alternative Python executable at {python_path}")
        else:
            print("No Python executable found in the virtual environment.")
            print("The virtual environment may not have been created correctly.")
            sys.exit(1)
    
    # Install dependencies
    print("Installing dependencies...")
    requirements_file = project_root / "requirements.txt"
    try:
        # First try to upgrade pip
        try:
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            print("Upgraded pip successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not upgrade pip: {e}")
            print("Continuing with existing pip version...")
        
        # Then install requirements
        try:
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies with pip: {e}")
            print("Trying an alternative approach...")
            
            # Try installing packages one by one
            with open(requirements_file, 'r') as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            for package in packages:
                try:
                    print(f"Installing {package}...")
                    subprocess.run([str(pip_path), "install", package], check=True)
                except subprocess.CalledProcessError as pe:
                    print(f"Warning: Failed to install {package}: {pe}")
            
            print("Finished installing dependencies.")
            
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    
    # Clone al-folio repository
    github_repo_dir = project_root / "github_repo"
    if not github_repo_dir.exists():
        print("\nCloning al-folio Jekyll theme repository...")
        try:
            try:
                import git
            except ImportError:
                print("GitPython not installed. Installing it now...")
                subprocess.run([str(pip_path), "install", "GitPython"], check=True)
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