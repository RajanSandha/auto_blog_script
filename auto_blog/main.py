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
import requests
import json

# Import configuration and exceptions
from . import config
from .utils.exceptions import (
    AutoBlogError, ContentGenerationError, PostCreationError,
    ImageProcessingError, JSONParsingError, AIProviderError
)
from .rss_fetcher import RSSFetcher
from .ai_content import AIFactory
from .image_handler import ImageHandler
from .post_generator import PostGenerator
from .github_manager import GitHubManager
from .utils import create_directory, PostHistory
from .webhook_handler import wehbook_handler
from .scraper.sheets_handler import GoogleSheetsHandler
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

def initialize_components(cfg: Dict[str, Any], repo_dir: Path) -> tuple:
    """
    Initialize all system components with proper error handling.
    
    Args:
        cfg: Configuration dictionary
        repo_dir: Path to the repository directory
        
    Returns:
        Tuple of initialized components
        
    Raises:
        AutoBlogError: If component initialization fails
    """
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
        
        if not github_manager.ensure_repo_exists():
            raise AutoBlogError("Failed to ensure GitHub repository exists")
        
        if not github_manager.pull_latest_changes():
            raise AutoBlogError("Failed to pull latest changes from GitHub")
        
        # Initialize URL tracking sheet handler
        sheets_handler = GoogleSheetsHandler(
            credentials_file=cfg.get('google_credentials_file'),
            spreadsheet_id=cfg.get('spreadsheet_id'),
            sheet_name=cfg.get('sheet_name', 'Sheet1')
        )
        
        # Initialize post history tracker
        history_file = Path(__file__).parent.parent / "data" / "post_history.json"
        post_history = PostHistory(str(history_file))
        post_history.clean_old_entries()
        
        # Initialize RSS fetcher
        rss_fetcher = RSSFetcher(
            rss_urls=cfg['rss_feeds'],
            max_items_per_feed=cfg['max_rss_items'],
            max_age_days=cfg['max_article_age_days'],
            feed_timeout=15,
            article_timeout=8,
            known_problematic_feeds=[]
        )
        
        # Initialize AI content generator
        ai_factory = AIFactory()
        ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
        
        if ai_provider == 'gemini':
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            ai_generator = ai_factory.create_generator('gemini', gemini_api_key, gemini_model)
        else:
            openai_api_key = os.getenv('OPENAI_API_KEY')
            openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            ai_generator = ai_factory.create_generator('openai', openai_api_key, openai_model)
        
        # Initialize image handler and post generator
        images_dir = Path(repo_dir) / "assets" / "images"
        posts_dir = Path(repo_dir) / "_posts"
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(posts_dir, exist_ok=True)
        
        image_handler = ImageHandler(str(images_dir))
        post_generator = PostGenerator(
            posts_dir=str(posts_dir),
            site_url=f"https://{cfg['github_username']}.github.io/{cfg['github_repo']}",
            author_name=cfg['github_username'],
            image_dir=str(images_dir),
            available_categories=["Tech News", "AI", "Programming", "Web Development", "Data Science", "Daily News"],
            available_tags=["ai", "machine-learning", "programming", "web", "mobile", "cloud", "security", "data"]
        )
        
        return (github_manager, post_history, rss_fetcher, ai_generator, 
                image_handler, post_generator, sheets_handler)
                
    except Exception as e:
        raise AutoBlogError(f"Failed to initialize components: {str(e)}")

def filteredContent(content: str) -> str:
    """
    Filter content to remove unwanted elements and some specific replacements.
    Args:
        content: Original content string
    Returns:
        Filtered content string
    """
    try:
        # Remove tag like [STRING](URL) non http links
        # This regex matches markdown links that do not start with http
        content = re.sub(r'\[([^\]]+)\]\((?!http)[^\)]+\)', '', content)

        # Remove example.com links completely, including brackets if applied
        content = re.sub(r'\[([^\]]+)\]\(https?://(?:www\.)?example\.com\)', r'\1', content)
        content = re.sub(r'\bhttps?://(?:www\.)?example\.com\b', '', content)

        # Also replace link text with correct replacement
        content = re.sub(
            r'\[link text\]\((https?://[^\)]+)\)',
            r'[\1](\1)',
            content
        )

        # Remove ``` blocks, including optional "markdown" after ```
        content = re.sub(r'```(?:markdown)?[\s\S]*?```', '', content)
        
        # Replace specific unwanted phrases
        replacements = {
            "Engadget is a web magazine with obsessive daily coverage of everything new in gadgets and consumer electronics": "Engadget",
            "Ars Technica - All content": "Ars Technica"
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        return content.strip()
    
    except Exception as e:
        raise JSONParsingError(f"Failed to filter content: {str(e)}")
import re

def process_rss_item(item: Any, ai_generator: Any, image_handler: Any, 
                    post_generator: Any, post_history: Any) -> Optional[tuple]:
    """
    Process a single RSS item into a blog post.
    
    Args:
        item: RSS feed item
        ai_generator: AI content generator
        image_handler: Image handler
        post_generator: Post generator
        post_history: Post history tracker
        
    Returns:
        Tuple of post path and automation data or None if processing failed or content not relevant
        
    Raises:
        ContentGenerationError: If AI content generation fails
        ImageProcessingError: If image processing fails
        PostCreationError: If post creation fails
    """
    logger.info(f"Processing item: {item.title}")
    
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
        
        # Generate blog post content
        generated_content = ai_generator.generate_blog_post(
            article_data=article_data,
            max_words=1200,
            style="informative and engaging"
        )
        
        # Check if content is relevant to our niche
        if not generated_content.get('relevant_to_niche', True):
            logger.info(f"Article '{item.title}' not relevant to niche, skipping")
            return None
        
        # Process image if available
        image_path = None
        if item.image_url:
            try:
                image_path = image_handler.download_image(item.image_url, item.title)
                if image_path:
                    image_path = image_handler.resize_image(image_path, max_width=1200)
            except Exception as e:
                logger.warning(f"Image processing failed, continuing without image: {str(e)}")
        
        # Create post
        mdContent = filteredContent(generated_content.get('content', ''))
        sourceName = filteredContent(item.source_name)
        post_path, automationData = post_generator.create_post(
            content_data={
                'title': generated_content.get('title', item.title),
                'content': mdContent,
                'tags': generated_content.get('tags', []),
                'meta_description': generated_content.get('meta_description', item.description),
                'source_url': item.link,
                'source_name': sourceName,
                'categories': generated_content.get('categories', []),
                'keywords': generated_content.get('keywords', [])
            },
            image_path=image_path
        )
    
        
        return (post_path, automationData)
        
    except (ContentGenerationError, ImageProcessingError, PostCreationError) as e:
        logger.error(f"Failed to process item {item.title}: {str(e)}")
        raise
    except Exception as e:
        raise AutoBlogError(f"Unexpected error processing item {item.title}: {str(e)}")

def main():
    """
    Main function to run the automated blog system.
    Fetches RSS feeds, generates blog posts with AI, and pushes to GitHub repository.
    """
    logger.info("Starting automated blog system")
    
    try:
        # Validate configuration
        errors = config.validate_config()
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            sys.exit(1)
        
        # Get configuration
        cfg = config.get_config()
        repo_dir = Path(__file__).parent.parent / "github_repo"
        
        # Initialize components
        (github_manager, post_history, rss_fetcher, ai_generator,
         image_handler, post_generator, sheets_handler) = initialize_components(cfg, repo_dir)
        
        # Fetch RSS feeds
        all_items = rss_fetcher.fetch_all_feeds()
        logger.info(f"Fetched {len(all_items)} items from RSS feeds")

        # Get processed URLs from Google Sheet
        processed_urls = sheets_handler.get_processed_urls()
        logger.info(f"Got {len(processed_urls)} processed URLs from tracking sheet")
        
        # Filter out items that have been processed
        unprocessed_items = [
            item for item in all_items 
            if item.link not in processed_urls
        ]
        logger.info(f"{len(unprocessed_items)} items remaining after filter")
                
        if not unprocessed_items:
            logger.info("No new articles to process")
            return
        
        # Determine number of posts to generate
        load_dotenv(override=True)
        try:
            posts_per_day = int(os.getenv('POSTS_PER_DAY', '1'))
        except (ValueError, TypeError):
            posts_per_day = 1
            logger.warning(f"Using default posts_per_day: {posts_per_day}")
        
        num_posts = min(len(unprocessed_items), posts_per_day)
        created_post_paths = []
        processed_urls = []
        automation_payloads = []
        
        # Process items and create posts with retry logic
        current_item_idx = 0
        successfully_processed = 0
        
        while successfully_processed < num_posts and current_item_idx < len(unprocessed_items):
            max_retries = 2  # Maximum number of retries per post
            retry_count = 0
            success = False
            
            while not success and retry_count < max_retries:
                if current_item_idx >= len(unprocessed_items):
                    logger.warning("Ran out of unprocessed items to try")
                    break
                    
                item = unprocessed_items[current_item_idx]
                current_item_idx += 1
                
                if retry_count > 0:
                    logger.info(f"Retrying with new item after delay (attempt {retry_count+1})")
                    time.sleep(5)  # Delay for 5 seconds between retries
                
                try:
                    result = process_rss_item(
                        item, ai_generator, image_handler, post_generator, post_history
                    )
                    
                    if result:  # Post was successfully created and is relevant
                        post_path, automationData = result
                        created_post_paths.append(post_path)
                        processed_urls.append(item.link)
                        automation_payloads.append(automationData)
                        success = True
                        successfully_processed += 1
                        logger.info(f"Successfully processed item {item.title}")
                    else:
                        logger.info(f"Item {item.title} was not relevant, trying another")
                        retry_count += 1
                        
                except AutoBlogError as e:
                    logger.error(f"Failed to process item: {str(e)}")
                    retry_count += 1
        
        # Update post history and commit changes
        if processed_urls:
            current_date = datetime.now().strftime('%Y-%m-%d')
            commit_message = f"Add {len(created_post_paths)} new blog post(s) for {current_date}"
            
            if not github_manager.commit_and_push_changes(commit_message):
                logger.error("Failed to commit and push changes")
                return

            # Add processed URLs to tracking sheet
            for url in processed_urls:
                sheets_handler.add_processed_url(url)

        logger.info("Automated blog system completed successfully")
        
    except AutoBlogError as e:
        logger.error(f"System error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
