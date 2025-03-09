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
    print("This script will fix the OpenAI API compatibility issue.")
    print("We'll downgrade to openai==0.28.0 which works with the ChatCompletion API.")
    print("The virtual environment will be completely removed and recreated.")
    
    confirmation = input("\nDo you want to continue? (y/n): ").strip().lower()
    
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
        print("\nVerifying OpenAI version...")
        
        # Verify OpenAI version
        venv_python = venv_dir / ("bin" if os.name != "nt" else "Scripts") / ("python" if os.name != "nt" else "python.exe")
        if not os.path.exists(venv_python):
            print(f"Error: Python not found in virtual environment at {venv_python}")
            return
            
        try:
            result = subprocess.run(
                [str(venv_python), "-c", "import openai; print(f'OpenAI version: {openai.__version__}')"],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout.strip())
            
            # Verify the version is 0.28.0
            if "0.28.0" not in result.stdout:
                print("Warning: OpenAI version may not be 0.28.0. There might still be compatibility issues.")
            else:
                print("OpenAI version is correct (0.28.0).")
                
        except subprocess.CalledProcessError:
            print("Failed to verify OpenAI version, but setup completed.")
        
        print("\nYou should now be able to run the system using:")
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
        print("\n=== MANUAL SETUP INSTRUCTIONS ===")
        print("1. Make sure you have virtualenv installed:")
        print("   pip install virtualenv")
        print("\n2. Create a virtual environment:")
        print("   virtualenv venv")
        print("\n3. Activate the environment:")
        print("   On Linux/Mac: source venv/bin/activate")
        print("   On Windows: venv\\Scripts\\activate")
        print("\n4. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n5. Run the system:")
        print("   python run_autoblog.py")
        print("\nNote: Make sure requirements.txt has openai==0.28.0 (NOT a newer version)")

if __name__ == "__main__":
    main() 