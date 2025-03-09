"""
File utilities for the automated blog system.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def create_directory(directory_path: str) -> bool:
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path: Path to the directory to create
        
    Returns:
        True if the directory exists or was created successfully, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {str(e)}")
        return False

def get_local_file_path(base_path: str, relative_path: str) -> str:
    """
    Get the absolute path to a file based on the base path and relative path.
    
    Args:
        base_path: Base directory path
        relative_path: Relative path from the base directory
        
    Returns:
        Absolute path to the file
    """
    return os.path.join(base_path, relative_path)

def ensure_file_exists(file_path: str, create_parent_dirs: bool = True) -> bool:
    """
    Ensure a file exists. Creates parent directories if needed.
    
    Args:
        file_path: Path to the file
        create_parent_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        True if the file exists, False otherwise
    """
    file = Path(file_path)
    
    # Check if the file exists
    if file.exists():
        return True
    
    # Create parent directories if needed
    if create_parent_dirs:
        parent_dir = file.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created parent directories for {file_path}")
            except Exception as e:
                logger.error(f"Error creating parent directories for {file_path}: {str(e)}")
                return False
    
    # Create an empty file
    try:
        file.touch()
        logger.info(f"Created empty file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating empty file {file_path}: {str(e)}")
        return False

def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The file extension (including the period)
    """
    return os.path.splitext(file_path)[1] 