"""
String utilities for the automated blog system.
"""

import re
from typing import Optional

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to make it a valid filename.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces and other whitespace with underscores
    sanitized = re.sub(r'\s+', "_", sanitized)
    # Remove leading/trailing periods and spaces
    sanitized = sanitized.strip(". ")
    
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length, adding a suffix if truncated.
    
    Args:
        text: The string to truncate
        max_length: Maximum length of the truncated string
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    # Adjust max_length to account for suffix
    max_length = max_length - len(suffix)
    if max_length <= 0:
        return suffix
    
    # Truncate at the last space within max_length if possible
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix

def extract_words(text: str, count: int = 50) -> str:
    """
    Extract the first N words from a text.
    
    Args:
        text: The text to extract words from
        count: Number of words to extract
        
    Returns:
        String containing the first N words
    """
    words = text.split()
    return " ".join(words[:count])

def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate a URL-friendly slug from text.
    
    Args:
        text: The text to convert to a slug
        max_length: Maximum length of the slug
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Remove special characters
    slug = re.sub(r'[^\w\s-]', '', slug)
    
    # Replace whitespace with hyphens
    slug = re.sub(r'[\s_-]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    # Ensure the slug is not empty
    if not slug:
        slug = "post"
    
    return slug 