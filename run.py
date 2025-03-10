#!/usr/bin/env python3
"""
Main script to run the auto_blog system.
This script:
1. Checks if the virtual environment exists, creates it if not
2. Ensures the GitHub repository is properly set up
3. Runs the auto_blog system to generate and publish posts
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from dotenv import load_dotenv
import time

def init_github_repo_manually():
    """Initialize the GitHub repository manually if there are issues with the GitHub manager."""
    github_repo_dir = Path("github_repo")
    
    if not github_repo_dir.exists():
        print("⚠️ GitHub repository directory doesn't exist, can't initialize manually.")
        return False
    
    print("🛠️ Manually initializing GitHub repository...")
    try:
        # Change to the github_repo directory
        os.chdir(github_repo_dir)
        
        # Initialize git repository if .git directory doesn't exist
        if not Path(".git").exists():
            subprocess.run(["git", "init"], check=True)
            print("✅ Git repository initialized.")
        
        # Configure git user and email from environment variables
        load_dotenv()
        github_username = os.getenv('GITHUB_USERNAME', 'yourusername')
        github_email = os.getenv('GITHUB_EMAIL', 'your.email@example.com')
        
        subprocess.run(["git", "config", "user.name", github_username], check=True)
        subprocess.run(["git", "config", "user.email", github_email], check=True)
        print(f"✅ Git user configured: {github_username} <{github_email}>")
        
        # Add remote origin if it doesn't exist
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        if "origin" not in result.stdout:
            github_repo = os.getenv('GITHUB_REPO', 'yourblog')
            subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{github_username}/{github_repo}.git"], check=True)
            print(f"✅ Added remote: https://github.com/{github_username}/{github_repo}.git")
        
        # Switch to main branch
        try:
            subprocess.run(["git", "checkout", "main"], check=True)
        except subprocess.CalledProcessError:
            # Branch doesn't exist, create it
            try:
                subprocess.run(["git", "checkout", "-b", "main"], check=True)
                print("✅ Created and switched to main branch.")
            except subprocess.CalledProcessError as branch_error:
                print(f"❌ Error creating branch: {branch_error}")
        
        # Go back to the project root
        os.chdir("..")
        return True
    except Exception as e:
        print(f"❌ Error during manual repository initialization: {e}")
        # Try to return to the project root
        try:
            os.chdir(Path(__file__).parent)
        except:
            pass
        return False

def main():
    """
    Main function to set up and run the auto_blog system.
    Handles environment setup and runs the blog generation process.
    """
    project_root = Path(__file__).resolve().parent
    venv_dir = project_root / "venv"
    
    # Force reload the .env file to ensure fresh environment variables
    dotenv_path = project_root / ".env"
    if dotenv_path.exists():
        print("⚙️ Loading environment variables from .env file...")
        # Force reload with override=True
        load_dotenv(dotenv_path=dotenv_path, override=True)
        
        # Debug environment variables
        print(f"📊 Environment settings:")
        print(f"   • AI Provider: {os.getenv('AI_PROVIDER', 'not set')}")
        print(f"   • Posts per day: {os.getenv('POSTS_PER_DAY', 'not set')}")
    
    load_dotenv()
    
    # Determine the project root directory
    project_root = Path(__file__).resolve().parent
    venv_dir = project_root / "venv"
    
    # Load environment variables for GitHub URL display
    load_dotenv()
    github_username = os.getenv('GITHUB_USERNAME', 'yourusername')
    github_repo = os.getenv('GITHUB_REPO', 'yourrepository')
    
    print("=" * 80)
    print("Auto Blog System - Minimal Mistakes Theme")
    print("=" * 80)
    
    # Check if virtual environment exists
    if not venv_dir.exists():
        print("\n📦 Virtual environment not found. Running setup first...")
        setup_script = project_root / "setup.py"
        if not setup_script.exists():
            print("❌ Error: setup.py script not found.")
            sys.exit(1)
        
        try:
            subprocess.run([sys.executable, str(setup_script)], check=True)
            print("✅ Setup completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running setup: {e}")
            sys.exit(1)
    
    # Determine python executable path based on platform
    is_windows = platform.system() == "Windows"
    bin_dir = "Scripts" if is_windows else "bin"
    python_path = venv_dir / bin_dir / ("python.exe" if is_windows else "python")
    
    # Check if the python executable exists
    if not python_path.exists():
        print(f"❌ Error: Python executable not found at {python_path}")
        print("Please run setup.py manually to create the virtual environment.")
        sys.exit(1)
    
    # Check if the GitHub repository exists
    github_repo_dir = project_root / "github_repo"
    if not github_repo_dir.exists():
        print("\n📦 Minimal Mistakes repository not found. Running setup...")
        setup_script = project_root / "setup.py"
        try:
            subprocess.run([sys.executable, str(setup_script)], check=True)
            print("✅ Setup completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running setup: {e}")
            sys.exit(1)
    
    # Try to initialize the GitHub repository manually as a fallback
    init_github_repo_manually()
    
    # Run the auto_blog system to generate and publish posts
    print("\n🔄 Running auto_blog system to generate and publish posts...")
    run_script = project_root / "run_autoblog.py"
    try:
        subprocess.run([str(python_path), str(run_script)], check=True)
        print("\n✅ Blog posts generated and published successfully!")
        print("\n📊 Summary:")
        print(f"- Repository: https://github.com/{github_username}/{github_repo}")
        print(f"- Website: https://{github_username}.github.io/{github_repo}")
        print("\n📝 Next steps:")
        print("1. If this is your first run, go to your GitHub repository settings")
        print("2. Navigate to Settings → Pages")
        print("3. Set the source to your main branch and root folder")
        print("4. Click Save to enable GitHub Pages")
        print("\n🔄 Run this script again tomorrow to generate new blog posts!")
        print("=" * 80)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running auto_blog system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 