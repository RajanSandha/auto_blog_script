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
from .utils import create_directory, PostHistory

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
        
        # Check if repo exists and pull latest changes
        if not github_manager.ensure_repo_exists():
            logger.error("Failed to ensure repository exists")
            sys.exit(1)
        
        if not github_manager.pull_latest_changes():
            logger.error("Failed to pull latest changes")
            sys.exit(1)
        
        # Initialize post history tracker to prevent duplicates
        history_file = Path(__file__).parent.parent / "data" / "post_history.json"
        post_history = PostHistory(str(history_file))
        # Clean old entries to keep the history file manageable
        post_history.clean_old_entries()
        logger.info("Post history tracker initialized")
        
        # Initialize RSS fetcher with more robust configuration
        rss_fetcher = RSSFetcher(
            rss_urls=cfg['rss_feeds'],
            max_items_per_feed=cfg['max_rss_items'],
            max_age_days=cfg['max_article_age_days'],
            feed_timeout=15,  # 15 seconds timeout for feed fetching
            article_timeout=8, # 8 seconds timeout for article fetching
            # Skip problematic feeds that often cause timeouts
            known_problematic_feeds=['wired.com']
        )
        
        # Initialize AI content generator
        ai_factory = AIFactory()
        ai_generator = None
        
        # Select AI provider
        try:
            # Reload environment variables to get the latest AI_PROVIDER setting
            ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
            logger.info(f"Using AI_PROVIDER directly from environment: {ai_provider}")
            
            if ai_provider == 'gemini':
                gemini_api_key = os.getenv('GEMINI_API_KEY')
                gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
                ai_generator = ai_factory.create_generator('gemini', gemini_api_key, gemini_model)
            else:
                openai_api_key = os.getenv('OPENAI_API_KEY')
                openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
                ai_generator = ai_factory.create_generator('openai', openai_api_key, openai_model)
        except Exception as ai_error:
            logger.error(f"Error initializing AI generator: {ai_error}")
            # Fall back to OpenAI if there's an error
            openai_api_key = os.getenv('OPENAI_API_KEY')
            openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            ai_generator = ai_factory.create_generator('openai', openai_api_key, openai_model)
        
        # Initialize image handler
        images_dir = Path(repo_dir) / "assets" / "images"
        os.makedirs(images_dir, exist_ok=True)
        image_handler = ImageHandler(str(images_dir))
        
        # Initialize post generator for minimal-mistakes theme
        posts_dir = Path(repo_dir) / "_posts"
        os.makedirs(posts_dir, exist_ok=True)
        
        post_generator = PostGenerator(
            posts_dir=str(posts_dir),
            site_url=f"https://{cfg['github_username']}.github.io/{cfg['github_repo']}",
            author_name=cfg['github_username'],
            image_dir=str(images_dir),
            available_categories=["Tech News", "AI", "Programming", "Web Development", "Data Science"],
            available_tags=["ai", "machine-learning", "programming", "web", "mobile", "cloud", "security", "data"]
        )
        
        # Fetch RSS feeds
        logger.info("Fetching RSS feeds...")
        all_items = rss_fetcher.fetch_all_feeds()
        logger.info(f"Fetched {len(all_items)} items from RSS feeds")
        
        # Filter out already processed items to avoid duplicates
        unprocessed_items = [
            item for item in all_items 
            if not post_history.is_url_processed(item.link)
        ]
        logger.info(f"Filtering out already processed items: {len(all_items) - len(unprocessed_items)} filtered, {len(unprocessed_items)} remaining")
        
        # If no unprocessed items are found, log and exit
        if not unprocessed_items:
            logger.info("No new articles to process. All fetched articles have already been used for posts.")
            logger.info("Try increasing MAX_RSS_ITEMS or MAX_ARTICLE_AGE_DAYS in .env for more content options.")
            return
        
        # Generate and save posts
        created_post_paths = []
        processed_urls = []
        
        # Re-read POSTS_PER_DAY directly from environment to ensure correct value
        load_dotenv(override=True)  # Force reload env vars
        
        try:
            posts_per_day = int(os.getenv('POSTS_PER_DAY', '1'))
            logger.info(f"Using POSTS_PER_DAY directly from environment: {posts_per_day}")
        except (ValueError, TypeError):
            posts_per_day = 1
            logger.warning(f"Could not parse POSTS_PER_DAY from environment, using default: {posts_per_day}")
        
        num_posts_to_generate = min(len(unprocessed_items), posts_per_day)
        logger.info(f"Will generate {num_posts_to_generate} posts based on POSTS_PER_DAY setting")
        
        for i, item in enumerate(unprocessed_items[:num_posts_to_generate]):
            logger.info(f"Processing item {i+1}/{num_posts_to_generate}: {item.title}")
            
            try:
                # Prepare article data for AI
                article_data = {
                    'title': item.title,
                    'content': item.content,
                    'description': item.description,
                    'source_url': item.link,
                    'source_name': item.source_name,
                    'author': item.author,
                    'image_url': item.image_url,
                    'categories': item.categories
                }
                
                # Generate blog post content with AI
                logger.info(f"Generating blog post content with {ai_provider}...")
                generated_content = ai_generator.generate_blog_post(
                    article_data=article_data,
                    max_words=1200,
                    style="informative and engaging"
                )
                
                # Download featured image if available
                image_path = None
                if item.image_url:
                    logger.info(f"Downloading image from {item.image_url}")
                    image_path = image_handler.download_image(item.image_url, item.title)
                    
                    if image_path:
                        # Resize image for optimal display
                        image_path = image_handler.resize_image(image_path, max_width=1200)
                
                # Create Jekyll post
                post_path = post_generator.create_post(
                    content_data={
                        'title': generated_content.get('title', item.title),
                        'content': generated_content.get('content', ''),
                        'tags': generated_content.get('tags', []),
                        'meta_description': generated_content.get('meta_description', item.description),
                        'source_url': item.link,
                        'source_name': item.source_name
                    },
                    image_path=image_path
                )
                
                if post_path:
                    created_post_paths.append(post_path)
                    # Mark the URL as processed to avoid future duplicates
                    processed_urls.append(item.link)
                    logger.info(f"Created post: {post_path}")
                else:
                    logger.error(f"Failed to create post for {item.title}")
                
            except Exception as e:
                logger.error(f"Error processing item {item.title}: {str(e)}")
                continue
        
        # Save processed URLs to history to prevent future duplicates
        if processed_urls:
            post_history.add_processed_urls(processed_urls)
            logger.info(f"Added {len(processed_urls)} URLs to post history")
        
        # Commit new posts and push changes to GitHub repository
        if created_post_paths:
            logger.info(f"Created {len(created_post_paths)} new posts, committing changes...")
            
            for path in created_post_paths:
                logger.info(f"New post: {path}")
            
            # Use a descriptive commit message
            current_date = datetime.now().strftime('%Y-%m-%d')
            commit_message = f"Add {len(created_post_paths)} new blog post(s) for {current_date}"
            
            # Commit and push ALL files in the github_repo directory
            logger.info("Committing ALL files in the github_repo directory to ensure everything is up-to-date")
            if github_manager.commit_and_push_changes(commit_message):
                logger.info("Successfully committed and pushed new posts to GitHub")
            else:
                logger.error("Failed to commit and push changes to GitHub")
                return False
        
        # Log post history stats
        stats = post_history.get_stats()
        logger.info(f"Post history stats: {stats['total_processed']} total processed URLs, {stats['recent_processed']} in the last 7 days")
        
        logger.info("Automated blog system completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
