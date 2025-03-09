"""
GitHub manager implementation for handling interaction with GitHub repository.
"""

import os
import logging
import git
from git import Repo
from typing import List, Optional
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class GitHubManager:
    """
    Handles interaction with GitHub repository for publishing blog posts.
    """
    
    def __init__(self, repo_path: str, github_token: str, 
                 github_username: str, github_email: str, 
                 github_repo: str, branch: str = "main"):
        """
        Initialize the GitHub manager.
        
        Args:
            repo_path: Local path to the Git repository
            github_token: GitHub personal access token
            github_username: GitHub username
            github_email: Email associated with GitHub account
            github_repo: Name of the GitHub repository
            branch: Branch to commit and push to
        """
        self.repo_path = repo_path
        self.github_token = github_token
        self.github_username = github_username
        self.github_email = github_email
        self.github_repo = github_repo
        self.branch = branch
        self.repo = None
        
        logger.info(f"GitHub manager initialized for repo: {github_username}/{github_repo}")
    
    def ensure_repo_exists(self) -> bool:
        """
        Ensure the local repository exists and has the al-folio structure.
        This version assumes the al-folio repository has already been cloned to repo_path.
        
        Returns:
            True if the repository exists and is set up correctly, False otherwise
        """
        try:
            repo_dir = Path(self.repo_path)
            
            # Check if the repository already exists with .git directory
            if (repo_dir / ".git").exists():
                self.repo = Repo(self.repo_path)
                logger.info(f"Using existing Git repository at {self.repo_path}")
                
                # Configure user and email
                with self.repo.config_writer() as git_config:
                    git_config.set_value('user', 'name', self.github_username)
                    git_config.set_value('user', 'email', self.github_email)
                
                return True
            
            # Check if the directory exists but is not a git repository
            if repo_dir.exists():
                # Initialize a new git repository
                logger.info(f"Initializing new Git repository in existing directory {self.repo_path}")
                self.repo = Repo.init(self.repo_path)
                
                # Configure user and email
                with self.repo.config_writer() as git_config:
                    git_config.set_value('user', 'name', self.github_username)
                    git_config.set_value('user', 'email', self.github_email)
                
                # Try to add the remote
                try:
                    remote_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/{self.github_repo}.git"
                    self.repo.create_remote('origin', remote_url)
                    logger.info(f"Added remote: origin -> {remote_url.replace(self.github_token, '****')}")
                except Exception as e:
                    logger.warning(f"Could not add remote: {e}")
                
                return True
            
            # If the directory doesn't exist, clone from the user's repository if possible
            try:
                logger.info(f"Attempting to clone repository {self.github_username}/{self.github_repo}")
                clone_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/{self.github_repo}.git"
                os.makedirs(self.repo_path, exist_ok=True)
                self.repo = Repo.clone_from(clone_url, self.repo_path)
                logger.info(f"Repository cloned to {self.repo_path}")
                
                # Configure user and email
                with self.repo.config_writer() as git_config:
                    git_config.set_value('user', 'name', self.github_username)
                    git_config.set_value('user', 'email', self.github_email)
                
                return True
            except Exception as e:
                # If clone fails (e.g., repository doesn't exist yet), log the error
                logger.error(f"Error cloning repository: {str(e)}")
                logger.info("You'll need to create the repository on GitHub first or check your GitHub credentials")
                return False
            
        except Exception as e:
            logger.error(f"Error ensuring repository exists: {str(e)}")
            return False
    
    def ensure_jekyll_structure(self, custom_domain: str = None) -> bool:
        """
        Ensure repository has al-folio Jekyll structure.
        Rather than creating Jekyll files from scratch, this method configures the existing al-folio structure.
        
        Args:
            custom_domain: Custom domain name to use (optional)
            
        Returns:
            True if the structure was set up correctly, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
                    
            repo_dir = Path(self.repo_path)
            
            # Check if essential al-folio directories exist
            essential_dirs = ["_posts", "assets", "_pages", "_bibliography", "_data"]
            for dir_path in essential_dirs:
                if not (repo_dir / dir_path).exists():
                    logger.warning(f"Expected al-folio directory not found: {dir_path}")
            
            # Update _config.yml to add user-specific settings
            config_path = repo_dir / "_config.yml"
            if config_path.exists():
                logger.info("Updating _config.yml with user settings")
                
                # Read the existing config
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # Update basic information in the config
                replace_pairs = {
                    'title: al-folio': f'title: {self.github_username}\'s Tech Blog',
                    'first_name: You': f'first_name: {self.github_username}',
                    'last_name: Name': f'last_name: ',
                    'email: you@example.com': f'email: {self.github_email}',
                    'github_username: alshedivat': f'github_username: {self.github_username}',
                    'repo_name: al-folio': f'repo_name: {self.github_repo}'
                }
                
                for old, new in replace_pairs.items():
                    config_content = config_content.replace(old, new)
                
                # Write the updated config back
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                
                logger.info("Updated _config.yml with user settings")
            else:
                logger.warning("_config.yml not found - al-folio structure may be incomplete.")
            
            # Create CNAME file for custom domain if provided
            if custom_domain:
                cname_path = repo_dir / "CNAME"
                logger.info(f"Setting up custom domain: {custom_domain}")
                with open(cname_path, 'w') as f:
                    f.write(custom_domain)
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring al-folio structure: {str(e)}")
            return False
    
    def pull_latest_changes(self) -> bool:
        """
        Pull the latest changes from the remote repository.
        
        Returns:
            True if pull was successful, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
            
            origin = self.repo.remotes.origin
            origin.pull(self.branch)
            logger.info(f"Pulled latest changes from {self.branch} branch")
            return True
        
        except Exception as e:
            logger.error(f"Error pulling latest changes: {str(e)}")
            return False
    
    def commit_and_push_changes(self, message: str) -> bool:
        """
        Commit and push changes to the remote repository.
        
        Args:
            message: Commit message
            
        Returns:
            True if commit and push were successful, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
            
            # Add all changes
            self.repo.git.add('--all')
            
            # Check if there are changes to commit
            if not self.repo.is_dirty(untracked_files=True):
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            self.repo.git.commit('-m', message)
            logger.info(f"Committed changes with message: {message}")
            
            # Push to remote
            origin = self.repo.remotes.origin
            push_info = origin.push(self.branch)
            
            # Check if push was successful
            if push_info[0].flags & git.PushInfo.ERROR:
                logger.error(f"Error pushing changes: {push_info[0].summary}")
                return False
            
            logger.info(f"Pushed changes to {self.branch} branch")
            return True
        
        except Exception as e:
            logger.error(f"Error committing and pushing changes: {str(e)}")
            return False
    
    def commit_and_push_files(self, filepaths: List[str], message: str) -> bool:
        """
        Commit and push specific files to the remote repository.
        
        Args:
            filepaths: List of file paths to commit
            message: Commit message
            
        Returns:
            True if commit and push were successful, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
            
            # Add specified files
            for filepath in filepaths:
                self.repo.git.add(filepath)
            
            # Check if there are changes to commit
            if not self.repo.is_dirty():
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            self.repo.git.commit('-m', message)
            logger.info(f"Committed files: {', '.join(filepaths)}")
            
            # Push to remote
            origin = self.repo.remotes.origin
            push_info = origin.push(self.branch)
            
            # Check if push was successful
            if push_info[0].flags & git.PushInfo.ERROR:
                logger.error(f"Error pushing changes: {push_info[0].summary}")
                return False
            
            logger.info(f"Pushed changes to {self.branch} branch")
            return True
        
        except Exception as e:
            logger.error(f"Error committing and pushing files: {str(e)}")
            return False
    
    def create_branch_if_not_exists(self, branch_name: str) -> bool:
        """
        Create a new branch if it doesn't exist.
        
        Args:
            branch_name: Name of the branch to create
            
        Returns:
            True if the branch exists or was created successfully, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
            
            # Check if the branch already exists
            if branch_name in [ref.name.split('/')[-1] for ref in self.repo.refs]:
                logger.info(f"Branch {branch_name} already exists")
                return True
            
            # Create the branch
            self.repo.git.checkout('-b', branch_name)
            logger.info(f"Created branch {branch_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {str(e)}")
            return False
    
    def switch_branch(self, branch_name: str) -> bool:
        """
        Switch to a different branch.
        
        Args:
            branch_name: Name of the branch to switch to
            
        Returns:
            True if the switch was successful, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
            
            # Check if the branch exists
            if branch_name not in [ref.name.split('/')[-1] for ref in self.repo.refs]:
                logger.error(f"Branch {branch_name} does not exist")
                return False
            
            # Switch to the branch
            self.repo.git.checkout(branch_name)
            self.branch = branch_name
            logger.info(f"Switched to branch {branch_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error switching to branch {branch_name}: {str(e)}")
            return False 