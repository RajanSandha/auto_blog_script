"""
Image handler implementation for downloading, processing, and storing images.
"""

import os
import requests
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
from urllib.parse import urlparse, unquote
from PIL import Image
import io
import random
import time

logger = logging.getLogger(__name__)

class ImageHandler:
    """
    Handles downloading, processing, and storing images for blog posts.
    """
    
    def __init__(self, image_dir: str):
        """
        Initialize the image handler.
        
        Args:
            image_dir: Directory to store downloaded images
        """
        self.image_dir = image_dir
        
        # Create the image directory if it doesn't exist
        os.makedirs(self.image_dir, exist_ok=True)
        logger.info(f"Image handler initialized with directory: {self.image_dir}")
    
    def download_image(self, url: str, article_title: str = "") -> Optional[str]:
        """
        Download an image from a URL and save it to the image directory.
        
        Args:
            url: URL of the image to download
            article_title: Title of the article (used for filename generation)
            
        Returns:
            Path to the downloaded image, or None if download failed
        """
        if not url:
            logger.warning("No image URL provided")
            return None
        
        try:
            # Generate a clean filename based on article title and URL
            filename = self._generate_filename(url, article_title)
            filepath = os.path.join(self.image_dir, filename)
            
            # Check if the file already exists
            if os.path.exists(filepath):
                logger.info(f"Image already exists at {filepath}")
                return filepath
            
            # Download the image
            logger.info(f"Downloading image from {url}")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Process the image
            img = Image.open(io.BytesIO(response.content))
            
            # Save the image to disk
            img.save(filepath)
            logger.info(f"Image saved to {filepath}")
            
            return filepath
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            return None
    
    def download_images_from_list(self, urls: List[str], article_title: str = "") -> List[str]:
        """
        Download multiple images from a list of URLs.
        
        Args:
            urls: List of image URLs to download
            article_title: Title of the article
            
        Returns:
            List of paths to downloaded images
        """
        image_paths = []
        
        for url in urls:
            # Add a small delay between downloads to be respectful to servers
            time.sleep(random.uniform(0.5, 1.5))
            
            path = self.download_image(url, article_title)
            if path:
                image_paths.append(path)
        
        return image_paths
    
    def download_article_image(self, article_data: dict) -> Optional[str]:
        """
        Download the main image from an article.
        
        Args:
            article_data: Dictionary containing article information
            
        Returns:
            Path to the downloaded image, or None if download failed
        """
        image_url = article_data.get('image_url')
        title = article_data.get('title', '')
        
        if not image_url:
            logger.warning(f"No image URL found for article: {title}")
            return None
        
        return self.download_image(image_url, title)
    
    def get_image_dimensions(self, image_path: str) -> Tuple[int, int]:
        """
        Get the dimensions of an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Tuple of (width, height), or (0, 0) if the image couldn't be opened
        """
        try:
            with Image.open(image_path) as img:
                return img.size
        except Exception as e:
            logger.error(f"Error getting image dimensions for {image_path}: {str(e)}")
            return (0, 0)
    
    def resize_image(self, image_path: str, max_width: int = 800) -> Optional[str]:
        """
        Resize an image to a maximum width, maintaining aspect ratio.
        
        Args:
            image_path: Path to the image
            max_width: Maximum width for the resized image
            
        Returns:
            Path to the resized image, or None if resizing failed
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Only resize if the image is wider than max_width
                if width > max_width:
                    # Calculate new height to maintain aspect ratio
                    new_height = int(height * (max_width / width))
                    resized_img = img.resize((max_width, new_height), Image.LANCZOS)
                    
                    # Save the resized image (overwrite original)
                    resized_img.save(image_path)
                    logger.info(f"Image resized to {max_width}x{new_height}: {image_path}")
                
                return image_path
        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {str(e)}")
            return None
    
    def _generate_filename(self, url: str, article_title: str = "") -> str:
        """
        Generate a filename for the downloaded image.
        
        Args:
            url: URL of the image
            article_title: Title of the article
            
        Returns:
            Generated filename
        """
        # Try to extract filename from URL
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        original_filename = os.path.basename(path)
        
        # Extract extension
        ext = os.path.splitext(original_filename)[1].lower()
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'  # Default to jpg if extension is not recognized
        
        # Create a base filename from the article title or URL
        if article_title:
            # Clean up article title for filename
            base_filename = ''.join(c if c.isalnum() else '_' for c in article_title)
            base_filename = base_filename.lower()[:50]  # Limit length
        else:
            # Use a hash of the URL if no title is provided
            base_filename = hashlib.md5(url.encode()).hexdigest()[:16]
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        return f"{base_filename}_{timestamp}{ext}" 