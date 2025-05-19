"""
Webhook handler for managing webhook calls and data processing.
"""

import os
import json
import logging
import random
import requests
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def call_webhook(data: Dict[str, Any], webhook_url: str = '') -> List[str]:
    """
    Send data to a webhook endpoint via POST and parse the response.
    Args:
        data: The data dictionary to send
        webhook_url: Webhook URL to call
    Returns:
        List of processed URLs, or empty list if error
    """
    url = webhook_url
    if not url:
        logger.error("Webhook URL not set in environment or passed as argument.")
        return []
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
        logger.info(f"Webhook response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Webhook POST failed: {response.status_code} - {response.text}")
            return []
            
        # Parse response
        try:
            response_data = response.json()
            # Extract URLs from the response format [{'0': url}, ...]
            processed_urls = []
            for item in response_data:
                if isinstance(item, dict) and '0' in item:
                    url = item['0']
                    if url != 'source_url':  # Skip header row
                        processed_urls.append(url)
            logger.info(f"Extracted {len(processed_urls)} processed URLs from webhook response")
            return processed_urls
        except json.JSONDecodeError:
            logger.error("Failed to parse webhook response as JSON")
            return []
            
    except Exception as e:
        logger.error(f"Exception during webhook POST: {str(e)}")
        return []

def filter_unprocessed_items(all_items: List[Any], processed_urls: List[str]) -> List[Any]:
    """
    Filter out items that have already been processed according to webhook data.
    Args:
        all_items: List of RSS items
        processed_urls: List of URLs that have been processed
    Returns:
        List of unprocessed RSS items
    """
    if not processed_urls:
        logger.warning("No processed URLs provided, returning all items")
        return all_items
    
    unprocessed = [
        item for item in all_items 
        #filter out items that have already been processed
        if not any(item.link == url for url in processed_urls)
        #filter out items where link or description contains 'sale' word
        if 'sale' not in item.link.lower() and 'sale' not in item.description.lower()
        #filter out items where image_url is not a valid URL
        if item.image_url is not None and item.image_url.startswith('http')
    ]
    
    # Shuffle the list randomly to avoid processing items in same order
    random.shuffle(unprocessed)
    return unprocessed

def send_automation_data(automation_data: Dict[str, Any], webhook_url: str = '') -> bool:
    """
    Send automation data to webhook.
    Args:
        automation_data: Dictionary containing automation data
        webhook_url: Webhook URL to send data to
    Returns:
        True if successful, False otherwise
    """
    try:
        response = call_webhook(automation_data, webhook_url)
        return bool(response)
    except Exception as e:
        logger.error(f"Failed to send automation data: {str(e)}")
        return False