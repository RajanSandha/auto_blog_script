"""
Custom exceptions for the automated blog system.
"""

class AutoBlogError(Exception):
    """Base exception for auto blog errors."""
    pass

class ContentGenerationError(AutoBlogError):
    """Raised when AI content generation fails."""
    pass

class PostCreationError(AutoBlogError):
    """Raised when blog post creation fails."""
    pass

class ImageProcessingError(AutoBlogError):
    """Raised when image processing fails."""
    pass

class JSONParsingError(AutoBlogError):
    """Raised when JSON parsing fails."""
    pass

class AIProviderError(AutoBlogError):
    """Raised when there are issues with AI provider integration."""
    pass