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
                 available_tags: List[str], ad_manager=None, seo_config=None):
        """
        Initialize the post generator.
        
        Args:
            posts_dir: Directory where Jekyll posts are stored
            site_url: URL of the blog site
            author_name: Name of the blog author
            image_dir: Directory where images are stored
            available_categories: List of available categories for the blog
            available_tags: List of available tags for the blog
            ad_manager: AdManager instance for adding ads to posts
            seo_config: SEO configuration settings
        """
        self.posts_dir = posts_dir
        self.site_url = site_url
        self.author_name = author_name
        self.image_dir = image_dir
        self.available_categories = available_categories
        self.available_tags = available_tags
        self.ad_manager = ad_manager
        self.seo_config = seo_config or {}
        
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
            
            # Add SEO-specific frontmatter if configured
            if self.seo_config:
                # Add description for SEO meta tags
                if description:
                    frontmatter['description'] = description
                
                # Add OpenGraph and Twitter card meta tags if enabled
                if self.seo_config.get('seo_enable_opengraph', True):
                    frontmatter['og_image'] = image_relative_path if image_relative_path else None
                    frontmatter['og_description'] = description
                
                if self.seo_config.get('seo_enable_twitter_cards', True):
                    twitter_username = self.seo_config.get('seo_twitter_username')
                    if twitter_username:
                        frontmatter['twitter'] = {
                            'username': twitter_username,
                            'card': 'summary_large_image'
                        }
                
                # Add Schema.org structured data if enabled
                if self.seo_config.get('seo_enable_schema_org', True):
                    frontmatter['schema_org'] = {
                        'type': 'BlogPosting',
                        'author': self.author_name,
                        'datePublished': f"{date_str}T{date.strftime('%H:%M:%S')}",
                        'headline': title,
                        'image': f"{self.site_url}{image_relative_path}" if image_relative_path else None,
                        'description': description
                    }
                
                # Add canonical URL for better SEO
                frontmatter['canonical_url'] = f"{self.site_url}/{date_str.replace('-', '/')}/{slug}/"
            
            # Set up sidebar ads if enabled and position is 'sidebar'
            if self.ad_manager and self.ad_manager.enabled and self.ad_manager.position == 'sidebar':
                frontmatter['sidebar'] = {
                    'nav': 'main',
                    'ads': True
                }
            
            # Remove None values from frontmatter
            if 'header' in frontmatter and frontmatter['header'].get('teaser') is None:
                del frontmatter['header']
            
            # Format frontmatter as YAML
            frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            # Add source attribution at the end of the content
            if source_url and source_name:
                content += f"\n\n---\n\nSource: [{source_name}]({source_url})"
            elif source_url:
                content += f"\n\n---\n\nSource: [Original Article]({source_url})"
            
            # Insert ads into content if enabled and not using sidebar position
            if self.ad_manager and self.ad_manager.enabled and self.ad_manager.position != 'sidebar':
                content = self.ad_manager.insert_ad_into_content(content)
                logger.info(f"Added {self.ad_manager.position} advertisement to post")
            
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
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower().strip()
        # Remove special characters
        slug = re.sub(r'[^\w\s-]', '', slug)
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove multiple hyphens
        slug = re.sub(r'-+', '-', slug)
        # Truncate to a reasonable length
        slug = slug[:50]
        # Remove trailing hyphens
        slug = slug.strip('-')
        return slug
    
    def _select_categories(self, max_categories: int = 2) -> List[str]:
        """
        Select random categories from the available categories.
        
        Args:
            max_categories: Maximum number of categories to select
            
        Returns:
            List of selected categories
        """
        num_categories = min(max_categories, len(self.available_categories))
        return random.sample(self.available_categories, num_categories)
    
    def _process_tags(self, tags: List[str], max_tags: int = 5) -> List[str]:
        """
        Process tags to be valid for Jekyll and select a subset if needed.
        
        Args:
            tags: List of tags
            max_tags: Maximum number of tags to use
            
        Returns:
            List of processed tags
        """
        # Ensure we have tags
        if not tags:
            # Use some from the available tags
            num_tags = min(max_tags, len(self.available_tags))
            return random.sample(self.available_tags, num_tags)
        
        # Process the provided tags
        processed_tags = []
        for tag in tags:
            # Convert to lowercase, replace spaces with hyphens
            processed_tag = tag.lower().strip()
            processed_tag = re.sub(r'[^\w\s-]', '', processed_tag)
            processed_tag = re.sub(r'\s+', '-', processed_tag)
            processed_tags.append(processed_tag)
        
        # Limit the number of tags
        if len(processed_tags) > max_tags:
            processed_tags = processed_tags[:max_tags]
        
        return processed_tags

    def _render_content(self, content, metadata=None):
        """
        Render the content for the blog post, including any necessary processing
        
        Args:
            content (str): The post content
            metadata (dict, optional): Additional metadata for rendering
            
        Returns:
            str: The processed content
        """
        if not content:
            return ""
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        # Add in-content ad after the first or second paragraph
        if (os.environ.get('ADS_ENABLED', 'false').lower() in ('true', 'yes', '1') and 
            (os.environ.get('ADS_GOOGLE_PUBLISHER_ID') or 
             os.environ.get('ADS_AMAZON_TRACKING_ID') or 
             os.environ.get('ADS_CUSTOM_AD_CODE'))):
            
            # Determine where to insert the ad
            # If there are at least 3 paragraphs, insert after the 2nd paragraph
            # Otherwise, insert after the 1st paragraph
            insert_position = 1 if len(paragraphs) >= 3 else 0
            if len(paragraphs) > insert_position:
                ad_include = '{% include content_ad.html %}'
                paragraphs.insert(insert_position + 1, ad_include)
        
        # Rejoin the paragraphs into a single string
        content = '\n\n'.join(paragraphs)
        
        # Apply any needed transformations to the content
        # For example, you might want to process markdown, add styling, etc.
        
        return content
        
    def _generate_post_file_path(self, title, pub_date):
        """
        Generate a file path for the blog post based on its title and publication date.
        
        Args:
            title (str): The post title
            pub_date (datetime): The publication date
            
        Returns:
            str: The file path where the post should be saved
        """
        # Format the date as YYYY-MM-DD
        date_str = pub_date.strftime('%Y-%m-%d')
        
        # Create a slug from the title
        slug = self._slugify(title)
        
        # Limit the slug length to avoid excessively long filenames
        if len(slug) > 100:
            slug = slug[:100]
        
        # Format: YYYY-MM-DD-title-slug.md
        file_name = f"{date_str}-{slug}.md"
        
        # Join with the posts directory
        return os.path.join(self.posts_dir, file_name)

    def generate_post_content(self, article, ai_content=None, ai_title=None):
        """
        Generate a markdown blog post from an article entry
        
        Args:
            article (dict): Article information from RSS feed
            ai_content (str, optional): AI-generated content
            ai_title (str, optional): AI-generated title
            
        Returns:
            tuple: (file_path, frontmatter, content) - File path where post was saved,
                   frontmatter dict, and content string
        """
        # Extract information from the article
        title = ai_title if ai_title else article.get('title', 'Untitled')
        link = article.get('link', '')
        description = article.get('description', '')
        content = ai_content if ai_content else article.get('content', description)
        pub_date = article.get('published_parsed') or article.get('updated_parsed')
        
        if pub_date:
            pub_date = datetime.datetime(*pub_date[:6])
        else:
            pub_date = datetime.datetime.now()
            
        # Generate tags for the post
        tags = self._generate_tags(article)
        
        # Create slug for URL
        slug = self._slugify(title)
        
        # Add SEO metadata if available
        seo_description = os.environ.get('SEO_DESCRIPTION', '')
        seo_keywords = os.environ.get('SEO_KEYWORDS', '')
        
        # Prepare frontmatter
        frontmatter = {
            'title': title,
            'date': pub_date.strftime('%Y-%m-%d %H:%M:%S %z'),
            'categories': tags,
            'tags': tags,
            'link': link,
            'excerpt': description[:160] + '...' if len(description) > 160 else description,
            'header': {
                'teaser': article.get('image', '/assets/images/teaser.jpg'),
            }
        }
        
        # Add SEO metadata to frontmatter if available
        if seo_description:
            frontmatter['description'] = seo_description
        if seo_keywords:
            frontmatter['keywords'] = seo_keywords.split(',')
        
        # Add additional SEO tags from environment variables
        for key, value in os.environ.items():
            if key.startswith('SEO_') and key != 'SEO_DESCRIPTION' and key != 'SEO_KEYWORDS':
                # Convert to lowercase and remove SEO_ prefix
                fm_key = key[4:].lower()
                # Add to frontmatter
                if ',' in value:
                    # Split comma-separated values into lists
                    frontmatter[fm_key] = [v.strip() for v in value.split(',')]
                else:
                    frontmatter[fm_key] = value
        
        # Process content through renderer
        processed_content = self._render_content(content, metadata={'article': article, 'frontmatter': frontmatter})
        
        # Generate the file path
        file_path = self._generate_post_file_path(title, pub_date)
        
        # Create the post file with YAML frontmatter
        self._write_post_file(file_path, frontmatter, processed_content)
        
        return file_path, frontmatter, processed_content 