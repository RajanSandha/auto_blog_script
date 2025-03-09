#!/usr/bin/env python3
"""
Script to generate blog posts using AI.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import logging
import json
import feedparser
import requests
from typing import List, Dict, Optional
import openai
from dotenv import load_dotenv
import google.generativeai as genai
from bs4 import BeautifulSoup
import markdown
import frontmatter
import yaml
import re

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_tech_news() -> List[Dict]:
    """
    Fetch latest tech news from various sources.
    
    Returns:
        List of dictionaries containing news articles
    """
    try:
        # List of tech news RSS feeds
        feeds = [
            'https://techcrunch.com/feed/',
            'https://www.theverge.com/rss/index.xml',
            'https://www.wired.com/feed/rss',
            'https://feeds.feedburner.com/venturebeat/SZYF'
        ]
        
        articles = []
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:  # Get top 3 articles from each feed
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary if 'summary' in entry else '',
                        'published': entry.published if 'published' in entry else '',
                        'source': feed.feed.title if 'title' in feed.feed else feed_url
                    }
                    articles.append(article)
            except Exception as e:
                logger.warning(f"Error fetching from {feed_url}: {str(e)}")
                continue
        
        return articles
    except Exception as e:
        logger.error(f"Error fetching tech news: {str(e)}")
        return []

def generate_post_content(articles: List[Dict], topic: Optional[str] = None) -> Dict:
    """
    Generate a blog post using AI based on the fetched articles.
    
    Args:
        articles: List of news articles
        topic: Optional specific topic to focus on
        
    Returns:
        Dictionary containing the generated post content
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Try using Google's Gemini Pro first
        try:
            GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
            if GOOGLE_API_KEY:
                genai.configure(api_key=GOOGLE_API_KEY)
                model = genai.GenerativeModel('gemini-pro')
                
                # Prepare prompt
                articles_text = "\n\n".join([
                    f"Article from {a['source']}:\nTitle: {a['title']}\nSummary: {a['summary']}"
                    for a in articles
                ])
                
                prompt = f"""Based on these recent tech news articles:

{articles_text}

Write a comprehensive blog post that:
1. Analyzes and synthesizes the key trends and developments
2. Provides insightful commentary and analysis
3. Includes relevant technical details when appropriate
4. Maintains a professional but engaging tone
5. Includes a clear introduction and conclusion

{f'Focus on aspects related to {topic}.' if topic else ''}

Format the response as a YAML front matter followed by markdown content:
---
title: [generated title]
date: [current date/time]
description: [brief description]
tags: [relevant tags]
categories: [appropriate category]
---

[blog post content]
"""
                
                response = model.generate_content(prompt)
                if response and response.text:
                    return {'content': response.text, 'source': 'gemini'}
        
        except Exception as e:
            logger.warning(f"Error using Gemini Pro: {str(e)}")
        
        # Fallback to OpenAI
        try:
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            if OPENAI_API_KEY:
                openai.api_key = OPENAI_API_KEY
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a tech blogger writing insightful articles about technology news and trends."},
                        {"role": "user", "content": f"""Based on these recent tech news articles:

{articles_text}

Write a comprehensive blog post that:
1. Analyzes and synthesizes the key trends and developments
2. Provides insightful commentary and analysis
3. Includes relevant technical details when appropriate
4. Maintains a professional but engaging tone
5. Includes a clear introduction and conclusion

{f'Focus on aspects related to {topic}.' if topic else ''}

Format the response as a YAML front matter followed by markdown content:
---
title: [generated title]
date: [current date/time]
description: [brief description]
tags: [relevant tags]
categories: [appropriate category]
---

[blog post content]"""}
                    ]
                )
                
                if response and response.choices and response.choices[0].message.content:
                    return {'content': response.choices[0].message.content, 'source': 'openai'}
        
        except Exception as e:
            logger.warning(f"Error using OpenAI: {str(e)}")
        
        raise Exception("Failed to generate content using any available AI service")
    
    except Exception as e:
        logger.error(f"Error generating post content: {str(e)}")
        return {'content': '', 'source': None}

def save_post(content: str) -> bool:
    """
    Save the generated post to the _posts directory.
    
    Args:
        content: The post content including front matter
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Parse the content
        post = frontmatter.loads(content)
        
        # Generate filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        title_slug = re.sub(r'[^\w\-]', '', re.sub(r'\s+', '-', post['title'].lower()))
        filename = f"{date_str}-{title_slug}.md"
        
        # Get the project root directory
        project_root = Path(__file__).resolve().parent
        posts_dir = project_root / "github_repo" / "_posts"
        posts_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = posts_dir / filename
        
        # Save the file
        with open(filepath, 'w') as f:
            f.write(content)
        
        logger.info(f"Saved post to {filepath}")
        print(f"\nCreated new AI-generated post: {filepath}")
        print("You can now review and edit the post if needed.")
        print("After reviewing, commit and push your changes to publish the post.")
        
        return True
    
    except Exception as e:
        logger.error(f"Error saving post: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate a blog post using AI")
    parser.add_argument('--topic', help='Specific topic to focus on (optional)')
    args = parser.parse_args()
    
    # Fetch tech news
    print("Fetching latest tech news...")
    articles = fetch_tech_news()
    if not articles:
        print("Error: Could not fetch any tech news articles.")
        return 1
    
    # Generate post content
    print("Generating blog post content using AI...")
    result = generate_post_content(articles, args.topic)
    if not result['content']:
        print("Error: Could not generate post content.")
        return 1
    
    print(f"Successfully generated content using {result['source']}.")
    
    # Save the post
    if not save_post(result['content']):
        print("Error: Could not save the generated post.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 