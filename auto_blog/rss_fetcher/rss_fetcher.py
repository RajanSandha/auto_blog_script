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
import signal
import threading
import platform
import functools

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
                 max_age_days: int = 3, user_agent: Optional[str] = None,
                 feed_timeout: int = 15, article_timeout: int = 8,
                 known_problematic_feeds: List[str] = None):
        """
        Initialize the RSS Fetcher.
        
        Args:
            rss_urls: List of RSS feed URLs to fetch from
            max_items_per_feed: Maximum number of items to fetch per feed
            max_age_days: Only fetch items published within this many days
            user_agent: Custom user agent string for HTTP requests
            feed_timeout: Timeout in seconds for RSS feed fetching (default: 15)
            article_timeout: Timeout in seconds for article content fetching (default: 8)
            known_problematic_feeds: List of feed URLs known to cause timeouts (can be pattern matching)
        """
        self.rss_urls = rss_urls
        self.max_items_per_feed = max_items_per_feed
        self.max_age_days = max_age_days
        self.user_agent = user_agent or "AutoBlogger/1.0"
        self.feed_timeout = feed_timeout
        self.article_timeout = article_timeout
        
        # Keep track of problematic feeds
        self.problematic_feeds = known_problematic_feeds or []
        # Add common known problematic feeds if not explicitly provided
        if known_problematic_feeds is None:
            self.problematic_feeds = []  # Add others as you identify them
        
        # A dictionary to keep track of feed timeout occurrences
        self.feed_timeout_count = {}
        # After this many consecutive timeouts, a feed will be added to problematic_feeds
        self.max_consecutive_timeouts = 2
        
    # Timeout handler for feed parsing
    def _timeout_handler(self, signum, frame):
        """Handler for timeout signal."""
        raise TimeoutError(f"Timed out after {self.feed_timeout} seconds")
    
    # Thread-based timeout for platforms where signals don't work well
    def _timeout_wrapper(self, func, *args, **kwargs):
        """Wrapper for functions with timeout using threading (cross-platform)."""
        result = [None]
        error = [None]
        completed = [False]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
                completed[0] = True
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(self.feed_timeout)
        
        if not completed[0]:
            raise TimeoutError(f"Timed out after {self.feed_timeout} seconds")
        
        if error[0]:
            raise error[0]
            
        return result[0]
        
    def _is_problematic_feed(self, url: str) -> bool:
        """Check if a feed URL matches any known problematic feed patterns."""
        return any(problem in url for problem in self.problematic_feeds)
        
    def fetch_all_feeds(self) -> List[RSSItem]:
        """
        Fetch all configured RSS feeds and return a combined list of items.
        
        Returns:
            List of RSSItem objects from all feeds, sorted by published date
        """
        all_items = []
        
        for url in self.rss_urls:
            # Skip empty URLs
            if not url.strip():
                continue
                
            # Skip known problematic feeds
            if self._is_problematic_feed(url):
                logger.warning(f"Skipping known problematic feed: {url}")
                continue
                
            # Try to fetch the feed with retries
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(1, max_retries + 1):
                try:
                    items = self.fetch_feed(url)
                    all_items.extend(items)
                    
                    # Reset timeout count on success
                    if url in self.feed_timeout_count:
                        del self.feed_timeout_count[url]
                    
                    # Add a random delay between requests to be respectful to servers
                    time.sleep(random.uniform(1.0, 3.0))
                    break  # Success, break retry loop
                except TimeoutError as te:
                    # Track consecutive timeouts
                    self.feed_timeout_count[url] = self.feed_timeout_count.get(url, 0) + 1
                    
                    if self.feed_timeout_count[url] >= self.max_consecutive_timeouts:
                        # After multiple timeouts, add to problematic feeds list
                        if url not in self.problematic_feeds:
                            logger.error(f"Adding {url} to problematic feeds list after {self.feed_timeout_count[url]} consecutive timeouts")
                            self.problematic_feeds.append(url)
                    
                    logger.warning(f"Timeout fetching feed {url} - skipping after {self.feed_timeout} seconds")
                    break  # Don't retry on timeout, just skip this feed
                except Exception as e:
                    if attempt < max_retries:
                        logger.warning(f"Error fetching feed {url} (attempt {attempt}/{max_retries}): {str(e)}")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Failed to fetch feed {url} after {max_retries} attempts: {str(e)}")
        
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
        
        try:
            # Different timeout approach based on platform
            is_windows = platform.system().lower() == 'windows'
            
            if is_windows:
                # Use threading-based timeout on Windows
                try:
                    feed = self._timeout_wrapper(feedparser.parse, url)
                except TimeoutError:
                    logger.warning(f"Timeout parsing feed {url} after {self.feed_timeout} seconds")
                    raise
            else:
                # Set up a timeout using signal on Unix-like platforms
                old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.feed_timeout)
                
                try:
                    # Parse the feed with timeout
                    feed = feedparser.parse(url)
                    
                    # Disable the alarm
                    signal.alarm(0)
                except TimeoutError:
                    logger.warning(f"Timeout parsing feed {url} after {self.feed_timeout} seconds")
                    raise
                finally:
                    # Restore the original signal handler
                    signal.signal(signal.SIGALRM, old_handler)
                    # Disable the alarm in case of exception before the previous disable
                    signal.alarm(0)
            
            # Check if the feed was successfully parsed
            if hasattr(feed, 'bozo_exception') and feed.bozo_exception:
                logger.warning(f"Warning parsing feed {url}: {feed.bozo_exception}")
            
            # Check if feed has entries
            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"No entries found in feed {url}")
                return []
            
            # Get the feed title (source name)
            source_name = feed.feed.get('title', '') if hasattr(feed, 'feed') else ''
            
            # Calculate the cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
            
            items = []
            for entry_index, entry in enumerate(feed.entries[:self.max_items_per_feed]):
                try:
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
                        try:
                            link = entry.get('link', '')
                            if link:
                                content = self._fetch_article_content(link)
                            else:
                                logger.warning(f"No link found for entry {entry_index} in feed {url}")
                        except TimeoutError:
                            logger.warning(f"Timeout fetching article content for entry {entry_index} in feed {url}")
                        except Exception as content_error:
                            logger.error(f"Error fetching content for entry {entry_index} from {url}: {str(content_error)}")
                    
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
                except Exception as entry_error:
                    logger.error(f"Error processing entry {entry_index} from feed {url}: {str(entry_error)}")
                    continue
            
            logger.info(f"Fetched {len(items)} items from {url}")
            return items
                
        except TimeoutError:
            # Re-raise to be handled by fetch_all_feeds
            raise
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {str(e)}")
            return []
    
    def _parse_date(self, entry: Dict[str, Any]) -> datetime:
        """Parse the published date from an RSS entry."""
        try:
            date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
            
            for field in date_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    try:
                        time_struct = getattr(entry, field)
                        return datetime(*time_struct[:6])
                    except (TypeError, ValueError) as e:
                        logger.debug(f"Error parsing structured date field {field}: {str(e)}")
                        continue
            
            # If no parsed date is available, try to parse from string
            date_fields = ['published', 'updated', 'created']
            for field in date_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    try:
                        # Try to parse the date string, but fall back to current date on failure
                        from dateutil import parser
                        return parser.parse(getattr(entry, field))
                    except Exception as e:
                        logger.debug(f"Error parsing date string from {field}: {str(e)}")
                        continue
            
            # Default to current date if we couldn't parse anything
            logger.debug("No valid date found in entry, using current date")
            return datetime.now()
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
            return datetime.now()
    
    def _extract_author(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract author information from an RSS entry."""
        try:
            if hasattr(entry, 'author_detail') and hasattr(entry.author_detail, 'name'):
                return entry.author_detail.name
            elif hasattr(entry, 'author'):
                return entry.author
            elif hasattr(entry, 'dc_creator'):
                return entry.dc_creator
            return None
        except Exception as e:
            logger.error(f"Error extracting author: {str(e)}")
            return None
    
    def _extract_categories(self, entry: Dict[str, Any]) -> List[str]:
        """Extract categories from an RSS entry."""
        try:
            categories = []
            
            # Try to extract from tags
            if hasattr(entry, 'tags'):
                for tag in entry.tags:
                    try:
                        if hasattr(tag, 'term'):
                            categories.append(tag.term)
                        elif hasattr(tag, 'label'):
                            categories.append(tag.label)
                        elif isinstance(tag, dict):
                            if 'term' in tag:
                                categories.append(tag['term'])
                            elif 'label' in tag:
                                categories.append(tag['label'])
                    except Exception as tag_error:
                        logger.debug(f"Error processing tag: {str(tag_error)}")
                        continue
            
            # Try to extract from categories field
            if hasattr(entry, 'categories'):
                for category in entry.categories:
                    if isinstance(category, str):
                        categories.append(category)
            
            return categories
        except Exception as e:
            logger.error(f"Error extracting categories: {str(e)}")
            return []
    
    def _extract_image_url(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract the main image URL from an RSS entry."""
        try:
            # Try to get image from media content
            if hasattr(entry, 'media_content'):
                for media in entry.media_content:
                    if isinstance(media, dict) and 'url' in media:
                        return media['url']
                    elif hasattr(media, 'url'):
                        return media.url
                        
            # Try to get image from media thumbnail
            if hasattr(entry, 'media_thumbnail'):
                for thumbnail in entry.media_thumbnail:
                    if isinstance(thumbnail, dict) and 'url' in thumbnail:
                        return thumbnail['url']
                    elif hasattr(thumbnail, 'url'):
                        return thumbnail.url
            
            # Try to get image from enclosures
            if hasattr(entry, 'enclosures'):
                for enclosure in entry.enclosures:
                    if hasattr(enclosure, 'type') and 'image' in enclosure.type:
                        if hasattr(enclosure, 'href'):
                            return enclosure.href
                        elif isinstance(enclosure, dict) and 'href' in enclosure:
                            return enclosure['href']
            
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
        except Exception as e:
            # Log the error but don't crash the process
            logger.error(f"Error extracting image URL: {str(e)}")
            return None
    
    def _extract_content(self, entry: Dict[str, Any]) -> str:
        """Extract the full content from an RSS entry."""
        try:
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
            
            # If nothing else works, try to use description or title
            if hasattr(entry, 'description'):
                return entry.description
            elif hasattr(entry, 'title'):
                return entry.title
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            return ""
    
    def _fetch_article_content(self, url: str) -> str:
        """Fetch the full article content from the URL."""
        if not url:
            logger.warning("Attempted to fetch article with empty URL")
            return ""
            
        try:
            # Use the requests library with explicit timeout
            headers = {'User-Agent': self.user_agent}
            
            try:
                # First, try using the requests timeout
                response = requests.get(url, headers=headers, timeout=self.article_timeout)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Remove unwanted elements (common ads, nav, etc.)
                for unwanted in soup.select('script, style, nav, header, footer, .ad, .ads, .advertisement'):
                    try:
                        unwanted.decompose()
                    except Exception:
                        pass  # Ignore errors when removing elements
                
                # Look for article content in common article containers
                article_selectors = [
                    'article', '.post-content', '.entry-content', '.article-content',
                    '.post-body', '.article-body', '.story-body', '.story',
                    '.content', 'main', '#content', '#main'
                ]
                
                content = ""
                for selector in article_selectors:
                    try:
                        article = soup.select_one(selector)
                        if article:
                            # Clean up the article text
                            content = article.get_text(separator="\n", strip=True)
                            # If we found substantial content, break
                            if len(content) > 500:
                                break
                    except Exception as e:
                        logger.debug(f"Error extracting content with selector '{selector}': {str(e)}")
                        continue
                
                # If we still don't have enough content, just use the body
                if len(content) < 500:
                    try:
                        if soup.body:
                            content = soup.body.get_text(separator="\n", strip=True)
                    except Exception as e:
                        logger.debug(f"Error extracting content from body: {str(e)}")
                
                return content
            
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching article content from {url} after {self.article_timeout} seconds")
                return ""
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error fetching article content from {url}: {str(e)}")
                return ""
        
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