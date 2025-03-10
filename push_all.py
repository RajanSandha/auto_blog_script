#!/usr/bin/env python3
"""
Helper script to add and push ALL files in the github_repo directory.
Use this if you want to ensure everything is up-to-date in your GitHub repository.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import time

def main():
    """
    Add and push ALL files in the github_repo directory.
    """
    project_root = Path(__file__).resolve().parent
    github_repo_dir = project_root / "github_repo"
    
    if not github_repo_dir.exists():
        print(f"❌ Error: github_repo directory not found at {github_repo_dir}")
        print("Run setup.py first to create the repository.")
        sys.exit(1)
    
    # Load .env file for GitHub credentials
    load_dotenv()
    github_username = os.getenv('GITHUB_USERNAME', 'yourusername')
    github_email = os.getenv('GITHUB_EMAIL', 'your.email@example.com')
    github_repo = os.getenv('GITHUB_REPO', 'yourrepository')
    
    # Print header
    print("=" * 80)
    print("Push ALL Files to GitHub Repository")
    print("=" * 80)
    
    try:
        # Change to the github_repo directory
        os.chdir(github_repo_dir)
        
        # Configure git user and email if not already set
        subprocess.run(["git", "config", "user.name", github_username], check=True)
        subprocess.run(["git", "config", "user.email", github_email], check=True)
        print(f"✅ Git user configured: {github_username} <{github_email}>")
        
        # Get the current branch
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        branch = result.stdout.strip() or "main"
        print(f"📁 Current branch: {branch}")
        
        # Add all files
        print("📂 Adding ALL files in the repository...")
        subprocess.run(["git", "add", "--all"], check=True)
        
        # Get status to see what's being committed
        result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=True)
        status = result.stdout.strip()
        
        if not status:
            print("✅ No changes to commit. Repository is up-to-date.")
            return
        
        print("\n📋 Files staged for commit:")
        print(status)
        print()
        
        # Commit the changes
        commit_message = f"Update all repository files - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"💾 Committing with message: {commit_message}")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to GitHub
        print(f"🚀 Pushing to {github_username}/{github_repo} on branch {branch}...")
        subprocess.run(["git", "push", "origin", branch], check=True)
        
        print("\n✅ All files successfully pushed to GitHub!")
        print(f"🔗 Repository URL: https://github.com/{github_username}/{github_repo}")
        print(f"🌐 Website URL: https://{github_username}.github.io/{github_repo}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing git command: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 