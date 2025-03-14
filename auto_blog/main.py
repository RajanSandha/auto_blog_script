"""
Main module for the automated blog system.
Handles the coordination of all components.
"""

import os
import logging
import sys
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import time
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Import configuration
from . import config
from .rss_fetcher import RSSFetcher
from .ai_content import AIFactory
from .image_handler import ImageHandler
from .post_generator import PostGenerator
from .github_manager import GitHubManager
from .utils import create_directory, PostHistory, AdManager

# Set up logging
log_dir = Path(__file__).parent.parent / "logs"
create_directory(str(log_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"autoblog_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the automated blog system.
    Fetches RSS feeds, generates blog posts with AI, and pushes to GitHub repository.
    """
    logger.info("Starting automated blog system")
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        logger.error("Exiting due to configuration errors")
        sys.exit(1)
    
    # Get configuration
    cfg = config.get_config()
    
    # Determine working directory for GitHub repo
    repo_dir = Path(__file__).parent.parent / "github_repo"
    os.makedirs(repo_dir, exist_ok=True)
    
    # Set up GitHub manager
    github_manager = GitHubManager(
        repo_path=str(repo_dir),
        github_token=cfg['github_token'],
        github_username=cfg['github_username'],
        github_repo=cfg['github_repo'],
        branch=cfg['github_branch'],
        author_name=cfg['github_username'],
        author_email=cfg['github_email']
    )
    
    # Ensure GitHub repository exists and is up to date
    if not github_manager.ensure_repo_exists():
        logger.error("Failed to initialize GitHub repository")
        sys.exit(1)
        
    # Pull latest changes to avoid conflicts
    if not github_manager.pull_latest_changes():
        logger.warning("Failed to pull latest changes, continuing with local repository")
    
    # Initialize RSS fetcher
    rss_fetcher = RSSFetcher(
        feed_urls=cfg['rss_feeds'],
        max_items_per_feed=cfg['max_rss_items'],
        max_age_days=cfg['max_article_age_days']
    )
    
    # Initialize AI content generator
    ai_generator = AIFactory.create_ai_provider(
        provider=cfg['ai_provider'],
        api_key=cfg.get(f"{cfg['ai_provider']}_api_key"),
        model=cfg.get(f"{cfg['ai_provider']}_model")
    )
    
    # Initialize image handler
    image_handler = ImageHandler(
        output_dir=os.path.join(repo_dir, cfg['blog_image_path'])
    )
    
    # Initialize ad manager if ads are enabled
    ad_manager = None
    if 'ads_enabled' in cfg and cfg['ads_enabled']:
        logger.info("Initializing ad manager with configuration")
        ad_manager = AdManager(cfg)
    
    # Get SEO configuration
    seo_config = {
        'seo_enable_opengraph': cfg.get('seo_enable_opengraph', True),
        'seo_enable_twitter_cards': cfg.get('seo_enable_twitter_cards', True),
        'seo_enable_schema_org': cfg.get('seo_enable_schema_org', True),
        'seo_enable_sitemap': cfg.get('seo_enable_sitemap', True),
        'seo_enable_robots_txt': cfg.get('seo_enable_robots_txt', True),
        'seo_twitter_username': cfg.get('seo_twitter_username', '')
    }
    
    # Initialize post generator
    post_generator = PostGenerator(
        posts_dir=os.path.join(repo_dir, cfg['blog_post_path']),
        site_url=cfg['site_url'],
        author_name=cfg['author_name'],
        image_dir=os.path.join(repo_dir, cfg['blog_image_path']),
        available_categories=cfg['jekyll_categories'],
        available_tags=cfg['jekyll_tags'],
        ad_manager=ad_manager,
        seo_config=seo_config
    )
    
    # Initialize post history tracker to avoid duplicates
    history_file = os.path.join(str(log_dir), "post_history.json")
    post_history = PostHistory(history_file)
    
    # Generate posts
    posts_to_create = cfg['posts_per_day']
    posts_created = []
    
    logger.info(f"Attempting to create {posts_to_create} new posts")
    
    # Attempt to fetch articles from RSS feeds
    rss_items = rss_fetcher.fetch_all_feeds()
    if not rss_items:
        logger.error("Failed to fetch any RSS feeds")
        sys.exit(1)
    
    logger.info(f"Fetched {len(rss_items)} RSS items from feeds")
    
    # Filter out articles that we've already processed
    new_items = [item for item in rss_items if not post_history.is_processed(item['url'])]
    logger.info(f"{len(new_items)} new RSS items after filtering out processed ones")
    
    # Shuffle to randomize which items we use
    random.shuffle(new_items)
    
    # Generate posts from RSS items
    for i, item in enumerate(new_items):
        if i >= posts_to_create:
            break
            
        logger.info(f"Processing item {i+1}/{posts_to_create}: {item['title']}")
        
        try:
            # Mark this URL as processed to avoid duplicates
            post_history.mark_as_processed(item['url'])
            
            # Generate enhanced content using AI
            logger.info(f"Generating content with {cfg['ai_provider']} for: {item['title']}")
            content_data = ai_generator.generate_content(
                title=item['title'],
                content=item['description'],
                url=item['url'],
                max_words=cfg['max_words_per_post']
            )
            
            if not content_data:
                logger.warning(f"Failed to generate content for: {item['title']}")
                continue
                
            # Generate an image for the post using AI if available in the future
            # For now, we'll use placeholder images
            image_path = image_handler.generate_placeholder_image(
                title=item['title'],
                width=1200,
                height=630
            )
            
            # Create the post file
            post_path = post_generator.create_post(
                content_data=content_data,
                image_path=image_path
            )
            
            if post_path:
                posts_created.append(post_path)
                logger.info(f"Created post: {post_path}")
            else:
                logger.warning(f"Failed to create post for: {item['title']}")
                
        except Exception as e:
            logger.error(f"Error processing item: {str(e)}")
    
    # Save post history
    post_history.save()
    
    # Create SEO files if enabled
    if cfg.get('seo_enable_sitemap', True):
        _create_sitemap(repo_dir, cfg['site_url'])
        
    if cfg.get('seo_enable_robots_txt', True):
        _create_robots_txt(repo_dir, cfg['site_url'])
    
    # Commit and push changes
    if posts_created:
        logger.info(f"Created {len(posts_created)} new posts")
        
        # Commit all changes to ensure all assets are included
        success = github_manager.commit_and_push_changes(
            message=f"Add {len(posts_created)} new blog posts"
        )
        
        if success:
            logger.info("Successfully pushed changes to GitHub repository")
            logger.info(f"Website will be updated at: {cfg['site_url']}")
        else:
            logger.error("Failed to push changes to GitHub repository")
    else:
        logger.info("No new posts were created")
    
    logger.info("Automated blog system completed successfully")

def _create_sitemap(repo_dir: Path, site_url: str) -> None:
    """
    Create a sitemap.xml file for the website.
    
    Args:
        repo_dir: Path to the GitHub repository
        site_url: URL of the site
    """
    try:
        # Jekyll automatically generates the sitemap if the plugin is enabled
        # We just need to make sure the _config.yml has the plugin
        config_path = repo_dir / "_config.yml"
        
        if config_path.exists():
            # Read existing config
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if sitemap plugin is already configured
            if 'jekyll-sitemap' not in content:
                logger.info("Adding sitemap plugin to _config.yml")
                
                # Prepare new content with sitemap plugin
                if 'plugins:' in content:
                    # Add to existing plugins list
                    content = content.replace('plugins:', 'plugins:\n  - jekyll-sitemap')
                else:
                    # Add new plugins section
                    content += '\n\n# SEO Plugins\nplugins:\n  - jekyll-sitemap\n'
                
                # Write updated config
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                logger.info("Added sitemap plugin to _config.yml")
        else:
            logger.warning("_config.yml not found, cannot add sitemap plugin")
    
    except Exception as e:
        logger.error(f"Error creating sitemap: {str(e)}")

def _create_robots_txt(repo_dir: Path, site_url: str) -> None:
    """
    Create a robots.txt file for the website.
    
    Args:
        repo_dir: Path to the GitHub repository
        site_url: URL of the site
    """
    try:
        robots_path = repo_dir / "robots.txt"
        
        # Don't overwrite if already exists
        if not robots_path.exists():
            logger.info("Creating robots.txt file")
            
            content = f"""# robots.txt for {site_url}
User-agent: *
Allow: /

Sitemap: {site_url}/sitemap.xml
"""
            
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info("Created robots.txt file")
    
    except Exception as e:
        logger.error(f"Error creating robots.txt: {str(e)}")

if __name__ == "__main__":
    main()
