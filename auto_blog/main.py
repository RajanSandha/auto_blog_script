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

# Import configuration
from . import config
from .rss_fetcher import RSSFetcher
from .ai_content import AIFactory
from .image_handler import ImageHandler
from .post_generator import PostGenerator
from .github_manager import GitHubManager
from .utils import create_directory

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
    
    try:
        # Initialize GitHub manager
        github_manager = GitHubManager(
            repo_path=str(repo_dir),
            github_token=cfg['github_token'],
            github_username=cfg['github_username'],
            github_email=cfg['github_email'],
            github_repo=cfg['github_repo'],
            branch=cfg['github_branch']
        )
        
        # Ensure repository exists and pull latest changes
        if not github_manager.ensure_repo_exists():
            logger.error("Failed to ensure repository exists")
            sys.exit(1)
        
        if not github_manager.pull_latest_changes():
            logger.error("Failed to pull latest changes")
            sys.exit(1)
        
        # Initialize RSS fetcher
        rss_fetcher = RSSFetcher(
            rss_urls=cfg['rss_feeds'],
            max_items_per_feed=cfg['max_rss_items'],
            max_age_days=cfg['max_article_age_days']
        )
        
        # Initialize AI content generator
        ai_factory = AIFactory()
        ai_generator = ai_factory.create_generator(
            provider=cfg['ai_provider'],
            api_key=cfg['openai_api_key'] if cfg['ai_provider'] == 'openai' else cfg['gemini_api_key'],
            model=cfg['openai_model'] if cfg['ai_provider'] == 'openai' else cfg['gemini_model']
        )
        
        # Initialize image handler
        # Images will be stored in the GitHub repo
        image_dir = os.path.join(repo_dir, cfg['blog_image_path'])
        image_handler = ImageHandler(image_dir=image_dir)
        
        # Initialize post generator
        post_generator = PostGenerator(
            posts_dir=os.path.join(repo_dir, cfg['blog_post_path']),
            site_url=cfg['site_url'],
            author_name=cfg['author_name'],
            image_dir=cfg['blog_image_path'],  # Relative path for Jekyll
            available_categories=cfg['jekyll_categories'],
            available_tags=cfg['jekyll_tags']
        )
        
        # Fetch RSS feeds
        logger.info("Fetching RSS feeds")
        rss_items = rss_fetcher.fetch_all_feeds()
        
        if not rss_items:
            logger.error("No RSS items fetched")
            sys.exit(1)
        
        logger.info(f"Fetched {len(rss_items)} RSS items")
        
        # Shuffle and select items to process
        random.shuffle(rss_items)
        selected_items = rss_items[:cfg['posts_per_day']]
        
        logger.info(f"Selected {len(selected_items)} items for processing")
        
        # Process each selected item
        created_files = []
        
        for i, item in enumerate(selected_items):
            logger.info(f"Processing item {i+1}/{len(selected_items)}: {item.title}")
            
            # Convert RSS item to dictionary for AI processing
            article_data = {
                'title': item.title,
                'link': item.link,
                'description': item.description,
                'content': item.content,
                'published_date': item.published_date,
                'author': item.author,
                'categories': item.categories,
                'image_url': item.image_url,
                'source_name': item.source_name
            }
            
            # Generate content using AI
            logger.info(f"Generating content for: {item.title}")
            generated_content = ai_generator.generate_blog_post(
                article_data=article_data,
                max_words=cfg['max_words_per_post']
            )
            
            # Download featured image
            logger.info(f"Downloading image for: {item.title}")
            image_path = None
            if item.image_url:
                image_path = image_handler.download_article_image(article_data)
                if image_path:
                    # Resize image if needed
                    image_handler.resize_image(image_path, max_width=800)
            
            # Create Jekyll post
            logger.info(f"Creating post for: {item.title}")
            post_path = post_generator.create_post(
                content_data=generated_content,
                image_path=image_path
            )
            
            if post_path:
                created_files.append(post_path)
                logger.info(f"Created post: {post_path}")
            else:
                logger.error(f"Failed to create post for: {item.title}")
            
            # Add a delay between posts to avoid rate limiting
            if i < len(selected_items) - 1:
                time.sleep(random.uniform(1.0, 3.0))
        
        # Commit and push changes if any posts were created
        if created_files:
            logger.info(f"Committing and pushing {len(created_files)} new posts")
            commit_message = f"Add {len(created_files)} new blog posts - {datetime.now().strftime('%Y-%m-%d')}"
            if github_manager.commit_and_push_changes(commit_message):
                logger.info("Successfully committed and pushed changes")
            else:
                logger.error("Failed to commit and push changes")
        else:
            logger.warning("No posts were created")
        
        logger.info("Automated blog system completed successfully")
    
    except Exception as e:
        logger.error(f"Error in automated blog system: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
