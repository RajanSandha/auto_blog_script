"""
Post history tracker for the automated blog system.
Keeps track of previously generated posts to avoid duplicates.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

class PostHistory:
    """
    Tracks post history to prevent generating duplicate posts.
    Stores information about processed URLs in a JSON file.
    """
    
    def __init__(self, history_file_path: str, max_history_days: int = 90):
        """
        Initialize the post history tracker.
        
        Args:
            history_file_path: Path to the JSON file for storing history
            max_history_days: Maximum number of days to keep history for
        """
        self.history_file_path = history_file_path
        self.max_history_days = max_history_days
        self.history = self._load_history()
        
    def _load_history(self) -> Dict[str, str]:
        """
        Load post history from JSON file.
        
        Returns:
            Dictionary with URLs as keys and dates as values
        """
        if not os.path.exists(self.history_file_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.history_file_path), exist_ok=True)
            return {}
        
        try:
            with open(self.history_file_path, 'r') as f:
                history = json.load(f)
                logger.info(f"Loaded {len(history)} entries from post history")
                return history
        except Exception as e:
            logger.error(f"Error loading post history: {str(e)}")
            return {}
    
    def _save_history(self):
        """Save post history to JSON file."""
        try:
            with open(self.history_file_path, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"Saved {len(self.history)} entries to post history")
        except Exception as e:
            logger.error(f"Error saving post history: {str(e)}")
    
    def clean_old_entries(self):
        """Remove entries older than max_history_days."""
        if not self.history:
            return
        
        cutoff_date = (datetime.now() - timedelta(days=self.max_history_days)).strftime('%Y-%m-%d')
        old_count = len(self.history)
        
        # Filter out old entries
        self.history = {
            url: date for url, date in self.history.items()
            if date >= cutoff_date
        }
        
        new_count = len(self.history)
        if old_count != new_count:
            logger.info(f"Cleaned {old_count - new_count} old entries from post history")
            self._save_history()
    
    def add_processed_url(self, url: str):
        """
        Mark a URL as processed.
        
        Args:
            url: The URL that was processed
        """
        self.history[url] = datetime.now().strftime('%Y-%m-%d')
        self._save_history()
    
    def add_processed_urls(self, urls: List[str]):
        """
        Mark multiple URLs as processed.
        
        Args:
            urls: List of URLs that were processed
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        for url in urls:
            self.history[url] = current_date
        self._save_history()
    
    def is_url_processed(self, url: str) -> bool:
        """
        Check if a URL has already been processed.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL has been processed, False otherwise
        """
        return url in self.history
    
    def filter_unprocessed_urls(self, urls: List[str]) -> List[str]:
        """
        Filter a list of URLs to only include those that haven't been processed.
        
        Args:
            urls: List of URLs to filter
            
        Returns:
            List of URLs that haven't been processed
        """
        return [url for url in urls if not self.is_url_processed(url)]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the post history.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_processed": len(self.history),
            "recent_processed": sum(1 for date in self.history.values() 
                                   if date >= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        } 