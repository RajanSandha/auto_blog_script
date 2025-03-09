"""
Configuration module for the automated blog system.
Loads environment variables and provides configuration settings.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Determine the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Load environment variables from .env file
env_path = PROJECT_ROOT / '.env'
if not env_path.exists():
    print(f"Error: Environment file not found at {env_path}")
    print("Please create a .env file based on the .env.example template.")
    sys.exit(1)

load_dotenv(dotenv_path=env_path)

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_EMAIL = os.getenv('GITHUB_EMAIL')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')

# Blog Settings
BLOG_POST_PATH = os.getenv('BLOG_POST_PATH', '_posts')
BLOG_IMAGE_PATH = os.getenv('BLOG_IMAGE_PATH', 'assets/images')
POSTS_PER_DAY = int(os.getenv('POSTS_PER_DAY', '3'))
MAX_WORDS_PER_POST = int(os.getenv('MAX_WORDS_PER_POST', '1000'))

# AI Provider Settings
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')

# RSS Feed Configuration
RSS_FEEDS = os.getenv('RSS_FEEDS', '').split(',')
MAX_RSS_ITEMS = int(os.getenv('MAX_RSS_ITEMS', '25'))
MAX_ARTICLE_AGE_DAYS = int(os.getenv('MAX_ARTICLE_AGE_DAYS', '3'))

# Jekyll Settings
JEKYLL_CATEGORIES = os.getenv('JEKYLL_CATEGORIES', 'Technology,News,AI,Programming').split(',')
JEKYLL_TAGS = os.getenv('JEKYLL_TAGS', 'tech,news,programming,ai,development').split(',')
AUTHOR_NAME = os.getenv('AUTHOR_NAME', 'Blog Author')
SITE_URL = os.getenv('SITE_URL', f'https://{GITHUB_USERNAME}.github.io')

def validate_config() -> List[str]:
    """
    Validate the loaded configuration.
    Returns a list of error messages, empty if no errors.
    """
    errors = []
    
    # Validate GitHub configuration
    if not GITHUB_TOKEN:
        errors.append("GITHUB_TOKEN is required")
    if not GITHUB_USERNAME:
        errors.append("GITHUB_USERNAME is required")
    if not GITHUB_REPO:
        errors.append("GITHUB_REPO is required")
    if not GITHUB_EMAIL:
        errors.append("GITHUB_EMAIL is required")
        
    # Validate RSS Feeds
    if not RSS_FEEDS or RSS_FEEDS == ['']:
        errors.append("At least one RSS feed URL must be provided in RSS_FEEDS")
        
    # Validate AI Provider configuration
    if AI_PROVIDER not in ['openai', 'gemini']:
        errors.append(f"AI_PROVIDER must be 'openai' or 'gemini', got '{AI_PROVIDER}'")
        
    if AI_PROVIDER == 'openai' and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")
        
    if AI_PROVIDER == 'gemini' and not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is required when AI_PROVIDER is 'gemini'")
    
    return errors

def get_config() -> Dict[str, Any]:
    """
    Returns the entire configuration as a dictionary.
    """
    return {
        # GitHub Configuration
        'github_token': GITHUB_TOKEN,
        'github_username': GITHUB_USERNAME,
        'github_repo': GITHUB_REPO,
        'github_email': GITHUB_EMAIL,
        'github_branch': GITHUB_BRANCH,
        
        # Blog Settings
        'blog_post_path': BLOG_POST_PATH,
        'blog_image_path': BLOG_IMAGE_PATH,
        'posts_per_day': POSTS_PER_DAY,
        'max_words_per_post': MAX_WORDS_PER_POST,
        
        # AI Provider Settings
        'ai_provider': AI_PROVIDER,
        'openai_api_key': OPENAI_API_KEY,
        'openai_model': OPENAI_MODEL,
        'gemini_api_key': GEMINI_API_KEY,
        'gemini_model': GEMINI_MODEL,
        
        # RSS Feed Configuration
        'rss_feeds': RSS_FEEDS,
        'max_rss_items': MAX_RSS_ITEMS,
        'max_article_age_days': MAX_ARTICLE_AGE_DAYS,
        
        # Jekyll Settings
        'jekyll_categories': JEKYLL_CATEGORIES,
        'jekyll_tags': JEKYLL_TAGS,
        'author_name': AUTHOR_NAME,
        'site_url': SITE_URL,
    }
