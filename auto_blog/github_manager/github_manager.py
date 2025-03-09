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
    
    def ensure_jekyll_structure(self, custom_domain: str = None) -> bool:
        """
        Ensure the repository has the necessary Jekyll structure for GitHub Pages.
        
        Args:
            custom_domain: Custom domain name to use (optional)
            
        Returns:
            True if the structure was created successfully, False otherwise
        """
        try:
            if not self.repo:
                if not self.ensure_repo_exists():
                    return False
                    
            repo_dir = Path(self.repo_path)
            
            # Create essential Jekyll directories if they don't exist
            essential_dirs = [
                "_posts",
                "_layouts",
                "_includes",
                "assets/images",
                "assets/css",
            ]
            
            for dir_path in essential_dirs:
                full_path = repo_dir / dir_path
                if not full_path.exists():
                    logger.info(f"Creating Jekyll directory: {dir_path}")
                    full_path.mkdir(parents=True, exist_ok=True)
            
            # Check if _config.yml exists, create a basic one if not
            config_path = repo_dir / "_config.yml"
            if not config_path.exists():
                logger.info("Creating basic Jekyll _config.yml")
                with open(config_path, 'w') as f:
                    f.write(f"""# Jekyll configuration for GitHub Pages
title: {self.github_username}'s Tech Blog
description: Automated tech news blog powered by AI
author: {self.github_username}
email: {self.github_email}

# Theme settings
theme: minima    # Choose one of: minima, jekyll-theme-cayman, jekyll-theme-minimal, jekyll-theme-hacker, jekyll-theme-slate, jekyll-theme-tactile
# Uncomment the following line instead if you want to use a remote theme
# remote_theme: owner/name

# Build settings
markdown: kramdown
permalink: /:year/:month/:day/:title/
plugins:
  - jekyll-feed
  - jekyll-sitemap
  - jekyll-seo-tag
  - jekyll-remote-theme

# Custom settings
future: false
timezone: UTC
show_excerpts: true

# Collections
collections:
  categories:
    output: true
    permalink: /categories/:path/
  tags:
    output: true
    permalink: /tags/:path/

# Defaults
defaults:
  - scope:
      path: ""
      type: "posts"
    values:
      layout: "post"
      comments: false
  - scope:
      path: ""
    values:
      layout: "default"

# Exclude from processing
exclude:
  - README.md
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor
  - .git
""")
            
            # Create Gemfile for Jekyll with GitHub Pages
            gemfile_path = repo_dir / "Gemfile"
            if not gemfile_path.exists():
                logger.info("Creating Gemfile for Jekyll with GitHub Pages")
                with open(gemfile_path, 'w') as f:
                    f.write("""source "https://rubygems.org"

# Use GitHub Pages
gem "github-pages", group: :jekyll_plugins

# If you have any plugins, put them here!
group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
  gem "jekyll-remote-theme"
end

# Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "webrick", "~> 1.7"
""")

            # Create custom SCSS for minima theme customization if needed
            minima_scss_path = repo_dir / "_sass" / "minima" / "custom-styles.scss"
            if not minima_scss_path.exists():
                os.makedirs(minima_scss_path.parent, exist_ok=True)
                logger.info("Creating custom SCSS for minima theme customization")
                with open(minima_scss_path, 'w') as f:
                    f.write("""// Custom styles for minima theme
// This file is imported at the end of "_sass/minima/skins/classic.scss"

// Example customization:
// .site-header {
//   background-color: #f0f0f0;
// }
""")

            # Create assets structure for theme customization
            assets_dir = repo_dir / "assets" / "css"
            os.makedirs(assets_dir, exist_ok=True)
            
            # Create custom CSS file for theme customization
            style_scss_path = repo_dir / "assets" / "css" / "style.scss"
            if not style_scss_path.exists():
                logger.info("Creating style.scss for theme customization")
                with open(style_scss_path, 'w') as f:
                    f.write("""---
---

@import "{{ site.theme }}";

// Your custom styles go here
""")
            
            # Create default layout if it doesn't exist
            default_layout_path = repo_dir / "_layouts/default.html"
            if not default_layout_path.exists():
                logger.info("Creating default Jekyll layout")
                os.makedirs(default_layout_path.parent, exist_ok=True)
                with open(default_layout_path, 'w') as f:
                    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ page.title }} | {{ site.title }}</title>
  <link rel="stylesheet" href="/assets/css/style.css">
  {% seo %}
</head>
<body>
  <header>
    <div class="container">
      <h1><a href="/">{{ site.title }}</a></h1>
      <p>{{ site.description }}</p>
    </div>
  </header>
  
  <main class="container">
    {{ content }}
  </main>
  
  <footer>
    <div class="container">
      <p>&copy; {{ site.time | date: '%Y' }} {{ site.author }}. All rights reserved.</p>
    </div>
  </footer>
</body>
</html>""")
            
            # Create post layout if it doesn't exist
            post_layout_path = repo_dir / "_layouts/post.html"
            if not post_layout_path.exists():
                logger.info("Creating post Jekyll layout")
                os.makedirs(post_layout_path.parent, exist_ok=True)
                with open(post_layout_path, 'w') as f:
                    f.write("""---
layout: default
---
<article class="post h-entry" itemscope itemtype="http://schema.org/BlogPosting">

  <header class="post-header">
    <h1 class="post-title p-name" itemprop="name headline">{{ page.title | escape }}</h1>
    <p class="post-meta">
      <time class="dt-published" datetime="{{ page.date | date_to_xmlschema }}" itemprop="datePublished">
        {%- assign date_format = site.minima.date_format | default: "%b %-d, %Y" -%}
        {{ page.date | date: date_format }}
      </time>
      {%- if page.author -%}
        • <span itemprop="author" itemscope itemtype="http://schema.org/Person"><span class="p-author h-card" itemprop="name">{{ page.author }}</span></span>
      {%- endif -%}
      
      {%- if page.categories.size > 0 -%}
      • <span class="categories">
        Categories: 
        {% for category in page.categories %}
        <a href="/categories/{{ category | slugify }}/">{{ category }}</a>{% if forloop.last == false %}, {% endif %}
        {% endfor %}
      </span>
      {%- endif -%}
    </p>
  </header>

  {%- if page.image -%}
  <div class="featured-image">
    <img src="{{ page.image }}" alt="{{ page.title | escape }}" itemprop="image">
  </div>
  {%- endif -%}

  <div class="post-content e-content" itemprop="articleBody">
    {{ content }}
  </div>

  {%- if page.tags.size > 0 -%}
  <div class="tags">
    Tags: 
    {% for tag in page.tags %}
    <a href="/tags/{{ tag | slugify }}/">#{{ tag }}</a>{% if forloop.last == false %} {% endif %}
    {% endfor %}
  </div>
  {%- endif -%}

  {%- if page.source -%}
  <div class="source">
    Source: <a href="{{ page.source.url }}" target="_blank" rel="nofollow noopener">{{ page.source.name }}</a>
  </div>
  {%- endif -%}

  <a class="u-url" href="{{ page.url | relative_url }}" hidden></a>
</article>""")
            
            # Create index.html for the home page if it doesn't exist
            index_path = repo_dir / "index.html"
            if not index_path.exists():
                logger.info("Creating index.html for the home page")
                with open(index_path, 'w') as f:
                    f.write("""---
layout: default
title: Home
---

<div class="home">
  <h1 class="page-heading">Latest Articles</h1>
  
  <div class="post-list">
    {% for post in site.posts limit:10 %}
    <div class="post-preview">
      <h2>
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      </h2>
      
      <div class="post-meta">
        <span class="date">{{ post.date | date: "%B %d, %Y" }}</span>
        {% if post.author %}
        <span class="author">by {{ post.author }}</span>
        {% endif %}
      </div>
      
      {% if post.image %}
      <div class="preview-image">
        <a href="{{ post.url | relative_url }}">
          <img src="{{ post.image }}" alt="{{ post.title }}">
        </a>
      </div>
      {% endif %}
      
      <div class="post-excerpt">
        {% if post.description %}
          {{ post.description }}
        {% else %}
          {{ post.excerpt | strip_html | truncatewords: 50 }}
        {% endif %}
        <a href="{{ post.url | relative_url }}" class="read-more">Read more &raquo;</a>
      </div>
    </div>
    {% endfor %}
  </div>
  
  <div class="pagination">
    <a href="/archive" class="all-posts">View All Posts</a>
  </div>
</div>
""")
            
            # Create archive.html for all posts if it doesn't exist
            archive_path = repo_dir / "archive.html"
            if not archive_path.exists():
                logger.info("Creating archive.html for all posts")
                with open(archive_path, 'w') as f:
                    f.write("""---
layout: default
title: Archive
---

<div class="archive">
  <h1 class="page-heading">All Articles</h1>
  
  {% assign postsByYear = site.posts | group_by_exp:"post", "post.date | date: '%Y'" %}
  
  {% for year in postsByYear %}
  <h2 class="year-heading">{{ year.name }}</h2>
  <ul class="post-list">
    {% for post in year.items %}
    <li>
      <span class="post-date">{{ post.date | date: "%b %d" }}</span>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </li>
    {% endfor %}
  </ul>
  {% endfor %}
</div>
""")
            
            # Create basic CSS if it doesn't exist
            css_path = repo_dir / "assets/css/style.css"
            if not css_path.exists():
                logger.info("Creating basic CSS styles")
                os.makedirs(css_path.parent, exist_ok=True)
                with open(css_path, 'w') as f:
                    f.write("""/* Basic styles for the blog */
:root {
  --primary-color: #0366d6;
  --text-color: #24292e;
  --background-color: #ffffff;
  --light-gray: #f6f8fa;
  --border-color: #e1e4e8;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
  background-color: var(--background-color);
  margin: 0;
  padding: 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 15px;
}

header {
  background-color: var(--primary-color);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
}

header h1 a {
  color: white;
  text-decoration: none;
}

footer {
  border-top: 1px solid var(--border-color);
  margin-top: 2rem;
  padding: 1rem 0;
  text-align: center;
  font-size: 0.9rem;
  color: #6a737d;
}

/* Post styles */
.post {
  margin-bottom: 3rem;
}

.post-meta {
  color: #6a737d;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.post-meta span {
  margin-right: 1rem;
}

.featured-image, .preview-image {
  margin-bottom: 1.5rem;
}

.featured-image img, .preview-image img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.post-content {
  margin-bottom: 1.5rem;
}

.post-content img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 1rem 0;
}

.tags a {
  color: var(--primary-color);
  text-decoration: none;
}

.source {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.9rem;
}

/* Home page styles */
.post-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.post-preview {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
}

.post-preview h2 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.post-preview h2 a {
  color: var(--text-color);
  text-decoration: none;
}

.post-preview h2 a:hover {
  color: var(--primary-color);
}

.post-excerpt {
  margin-top: 1rem;
}

.read-more {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: bold;
  display: inline-block;
  margin-top: 0.5rem;
}

/* Archive page styles */
.year-heading {
  margin-top: 2rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.archive .post-list {
  margin-left: 1rem;
}

.archive .post-list li {
  margin-bottom: 0.5rem;
}

.post-date {
  display: inline-block;
  min-width: 6rem;
  color: #6a737d;
}

/* Pagination */
.pagination {
  margin-top: 2rem;
  text-align: center;
}

.all-posts {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  header {
    padding: 1rem 0;
  }
  
  .post-meta span {
    display: block;
    margin-bottom: 0.5rem;
  }
  
  .post-date {
    display: block;
    min-width: auto;
  }
}""")
            
            # Create CNAME file for custom domain if provided
            if custom_domain:
                cname_path = repo_dir / "CNAME"
                logger.info(f"Setting up custom domain: {custom_domain}")
                with open(cname_path, 'w') as f:
                    f.write(custom_domain)
            
            # Create .nojekyll file if it doesn't exist (in case we want GitHub to not process with Jekyll)
            # Uncomment if you want to disable Jekyll processing
            # nojekyll_path = repo_dir / ".nojekyll"
            # if not nojekyll_path.exists():
            #     with open(nojekyll_path, 'w') as f:
            #         pass  # Empty file
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring Jekyll structure: {str(e)}")
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