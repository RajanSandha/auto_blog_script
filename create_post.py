#!/usr/bin/env python3
"""
Script to create new blog posts for the al-folio Jekyll theme.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import re
from typing import Optional

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'[\s]+', '-', text)
    # Remove special characters
    text = re.sub(r'[^\w\-]', '', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    return text

def create_post(title: str, category: Optional[str] = None) -> bool:
    """
    Create a new blog post with the given title.
    
    Args:
        title: The title of the blog post
        category: Optional category for the post
        
    Returns:
        True if post was created successfully, False otherwise
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).resolve().parent
        posts_dir = project_root / "github_repo" / "_posts"
        
        # Create _posts directory if it doesn't exist
        posts_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with current date and slugified title
        today = datetime.now()
        date_prefix = today.strftime("%Y-%m-%d")
        slug = slugify(title)
        filename = f"{date_prefix}-{slug}.md"
        filepath = posts_dir / filename
        
        # Check if post already exists
        if filepath.exists():
            print(f"Error: Post already exists at {filepath}")
            return False
        
        # Create post content
        content = f"""---
layout: post
title: {title}
date: {today.strftime("%Y-%m-%d %H:%M:%S")} +0000
description: # Add post description (optional)
tags: # Add post tags (optional)
categories: {category if category else ''}
---

Write your post content here...
"""
        
        # Write the post file
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"Created new post: {filepath}")
        print("\nYou can now edit this file to add your post content.")
        print("After editing, commit and push your changes to publish the post.")
        
        return True
        
    except Exception as e:
        print(f"Error creating post: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create a new blog post")
    parser.add_argument('--title', required=True, help='Title of the blog post')
    parser.add_argument('--category', help='Category for the blog post (optional)')
    args = parser.parse_args()
    
    if create_post(args.title, args.category):
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main()) 