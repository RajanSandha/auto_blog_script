#!/usr/bin/env python3
"""
Wrapper script to run the auto_blog system.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import and run the auto_blog main function
from auto_blog.main import main

if __name__ == "__main__":
    main() 