"""
Post generator implementation for creating Jekyll-compatible blog posts.
"""

import os
import re
import random
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import shutil

logger = logging.getLogger(__name__)

class PostGenerator:
    """
    Generates Jekyll-compatible blog posts from AI-generated content.
    """
    
    def __init__(self, posts_dir: str, site_url: str, author_name: str, 
                 image_dir: str, available_categories: List[str],
                 available_tags: List[str]):
        """
        Initialize the post generator.
        
        Args:
            posts_dir: Directory where Jekyll posts are stored
            site_url: URL of the blog site
            author_name: Name of the blog author
            image_dir: Directory where images are stored
            available_categories: List of available categories for the blog
            available_tags: List of available tags for the blog
        """
        self.posts_dir = posts_dir
        self.site_url = site_url
        self.author_name = author_name
        self.image_dir = image_dir
        self.available_categories = available_categories
        self.available_tags = available_tags
        
        # Create the posts directory if it doesn't exist
        os.makedirs(self.posts_dir, exist_ok=True)
        logger.info(f"Post generator initialized with directory: {self.posts_dir}")
    
    def create_post(self, content_data: Dict[str, Any], image_path: Optional[str] = None) -> Optional[str]:
        """
        Create a Jekyll-compatible blog post for minimal-mistakes theme.
        
        Args:
            content_data: Dictionary containing the generated content and metadata
            image_path: Path to the featured image for the post
            
        Returns:
            Path to the created post file, or None if creation failed
        """
        try:
            # Extract content data
            title = content_data.get('title', '')
            content = content_data.get('content', '')
            tags = content_data.get('tags', [])
            description = content_data.get('meta_description', '')
            source_url = content_data.get('source_url', '')
            source_name = content_data.get('source_name', '')
            
            if not title or not content:
                logger.error("Cannot create post: missing title or content")
                return None
            
            # Generate filename with date and slug
            date = datetime.now()
            date_str = date.strftime('%Y-%m-%d')
            time_str = date.strftime('%H:%M:%S %z')
            slug = self._generate_slug(title)
            filename = f"{date_str}-{slug}.md"  # Minimal mistakes uses .md extension
            filepath = os.path.join(self.posts_dir, filename)
            
            # Prepare relative image path if an image is provided
            image_relative_path = None
            if image_path:
                # Get image path relative to the Jekyll site root
                image_name = os.path.basename(image_path)
                # Minimal-mistakes typically uses /assets/images/ for images
                image_relative_path = f"/assets/images/{image_name}"
                
                # Make sure the image is in the assets/images directory
                assets_img_dir = os.path.join(os.path.dirname(self.posts_dir), "assets/images")
                os.makedirs(assets_img_dir, exist_ok=True)
                
                # Check if the image is already in the assets/images directory
                target_image_path = os.path.join(assets_img_dir, image_name)
                image_abs_path = os.path.abspath(image_path)
                target_abs_path = os.path.abspath(target_image_path)
                
                # Only copy if the source and destination are different
                if image_abs_path != target_abs_path:
                    shutil.copy2(image_path, target_image_path)
                    logger.info(f"Copied image from {image_path} to {target_image_path}")
                else:
                    logger.info(f"Image already in correct location: {target_image_path}")
            
            # Process tags to be valid for Jekyll
            processed_tags = self._process_tags(tags, max_tags=5)
            
            # Prepare frontmatter in minimal-mistakes format
            frontmatter = {
                'title': title,
                'date': f"{date_str} {time_str}",
                'categories': self._select_categories(max_categories=2),
                'tags': processed_tags,
                'excerpt': description if description else f"{' '.join(content.split()[:30])}...",
                'header': {
                    'teaser': image_relative_path if image_relative_path else None
                },
                'toc': True,
                'toc_sticky': True,
                'classes': 'wide'
            }
            
            # Remove None values from frontmatter
            if frontmatter['header']['teaser'] is None:
                del frontmatter['header']
            
            # Format frontmatter as YAML
            frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            # Add source attribution at the end of the content
            if source_url and source_name:
                content += f"\n\n---\n\nSource: [{source_name}]({source_url})"
            elif source_url:
                content += f"\n\n---\n\nSource: [Original Article]({source_url})"
            
            # Combine frontmatter and content
            post_content = f"---\n{frontmatter_yaml}---\n\n{content}"
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(post_content)
            
            logger.info(f"Created post {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return None
    
    def _generate_slug(self, title: str) -> str:
        """
        Generate a slug from the post title.
        
        Args:
            title: The post title
            
        Returns:
            A URL-friendly slug
        """
        # Remove special characters and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug.strip())
        
        # Limit length
        return slug[:50]
    
    def _select_categories(self, max_categories: int = 2) -> List[str]:
        """
        Select random categories from available categories.
        
        Args:
            max_categories: Maximum number of categories to select
            
        Returns:
            List of selected categories
        """
        num_categories = min(max_categories, len(self.available_categories))
        return random.sample(self.available_categories, num_categories)
    
    def _process_tags(self, suggested_tags: List[str], max_tags: int = 5) -> List[str]:
        """
        Process and filter suggested tags.
        
        Args:
            suggested_tags: List of tags suggested by the AI
            max_tags: Maximum number of tags to include
            
        Returns:
            List of processed tags
        """
        # Filter out invalid tags and convert to lowercase
        processed_tags = []
        
        # First add tags that match our available tags
        available_tags_lower = [tag.lower() for tag in self.available_tags]
        
        for tag in suggested_tags:
            # Skip empty tags
            if not tag:
                continue
                
            # Convert to lowercase and remove special characters
            clean_tag = re.sub(r'[^\w\s-]', '', tag.lower())
            clean_tag = re.sub(r'[\s_-]+', '-', clean_tag.strip())
            
            # If the tag is in our available tags, add it
            if clean_tag.lower() in available_tags_lower:
                processed_tags.append(clean_tag)
        
        # If we don't have enough tags, add some from our available tags
        if len(processed_tags) < max_tags:
            remaining_slots = max_tags - len(processed_tags)
            # Get tags that aren't already selected
            remaining_tags = [tag for tag in self.available_tags if tag.lower() not in [t.lower() for t in processed_tags]]
            
            if remaining_tags:
                # Select random tags from remaining available tags
                num_to_add = min(remaining_slots, len(remaining_tags))
                processed_tags.extend(random.sample(remaining_tags, num_to_add))
        
        # Limit the number of tags
        return processed_tags[:max_tags] 