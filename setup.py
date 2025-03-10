#!/usr/bin/env python3
"""
Setup script for the auto_blog system.
Creates a virtual environment and installs all dependencies.
Clones the minimal-mistakes Jekyll theme for GitHub Pages.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import urllib.request

# Check Python version
if sys.version_info < (3, 6):
    print("Error: This script requires Python 3.6 or higher.")
    print(f"Current Python version: {sys.version}")
    sys.exit(1)

def check_venv_module():
    """Check if the venv module is available."""
    try:
        import venv
        return True
    except ImportError:
        return False

def main():
    # Determine the project root directory
    project_root = Path(__file__).resolve().parent
    venv_dir = project_root / "venv"
    
    # Detect system and Python details for logging
    system_info = f"System: {platform.system()} {platform.release()}"
    python_info = f"Python: {platform.python_version()} at {sys.executable}"
    print(f"\nSystem Information:")
    print(f"  {system_info}")
    print(f"  {python_info}")
    print(f"  venv module available: {check_venv_module()}\n")
    
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
        # Get the Python major and minor version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"Using Python version: {python_version}")
        
        # Check for specific Python version
        python3_path = f"/usr/bin/python{python_version}"
        if os.path.exists(python3_path):
            print(f"Found Python at {python3_path}, using it to create venv")
            subprocess.run([python3_path, "-m", "venv", str(venv_dir)], check=True)
        else:
            # Use system executable
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print("Virtual environment created successfully with venv module.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
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
            
            # If not installed, try to install it
            if not virtualenv_installed:
                print("Installing virtualenv...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "virtualenv"], check=True)
                    virtualenv_installed = True
                except subprocess.CalledProcessError as pip_error:
                    print(f"Error installing virtualenv: {pip_error}")
                    virtualenv_installed = False
            
            # Use virtualenv if installed
            if virtualenv_installed:
                print("Trying to create venv using virtualenv...")
                try:
                    subprocess.run(["virtualenv", str(venv_dir)], check=True)
                    print("Virtual environment created successfully with virtualenv.")
                except subprocess.CalledProcessError as ve_error:
                    print(f"Error creating virtual environment with virtualenv: {ve_error}")
                    raise
            else:
                raise RuntimeError("virtualenv is not available")
                
        except Exception as alt_error:
            print(f"Error with alternative method: {alt_error}")
            print("Trying method 3: direct virtualenv command...")
            
            # Method 3: Try using direct virtualenv command
            try:
                virtualenv_paths = [
                    "virtualenv",
                    "/usr/local/bin/virtualenv",
                    "/usr/bin/virtualenv",
                    f"{os.path.dirname(sys.executable)}/virtualenv"
                ]
                
                for virtualenv_path in virtualenv_paths:
                    try:
                        print(f"Trying virtualenv at {virtualenv_path}...")
                        subprocess.run([virtualenv_path, str(venv_dir)], check=True)
                        print(f"Virtual environment created successfully with {virtualenv_path}")
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:  # This runs if the loop completes without breaking
                    raise RuntimeError("All virtualenv paths failed")
                    
            except Exception as direct_ve_error:
                print(f"Error with direct virtualenv command: {direct_ve_error}")
                print("Trying method 4: create manually...")
                
                # Method 4: Try creating it manually
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
                        # Get the actual executable name that should be used for python3
                        python_exec = sys.executable
                        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
                        
                        # Try finding the Python executable at various possible locations
                        potential_pythons = [
                            python_exec,
                            f"/usr/bin/python{python_version}",
                            "/usr/bin/python3",
                            f"/usr/local/bin/python{python_version}",
                            "/usr/local/bin/python3"
                        ]
                        
                        print(f"Looking for Python executable at possible locations...")
                        python_found = None
                        for potential_python in potential_pythons:
                            if os.path.exists(potential_python):
                                python_found = potential_python
                                print(f"Using Python from: {python_found}")
                                break
                        
                        if python_found:
                            target_python = bin_dir / 'python'
                            target_python3 = bin_dir / 'python3'
                            
                            # Create symlinks for both python and python3
                            if not target_python.exists():
                                print(f"Creating symlink from {python_found} to {target_python}")
                                os.symlink(python_found, target_python)
                                
                            if not target_python3.exists():
                                print(f"Creating symlink from {python_found} to {target_python3}")
                                os.symlink(python_found, target_python3)
                        else:
                            print("Warning: Could not find a suitable Python executable for symlinks")
                            print("Attempting to copy the system executable instead")
                            
                            # Last resort: Try to copy the executable
                            try:
                                shutil.copy(sys.executable, bin_dir / 'python')
                                shutil.copy(sys.executable, bin_dir / 'python3')
                            except Exception as copy_error:
                                print(f"Error copying Python executable: {copy_error}")
                                print("You may need to manually create the Python symlinks")
                    
                    print("Created virtual environment structure manually.")
                    
                    # Install pip in the virtual environment
                    print("Installing pip in the virtual environment...")
                    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
                    get_pip_script = venv_dir / "get-pip.py"
                    
                    # Download get-pip.py
                    urllib.request.urlretrieve(get_pip_url, get_pip_script)
                    
                    # Run get-pip.py with the virtual environment's Python
                    subprocess.run([str(target_python), str(get_pip_script)], check=True)
                    
                    print("Successfully installed pip in the virtual environment.")
                    
                except Exception as manual_error:
                    print(f"Error creating virtual environment manually: {manual_error}")
                    print("\nVirtual environment creation failed through all methods.")
                    print("\n" + "="*80)
                    print("TROUBLESHOOTING GUIDE")
                    print("="*80)
                    print("1. Install the Python venv module on your system:")
                    print("   - For Debian/Ubuntu: sudo apt-get install python3-venv")
                    print("   - For Red Hat/Fedora: sudo dnf install python3-libs")
                    print("   - For Arch Linux: pacman -S python-virtualenv")
                    print("\n2. Try installing virtualenv and running it directly:")
                    print("   pip install virtualenv")
                    print("   virtualenv venv")
                    print("\n3. If you continue to have issues, create the virtual environment manually:")
                    print("   python3 -m venv venv")
                    print("   # OR")
                    print("   virtualenv venv")
                    print("\n4. Then install dependencies manually:")
                    print("   venv/bin/pip install -r requirements.txt  # On Linux/Mac")
                    print("   venv\\Scripts\\pip install -r requirements.txt  # On Windows")
                    print("\n5. You can also try with the system Python directly:")
                    print(f"   {sys.executable} -m pip install -r requirements.txt")
                    print("\nError details:")
                    print(f"   {manual_error}")
                    print("="*80)
                    sys.exit(1)
    
    # Create activation scripts for convenience
    create_activation_scripts(project_root, venv_dir)
    
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
        print("\nFailed to install dependencies. You can try installing them manually:")
        print(f"  {pip_path} install -r {requirements_file}")
        print("\nOr install packages one by one if you encounter issues with specific packages.")
        print("Sometimes, installing with the --no-cache-dir option can help:")
        print(f"  {pip_path} install --no-cache-dir -r {requirements_file}")
        sys.exit(1)
    
    # Clone minimal-mistakes repository
    github_repo_dir = project_root / "github_repo"
    if not github_repo_dir.exists():
        print("\nCloning minimal-mistakes Jekyll theme repository...")
        try:
            # Use subprocess to call git directly instead of GitPython
            print("Using system git to clone repository...")
            
            # First check if git is available
            try:
                subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                git_available = True
            except (subprocess.CalledProcessError, FileNotFoundError) as git_check_err:
                git_available = False
                print(f"Git not available or not in PATH: {git_check_err}")
            
            if git_available:
                # Clone the repository using git directly
                subprocess.run(["git", "clone", "https://github.com/mmistakes/minimal-mistakes.git", str(github_repo_dir)], check=True)
                print("Successfully cloned minimal-mistakes repository.")
                
                # Remove .git directory to disconnect from original repository
                git_dir = github_repo_dir / ".git"
                if git_dir.exists():
                    shutil.rmtree(git_dir)
                    print("Removed .git directory from the cloned repository.")
                
                # Initialize new git repository
                subprocess.run(["git", "init"], cwd=str(github_repo_dir), check=True)
                print("Initialized new git repository.")
            else:
                print("Git not available. Attempting to download ZIP file instead...")
                try:
                    # Download ZIP file directly
                    zip_url = "https://github.com/mmistakes/minimal-mistakes/archive/refs/heads/master.zip"
                    zip_path = project_root / "minimal-mistakes.zip"
                    print(f"Downloading {zip_url}...")
                    
                    urllib.request.urlretrieve(zip_url, zip_path)
                    print("Download complete. Extracting...")
                    
                    # Extract ZIP file
                    import zipfile
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        # Extract to a temporary directory
                        temp_dir = project_root / "temp_extract"
                        zip_ref.extractall(temp_dir)
                    
                    # Rename the extracted directory
                    extracted_dir = temp_dir / "minimal-mistakes-master"
                    if extracted_dir.exists():
                        # If github_repo_dir exists as a file (unlikely but possible), remove it
                        if github_repo_dir.exists() and not github_repo_dir.is_dir():
                            github_repo_dir.unlink()
                            
                        # Move the extracted directory to github_repo_dir
                        if not github_repo_dir.exists():
                            shutil.move(str(extracted_dir), str(github_repo_dir))
                    
                    # Clean up
                    if zip_path.exists():
                        zip_path.unlink()
                    if temp_dir.exists() and temp_dir.is_dir():
                        shutil.rmtree(temp_dir)
                        
                    print("Successfully extracted minimal-mistakes theme.")
                except Exception as zip_error:
                    print(f"Error downloading/extracting ZIP file: {zip_error}")
                    raise RuntimeError("Could not clone or download the repository. Check your internet connection.")
            
            # Setup minimal-mistakes theme for use with GitHub Pages
            print("\nSetting up minimal-mistakes theme for GitHub Pages...")
            
            # Remove directories and files not needed for GitHub Pages
            print("Removing files and directories not needed for GitHub Pages...")
            items_to_remove = [
                ".editorconfig", ".gitattributes", ".github", "docs",
                "test", "CHANGELOG.md", "minimal-mistakes-jekyll.gemspec",
                "README.md", "screenshot.png", "screenshot-layouts.png", ".travis.yml"
            ]
            
            for item in items_to_remove:
                item_path = github_repo_dir / item
                if item_path.exists():
                    if item_path.is_dir():
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            
            print("Creating necessary directories for blog posts and images...")
            # Ensure _posts directory exists
            posts_dir = github_repo_dir / "_posts"
            posts_dir.mkdir(exist_ok=True)
            
            # Ensure assets/images directory exists for post images
            images_dir = github_repo_dir / "assets" / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            
            print("Setting up sample _config.yml file...")
            # Copy starter _config.yml if it doesn't exist
            config_yml = github_repo_dir / "_config.yml"
            starter_config = github_repo_dir / "_config.yml"
            
            if not config_yml.exists() and starter_config.exists():
                shutil.copy(str(starter_config), str(config_yml))
                
            print("Setup of minimal-mistakes theme completed successfully!")
            
        except Exception as e:
            print(f"\nError setting up minimal-mistakes repository: {e}")
            print("\n" + "="*80)
            print("MANUAL REPOSITORY SETUP INSTRUCTIONS")
            print("="*80)
            print("You can set up the repository manually by following these steps:")
            print("\nOption 1: Using Git")
            print("1. Clone the minimal-mistakes repository:")
            print("   git clone https://github.com/mmistakes/minimal-mistakes.git github_repo")
            print("2. Remove the .git directory from the cloned repository:")
            print("   rm -rf github_repo/.git")
            print("3. Initialize a new git repository:")
            print("   cd github_repo")
            print("   git init")
            
            print("\nOption 2: Download ZIP File")
            print("1. Download the ZIP file from:")
            print("   https://github.com/mmistakes/minimal-mistakes/archive/refs/heads/master.zip")
            print("2. Extract the ZIP file and rename the directory to github_repo")

            print("\nOption 3: Use the included manual_clone.sh script (Linux/Mac only):")
            print("   chmod +x manual_clone.sh")
            print("   ./manual_clone.sh")
            
            print("\nAfter setup:")
            print("1. Create the following directories if they don't exist:")
            print("   mkdir -p github_repo/_posts github_repo/assets/images")
            print("2. Follow the minimal-mistakes setup documentation:")
            print("   https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/")
            print("="*80)
    else:
        print(f"\ngithub_repo directory already exists at {github_repo_dir}")
        print("Using existing repository.")
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with your GitHub credentials")
    print("2. Run the system with: ./run.py")

def create_activation_scripts(project_root, venv_dir):
    """Create convenience scripts to activate the virtual environment."""
    print("Creating activation scripts...")
    
    # Create run_blog.sh for Unix-like systems
    run_script_sh = project_root / "run_blog.sh"
    with open(run_script_sh, 'w') as f:
        f.write(f"""#!/bin/bash
# Activation script for the auto_blog virtual environment

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"

# Activate the virtual environment
source "{venv_dir}/bin/activate"

# Inform the user
echo "Virtual environment activated. Run 'python run_autoblog.py' to start the system."
""")
    
    # Make the shell script executable
    os.chmod(run_script_sh, 0o755)
    
    # Create run_blog.bat for Windows
    run_script_bat = project_root / "run_blog.bat"
    with open(run_script_bat, 'w') as f:
        f.write(f"""@echo off
REM Activation script for the auto_blog virtual environment

REM Get the directory of this script
SET SCRIPT_DIR=%~dp0

REM Activate the virtual environment
call "{venv_dir}\\Scripts\\activate.bat"

REM Inform the user
echo Virtual environment activated. Run 'python run_autoblog.py' to start the system.
""")

if __name__ == "__main__":
    main() 