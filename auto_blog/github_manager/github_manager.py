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
        Ensure the local repository exists. Clone it if not.
        
        Returns:
            True if the repository exists or was cloned successfully, False otherwise
        """
        try:
            repo_dir = Path(self.repo_path)
            
            # Check if the repository already exists
            if (repo_dir / ".git").exists():
                self.repo = Repo(self.repo_path)
                logger.info(f"Using existing Git repository at {self.repo_path}")
                return True
            
            # Clone the repository if it doesn't exist
            clone_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/{self.github_repo}.git"
            logger.info(f"Cloning repository {self.github_username}/{self.github_repo}")
            
            os.makedirs(self.repo_path, exist_ok=True)
            self.repo = Repo.clone_from(clone_url, self.repo_path)
            logger.info(f"Repository cloned to {self.repo_path}")
            
            # Configure user and email
            with self.repo.config_writer() as git_config:
                git_config.set_value('user', 'name', self.github_username)
                git_config.set_value('user', 'email', self.github_email)
            
            return True
        
        except Exception as e:
            logger.error(f"Error ensuring repository exists: {str(e)}")
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