"""
AI factory module for creating different AI content generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AIGenerator(ABC):
    """Abstract base class for AI content generators."""
    
    @abstractmethod
    def generate_blog_post(self, 
                          article_data: Dict[str, Any], 
                          max_words: int = 1000,
                          style: str = "informative and engaging") -> Dict[str, Any]:
        """
        Generate a blog post based on the provided article data.
        
        Args:
            article_data: Dictionary containing article information
            max_words: Maximum word count for the generated post
            style: The writing style to use
            
        Returns:
            Dictionary containing the generated blog post content and metadata
        """
        pass


class AIFactory:
    """Factory class for creating AI content generators."""
    
    @staticmethod
    def create_generator(provider: str, api_key: str, model: Optional[str] = None) -> AIGenerator:
        """
        Create an AI generator for the specified provider.
        
        Args:
            provider: The AI provider name ('openai' or 'gemini')
            api_key: The API key for the AI provider
            model: The model name to use (optional)
            
        Returns:
            An AIGenerator instance for the requested provider
        
        Raises:
            ValueError: If the provider is not supported
        """
        provider = provider.lower()
        
        if provider == 'openai':
            from .openai_generator import OpenAIGenerator
            return OpenAIGenerator(api_key, model)
        elif provider == 'gemini':
            from .gemini_generator import GeminiGenerator
            return GeminiGenerator(api_key, model)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}") 