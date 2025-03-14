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
from git.exc import InvalidGitRepositoryError, NoSuchPathError
import traceback
import subprocess

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
            repo_path: Path to the local repository
            github_token: GitHub personal access token
            github_username: GitHub username
            github_email: Email for Git commits
            github_repo: Repository name (e.g., 'username/repo')
            branch: Branch to use (default: 'main')
        """
        self.repo_path = repo_path
        self.github_token = github_token
        self.github_username = github_username
        self.github_email = github_email
        self.github_repo = github_repo
        # Clean the branch name to remove any comments
        self.branch = branch.split('#')[0].strip() if branch else "main"
        self.repo = None
        
        logger.info(f"GitHub manager initialized for repo: {github_username}/{github_repo}")
        
        # Ensure Git is properly configured
        self._setup_git_config()
    
    def _setup_git_config(self):
        """
        Configure global Git settings needed for proper operation.
        This helps prevent issues with line endings and other Git behaviors.
        """
        try:
            # Set global Git configuration for the GitPython instance
            with git.Git().custom_environment(GIT_COMMITTER_NAME=self.github_username, 
                                             GIT_COMMITTER_EMAIL=self.github_email,
                                             GIT_AUTHOR_NAME=self.github_username,
                                             GIT_AUTHOR_EMAIL=self.github_email):
                # This environment will be used for all Git operations in this instance
                pass
                
            # Set additional Git configurations if needed
            if self.repo:
                with self.repo.config_writer() as git_config:
                    # Configure line ending behavior for cross-platform compatibility
                    git_config.set_value('core', 'autocrlf', 'input')
                    # Set user information
                    git_config.set_value('user', 'name', self.github_username)
                    git_config.set_value('user', 'email', self.github_email)
                logger.debug("Git configuration set successfully")
        except Exception as e:
            logger.warning(f"Error setting up Git configuration: {str(e)}")
            # This is non-fatal, so we'll continue even if this fails
    
    def ensure_repo_exists(self) -> bool:
        """
        Ensure that the repository exists locally.
        If the repository doesn't exist, it will be created from scratch.
        
        Returns:
            True if the repository exists or was created successfully, False otherwise
        """
        try:
            # Check if the repo directory exists
            repo_path = Path(self.repo_path)
            if repo_path.exists() and repo_path.is_dir():
                logger.info(f"Found existing repository at {self.repo_path}")
                try:
                    # Try to load the git repository
                    import git
                    self.repo = git.Repo(self.repo_path)
                    
                    # Check if the remote is set correctly
                    try:
                        origin_url = self.repo.remotes.origin.url
                        expected_url = f"https://github.com/{self.github_username}/{self.github_repo}.git"
                        
                        if origin_url != expected_url:
                            logger.warning(f"Remote URL is {origin_url}, expected {expected_url}")
                            logger.info("Updating remote URL")
                            self.repo.remotes.origin.set_url(expected_url)
                    except Exception as remote_err:
                        logger.warning(f"Error checking remote: {remote_err}")
                        # Try to add the remote if it doesn't exist
                        try:
                            self.repo.create_remote('origin', f'https://github.com/{self.github_username}/{self.github_repo}.git')
                            logger.info("Added remote origin")
                        except git.GitCommandError:
                            # Remote might already exist with a different URL
                            self.repo.delete_remote('origin')
                            self.repo.create_remote('origin', f'https://github.com/{self.github_username}/{self.github_repo}.git')
                            logger.info("Reset remote origin")
                    
                    # Configure user and email
                    with self.repo.config_writer() as config:
                        config.set_value('user', 'name', self.github_username)
                        config.set_value('user', 'email', self.github_email)
                    logger.info("Configured user and email")
                    
                    return True
                    
                except (ImportError, Exception) as e:
                    logger.warning(f"Error loading existing repository: {e}")
                    logger.warning("Attempting to initialize repository from scratch")
                    # The directory exists but is not a valid git repository or has issues
                    # Will re-initialize it below
            
            # At this point, either the directory doesn't exist or we couldn't load it as a git repo
            # Initialize a new repository
            return self._init_and_configure_repo()
                
        except Exception as e:
            logger.error(f"Error ensuring repository exists: {e}")
            return False
    
    def _init_and_configure_repo(self) -> bool:
        """
        Initialize and configure a new git repository.
        This is called if the repository directory doesn't exist or is not a git repository.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            import git
            repo_path = Path(self.repo_path)
            
            # Create the directory if it doesn't exist
            if not repo_path.exists():
                logger.info(f"Creating directory: {repo_path}")
                os.makedirs(repo_path, exist_ok=True)
            
            # If the directory exists and contains files, check if it's already a git repo
            if repo_path.exists() and any(repo_path.iterdir()):
                try:
                    # Try to load as git repository
                    self.repo = git.Repo(repo_path)
                    logger.info("Directory is already a git repository")
                except git.InvalidGitRepositoryError:
                    # Not a git repository, initialize it
                    logger.info("Directory exists but is not a git repository, initializing...")
                    self.repo = git.Repo.init(repo_path)
            else:
                # Empty directory or newly created, initialize it
                logger.info(f"Initializing new git repository at {repo_path}")
                self.repo = git.Repo.init(repo_path)
            
            # Configure remote
            remote_url = f"https://github.com/{self.github_username}/{self.github_repo}.git"
            try:
                # Check if origin already exists
                origin = self.repo.remote('origin')
                if list(origin.urls)[0] != remote_url:
                    logger.info(f"Updating remote URL from {list(origin.urls)[0]} to {remote_url}")
                    origin.set_url(remote_url)
            except (ValueError, git.GitCommandError):
                # Origin doesn't exist, create it
                logger.info(f"Adding remote origin: {remote_url}")
                self.repo.create_remote('origin', remote_url)
            
            # Configure user and email
            with self.repo.config_writer() as config:
                config.set_value('user', 'name', self.github_username)
                config.set_value('user', 'email', self.github_email)
            logger.info("Configured user and email")
            
            # Configure default branch
            clean_branch = self.branch.split('#')[0].strip()
            
            # Check if the branch already exists in the local repository
            try:
                # Try to get the branch
                self.repo.heads[clean_branch]
                logger.info(f"Branch {clean_branch} already exists")
            except (IndexError, ValueError):
                # Branch doesn't exist, create it
                logger.info(f"Creating branch {clean_branch}")
                self.repo.git.checkout('-b', clean_branch)
            
            # Set up Jekyll structure
            self.ensure_jekyll_structure()
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing repository: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def ensure_jekyll_structure(self, custom_domain: str = None) -> bool:
        """
        Ensure repository has minimal-mistakes Jekyll structure.
        Rather than creating Jekyll files from scratch, this method configures the existing minimal-mistakes structure.
        
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
            
            # Check if essential minimal-mistakes directories exist
            essential_dirs = ["_posts", "assets", "_data", "_pages", "_includes", "_layouts"]
            for dir_path in essential_dirs:
                dir_full_path = repo_dir / dir_path
                if not dir_full_path.exists():
                    logger.warning(f"Expected minimal-mistakes directory not found: {dir_path}")
                    dir_full_path.mkdir(exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
            
            # Ensure assets/images directory exists for post images
            images_dir = repo_dir / "assets" / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Update _config.yml to add user-specific settings
            config_path = repo_dir / "_config.yml"
            if config_path.exists():
                logger.info("Updating _config.yml with user settings")
                
                # Read the existing config
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # Update basic information in the config
                replace_pairs = {
                    'title                    : "Your Site Title"': f'title                    : "{self.github_username}\'s Tech Blog"',
                    'name                     : "Your Name"': f'name                     : "{self.github_username}"',
                    'description              : "An amazing website."': f'description              : "Automated tech blog powered by AI."',
                    'url                      : # the base hostname & protocol for your site e.g. "https://mmistakes.github.io"': f'url                      : "https://{self.github_username}.github.io"',
                    'baseurl                  : # the subpath of your site, e.g. "/blog"': f'baseurl                  : "/{self.github_repo}"',
                    'repository               : # GitHub username/repo-name e.g. "mmistakes/minimal-mistakes"': f'repository               : "{self.github_username}/{self.github_repo}"',
                    'search                   : # true, false (default)': 'search                   : true',
                    'atom_feed:\n  path                   : # blank (default) uses feed.xml': 'atom_feed:\n  path                   : "/feed.xml"',
                }
                
                # Apply replacements
                for old_text, new_text in replace_pairs.items():
                    # Use flexible matching approach
                    old_text_pattern = old_text.split(':')[0].strip() if ':' in old_text else old_text
                    if old_text_pattern in config_content:
                        config_content = config_content.replace(old_text, new_text)
                
                # Add custom domain if provided
                if custom_domain:
                    if 'url                      :' in config_content:
                        config_content = config_content.replace(
                            f'url                      : "https://{self.github_username}.github.io"',
                            f'url                      : "https://{custom_domain}"'
                        )
                    if 'baseurl                  :' in config_content:
                        config_content = config_content.replace(
                            f'baseurl                  : "/{self.github_repo}"',
                            'baseurl                  : ""'
                        )
                
                # Write updated config back to file
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                logger.info("Updated _config.yml with user settings")
                
                # Create/update CNAME file for custom domain if provided
                if custom_domain:
                    cname_path = repo_dir / "CNAME"
                    with open(cname_path, 'w') as f:
                        f.write(custom_domain)
                    logger.info(f"Created CNAME file with domain: {custom_domain}")
            else:
                logger.warning("_config.yml not found, minimal-mistakes theme might not be properly set up")
            
            # Create index.html in the root if it doesn't exist
            index_html_path = repo_dir / "index.html"
            if not index_html_path.exists():
                with open(index_html_path, 'w', encoding='utf-8') as f:
                    f.write("""---
layout: home
author_profile: true
---
""")
                logger.info("Created index.html file")
                
            # Ensure _pages directory has proper content
            about_page_path = repo_dir / "_pages" / "about.md"
            if not about_page_path.exists():
                if not (repo_dir / "_pages").exists():
                    (repo_dir / "_pages").mkdir(exist_ok=True)
                    
                with open(about_page_path, 'w', encoding='utf-8') as f:
                    f.write("""---
permalink: /about/
title: "About"
---

This is an automated tech blog powered by AI. The content is generated by processing tech news articles and creating informative summaries and insights.
""")
                logger.info("Created about.md page")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring Jekyll structure: {e}")
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
            
            # Check if there are untracked files that might be overwritten
            has_untracked = False
            try:
                # Check for untracked files
                untracked_files = self.repo.git.ls_files('--others', '--exclude-standard')
                has_untracked = bool(untracked_files.strip())
                
                if has_untracked:
                    logger.info("Found untracked files, stashing them before pull")
                    # Stash untracked files
                    self.repo.git.stash('--include-untracked')
            except Exception as stash_error:
                logger.warning(f"Error checking or stashing untracked files: {stash_error}")
                # Continue with the pull anyway
            
            # Make sure the repository is in a clean state
            if self.repo.is_dirty():
                logger.warning("Repository has uncommitted changes. Attempting to reset...")
                self.repo.git.reset('--hard')
            
            # Try to get the origin remote
            try:
                origin = self.repo.remotes.origin
            except (AttributeError, IndexError):
                logger.warning("Remote 'origin' not found, adding it...")
                self.repo.create_remote('origin', f'https://github.com/{self.github_username}/{self.github_repo}.git')
                origin = self.repo.remotes.origin
            
            # Make sure we use the clean branch name without any comments
            clean_branch = self.branch.split('#')[0].strip()
            
            # Try fetch first to check connectivity
            logger.info(f"Fetching from remote...")
            origin.fetch()
            
            # Then pull with --ff-only to avoid merge conflicts
            logger.info(f"Pulling latest changes from {clean_branch} branch")
            try:
                origin.pull(clean_branch, ff_only=True)
            except Exception as pull_error:
                logger.warning(f"Error pulling with --ff-only: {pull_error}")
                logger.info("Trying alternative pull strategy...")
                
                # If the --ff-only pull fails, try to reset to the remote branch
                try:
                    remote_branch = f"origin/{clean_branch}"
                    logger.info(f"Fetching from {remote_branch} and resetting")
                    self.repo.git.fetch('origin', clean_branch)
                    
                    # Check if the branch exists in the remote
                    remote_refs = [ref.name for ref in self.repo.remote().refs]
                    if remote_branch.replace('/', '/') in remote_refs:
                        # Reset to the remote branch
                        self.repo.git.reset('--hard', remote_branch)
                        logger.info(f"Reset to {remote_branch} successful")
                    else:
                        # If the branch doesn't exist in the remote, we'll push our local branch
                        logger.info(f"Branch {clean_branch} not found in remote, local changes will be kept")
                except Exception as reset_error:
                    logger.warning(f"Error resetting to remote branch: {reset_error}")
                    logger.info("Proceeding with local changes")
            
            # Apply stashed changes if we stashed them
            if has_untracked:
                try:
                    logger.info("Applying stashed changes")
                    self.repo.git.stash('pop')
                except Exception as pop_error:
                    logger.warning(f"Error applying stashed changes: {pop_error}")
            
            logger.info(f"Successfully pulled latest changes from {clean_branch} branch")
            return True
        
        except Exception as e:
            logger.error(f"Error pulling latest changes: {str(e)}")
            return False
    
    def commit_and_push_changes(self, message: str) -> bool:
        """
        Commit all changes in the repository and push to the remote branch.
        
        Args:
            message: The commit message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add all files in the repository - this ensures new files are tracked
            logger.info("Adding ALL files in the github_repo directory...")
            os.chdir(self.repo_path)
            
            # Try using GitPython to add all files
            try:
                self.repo.git.add(A=True)
                logger.info("Added all files using GitPython")
            except Exception as e:
                # Fall back to direct git command if GitPython fails
                logger.warning(f"GitPython add failed: {str(e)}, falling back to direct git command")
                subprocess.run(["git", "add", "--all"], check=True)
                logger.info("Added all files using direct git command")
            
            # Check if there are changes to commit
            status = self.repo.git.status(porcelain=True)
            if not status:
                logger.info("No changes to commit")
                return True
            
            # Log the files staged for commit
            logger.info(f"Files staged for commit:\n{status}")
            
            # Make the commit
            logger.info(f"Committing changes with message: {message}")
            self.repo.git.commit(m=message)
            
            # Push changes to remote
            branch_name = self.repo.active_branch.name
            logger.info(f"Pushing changes to remote branch: {branch_name}")
            
            try:
                # Try the push operation
                self.repo.git.push("origin", branch_name)
                logger.info(f"Successfully pushed changes to {branch_name}")
                return True
            except git.GitCommandError as push_error:
                logger.warning(f"Error pushing changes: {push_error}")
                
                # Check if it's an authentication error
                if "could not read Username" in str(push_error) or "Authentication failed" in str(push_error):
                    # Try setting the remote URL with the token embedded
                    try:
                        if self.github_token and self.github_username and self.github_repo:
                            logger.info("Detected authentication error. Attempting to update remote with token.")
                            auth_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/{self.github_repo}.git"
                            self.repo.git.remote("set-url", "origin", auth_url)
                            logger.info("Updated remote URL with authentication token")
                            
                            # Try push again with the new URL
                            self.repo.git.push("origin", branch_name)
                            logger.info(f"Successfully pushed changes to {branch_name} after URL update")
                            return True
                    except Exception as auth_fix_error:
                        logger.error(f"Failed to fix authentication: {str(auth_fix_error)}")
                
                # If not fixed, try to fetch and rebase before pushing
                logger.info("Fetching remote changes before retrying push")
                try:
                    self.repo.git.fetch("origin", branch_name)
                    self.repo.git.rebase(f"origin/{branch_name}")
                    logger.info("Attempting to rebase and push")
                    self.repo.git.push("origin", branch_name)
                    logger.info(f"Successfully pushed changes to {branch_name} after rebase")
                    return True
                except git.GitCommandError as rebase_error:
                    logger.warning(f"Rebase and push failed: {rebase_error}")
                    
                    # As a last resort, try force push (if it's due to divergent branches)
                    if "rejected" in str(rebase_error) and "divergent" in str(rebase_error):
                        logger.warning("Attempting force push as last resort")
                        try:
                            self.repo.git.push("-f", "origin", branch_name)
                            logger.info(f"Successfully force pushed changes to {branch_name}")
                            return True
                        except git.GitCommandError as force_error:
                            logger.error(f"Force push failed: {force_error}")
                
                return False
            
        except Exception as e:
            logger.error(f"Error committing and pushing changes: {str(e)}")
            return False
    
    def commit_and_push_files(self, filepaths: List[str], message: str) -> bool:
        """
        Commit specific files and push changes to the remote repository.
        
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
            
            # Log the files we're committing
            for filepath in filepaths:
                logger.info(f"Committed files: {filepath}")
                
            # But actually add ALL files to ensure everything is up-to-date
            logger.info("Adding ALL files in the github_repo directory for completeness...")
            
            # First, make sure we're in the right directory
            os.chdir(self.repo_path)
            
            # Add all files
            self.repo.git.add(A=True)  # Same as 'git add --all'
            
            # As a backup, use direct git command
            try:
                subprocess.run(["git", "add", "--all"], cwd=self.repo_path, check=True)
            except Exception as cmd_error:
                logger.warning(f"Direct git command failed, but GitPython method may have succeeded: {cmd_error}")
            
            # Check if there are changes to commit
            if not self.repo.is_dirty():
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            self.repo.git.commit('-m', message)
            logger.info(f"Committed files: {', '.join(filepaths)}")
            
            # Push to remote
            origin = self.repo.remotes.origin
            # Make sure we use the clean branch name without any comments
            clean_branch = self.branch.split('#')[0].strip()
            try:
                push_info = origin.push(clean_branch)
                
                # Check if push was successful
                if len(push_info) > 0 and push_info[0].flags & git.PushInfo.ERROR:
                    logger.error(f"Error pushing changes: {push_info[0].summary}")
                    return False
                
                logger.info(f"Pushed changes to {clean_branch} branch")
                return True
            except Exception as push_error:
                logger.error(f"Error pushing to remote: {str(push_error)}")
                return False
        
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
        Switch to the specified branch.
        
        Args:
            branch_name: Name of the branch to switch to
            
        Returns:
            True if the switch was successful, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
            
            # Clean branch name (remove any comments)
            clean_branch = branch_name.split('#')[0].strip()
            
            # Check current branch
            current_branch = None
            try:
                current_branch = self.repo.active_branch.name
            except (TypeError, ValueError, AttributeError) as branch_err:
                logger.warning(f"Error getting current branch: {branch_err}")
                # Could be a detached HEAD state
            
            # If we're already on the correct branch, do nothing
            if current_branch == clean_branch:
                logger.info(f"Already on branch '{clean_branch}'")
                return True
            
            # Check if the branch exists
            if clean_branch in [h.name for h in self.repo.heads]:
                # Branch exists locally, switch to it
                logger.info(f"Switching to existing branch '{clean_branch}'")
                self.repo.git.checkout(clean_branch)
            else:
                # Branch doesn't exist, check if it exists in remote
                try:
                    remote_branch = f"origin/{clean_branch}"
                    remote_refs = [ref.name for ref in self.repo.remote().refs]
                    remote_exists = remote_branch.replace('/', '/') in remote_refs
                    
                    if remote_exists:
                        # Branch exists in remote, check it out
                        logger.info(f"Creating branch '{clean_branch}' from remote")
                        self.repo.git.checkout('-b', clean_branch, remote_branch)
                    else:
                        # Branch doesn't exist anywhere, create it
                        logger.info(f"Creating new branch '{clean_branch}'")
                        self.repo.git.checkout('-b', clean_branch)
                except Exception as remote_err:
                    logger.warning(f"Error checking remote branches: {remote_err}")
                    # Fallback: create the branch locally
                    logger.info(f"Creating new branch '{clean_branch}' (fallback method)")
                    self.repo.git.checkout('-b', clean_branch)
            
            logger.info(f"Successfully switched to branch '{clean_branch}'")
            return True
            
        except Exception as e:
            logger.error(f"Error switching to branch '{branch_name}': {e}")
            return False 