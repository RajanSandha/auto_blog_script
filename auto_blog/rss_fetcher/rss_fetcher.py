"""
RSS Fetcher implementation for fetching and parsing RSS feeds.
"""

import feedparser
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging
import time
import random
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RSSItem:
    """Represents a single item from an RSS feed with all necessary information."""
    title: str
    link: str
    description: str
    content: str  # Full article content
    published_date: datetime
    author: Optional[str] = None
    categories: List[str] = None
    image_url: Optional[str] = None
    source_name: str = ""
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []


class RSSFetcher:
    """
    Fetches and parses RSS feeds, extracting relevant information
    for article generation.
    """
    
    def __init__(self, rss_urls: List[str], max_items_per_feed: int = 25, 
                 max_age_days: int = 3, user_agent: Optional[str] = None):
        """
        Initialize the RSS Fetcher.
        
        Args:
            rss_urls: List of RSS feed URLs to fetch from
            max_items_per_feed: Maximum number of items to fetch per feed
            max_age_days: Only fetch items published within this many days
            user_agent: Custom user agent string for HTTP requests
        """
        self.rss_urls = rss_urls
        self.max_items_per_feed = max_items_per_feed
        self.max_age_days = max_age_days
        self.user_agent = user_agent or "AutoBlogger/1.0"
        
    def fetch_all_feeds(self) -> List[RSSItem]:
        """
        Fetch all configured RSS feeds and return a combined list of items.
        
        Returns:
            List of RSSItem objects from all feeds, sorted by published date
        """
        all_items = []
        
        for url in self.rss_urls:
            try:
                items = self.fetch_feed(url)
                all_items.extend(items)
                # Add a random delay between requests to be respectful to servers
                time.sleep(random.uniform(1.0, 3.0))
            except Exception as e:
                logger.error(f"Error fetching feed {url}: {str(e)}")
        
        # Sort by published date, newest first
        all_items.sort(key=lambda x: x.published_date, reverse=True)
        return all_items
    
    def fetch_feed(self, url: str) -> List[RSSItem]:
        """
        Fetch and parse a single RSS feed.
        
        Args:
            url: URL of the RSS feed to fetch
            
        Returns:
            List of RSSItem objects from the feed
        """
        logger.info(f"Fetching RSS feed: {url}")
        
        # Parse the feed
        feed = feedparser.parse(url)
        
        # Get the feed title (source name)
        source_name = feed.feed.get('title', '') if hasattr(feed, 'feed') else ''
        
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        
        items = []
        for entry in feed.entries[:self.max_items_per_feed]:
            # Parse the published date
            published_date = self._parse_date(entry)
            
            # Skip if older than cutoff date
            if published_date < cutoff_date:
                continue
            
            # Extract image URL if available
            image_url = self._extract_image_url(entry)
            
            # Extract or fetch full content
            content = self._extract_content(entry)
            
            # If we couldn't get content from the RSS feed, try to fetch the article
            if not content or len(content) < 200:  # Arbitrary minimum length
                content = self._fetch_article_content(entry.link)
            
            # Create RSS item
            item = RSSItem(
                title=entry.get('title', ''),
                link=entry.get('link', ''),
                description=entry.get('summary', ''),
                content=content,
                published_date=published_date,
                author=self._extract_author(entry),
                categories=self._extract_categories(entry),
                image_url=image_url,
                source_name=source_name
            )
            
            items.append(item)
            
        logger.info(f"Fetched {len(items)} items from {url}")
        return items
    
    def _parse_date(self, entry: Dict[str, Any]) -> datetime:
        """Parse the published date from an RSS entry."""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                time_struct = getattr(entry, field)
                return datetime(*time_struct[:6])
        
        # If no parsed date is available, try to parse from string
        date_fields = ['published', 'updated', 'created']
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    # Try to parse the date string, but fall back to current date on failure
                    from dateutil import parser
                    return parser.parse(getattr(entry, field))
                except:
                    pass
        
        # Default to current date if we couldn't parse anything
        return datetime.now()
    
    def _extract_author(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract author information from an RSS entry."""
        if hasattr(entry, 'author_detail') and hasattr(entry.author_detail, 'name'):
            return entry.author_detail.name
        elif hasattr(entry, 'author'):
            return entry.author
        return None
    
    def _extract_categories(self, entry: Dict[str, Any]) -> List[str]:
        """Extract categories from an RSS entry."""
        categories = []
        
        if hasattr(entry, 'tags'):
            for tag in entry.tags:
                if hasattr(tag, 'term'):
                    categories.append(tag.term)
                elif hasattr(tag, 'label'):
                    categories.append(tag.label)
        
        return categories
    
    def _extract_image_url(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract the main image URL from an RSS entry."""
        # Try to get image from media content
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if 'url' in media and ('image' in media.get('type', '') or media.get('medium') == 'image'):
                    return media.url
                    
        # Try to get image from media thumbnail
        if hasattr(entry, 'media_thumbnail'):
            for thumbnail in entry.media_thumbnail:
                if 'url' in thumbnail:
                    return thumbnail.url
        
        # Try to get image from enclosures
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if hasattr(enclosure, 'type') and 'image' in enclosure.type:
                    return enclosure.href
        
        # Try to extract from content or summary
        content_fields = ['content', 'summary', 'description']
        for field in content_fields:
            if hasattr(entry, field):
                content_list = getattr(entry, field)
                if isinstance(content_list, list):
                    for content_item in content_list:
                        if isinstance(content_item, dict) and 'value' in content_item:
                            urls = self._extract_images_from_html(content_item.value)
                            if urls:
                                return urls[0]
                else:
                    urls = self._extract_images_from_html(getattr(entry, field))
                    if urls:
                        return urls[0]
        
        return None
    
    def _extract_content(self, entry: Dict[str, Any]) -> str:
        """Extract the full content from an RSS entry."""
        # Try to get content from the 'content' field
        if hasattr(entry, 'content'):
            for content in entry.content:
                if isinstance(content, dict) and 'value' in content:
                    return content.value
        
        # Try to get from other fields
        for field in ['summary_detail', 'summary']:
            if hasattr(entry, field):
                field_value = getattr(entry, field)
                if isinstance(field_value, dict) and 'value' in field_value:
                    return field_value.value
                else:
                    return str(field_value)
        
        return ""
    
    def _fetch_article_content(self, url: str) -> str:
        """Fetch the full article content from the URL."""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove unwanted elements (common ads, nav, etc.)
            for unwanted in soup.select('script, style, nav, header, footer, .ad, .ads, .advertisement'):
                unwanted.decompose()
            
            # Look for article content in common article containers
            article_selectors = [
                'article', '.post-content', '.entry-content', '.article-content',
                '.post-body', '.article-body', '.story-body', '.story',
                '.content', 'main', '#content', '#main'
            ]
            
            content = ""
            for selector in article_selectors:
                article = soup.select_one(selector)
                if article:
                    # Clean up the article text
                    content = article.get_text(separator="\n", strip=True)
                    # If we found substantial content, break
                    if len(content) > 500:
                        break
            
            # If we still don't have enough content, just use the body
            if len(content) < 500:
                content = soup.body.get_text(separator="\n", strip=True)
            
            return content
        
        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {str(e)}")
            return ""
    
    def _extract_images_from_html(self, html_content: str) -> List[str]:
        """Extract image URLs from HTML content."""
        if not html_content:
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            images = soup.find_all('img')
            urls = []
            
            for img in images:
                if img.has_attr('src'):
                    urls.append(img['src'])
                elif img.has_attr('data-src'):
                    urls.append(img['data-src'])
                    
            return urls
        except Exception as e:
            logger.error(f"Error extracting image URLs from HTML: {str(e)}")
            return [] 