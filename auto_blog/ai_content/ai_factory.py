"""
AI factory module for creating different AI content generators.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import logging
from ..utils.exceptions import AIProviderError, JSONParsingError, ContentGenerationError

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
            
        Raises:
            ContentGenerationError: If content generation fails
            JSONParsingError: If there are issues parsing JSON responses
        """
        pass

    def _validate_response(self, response: Dict[str, Any]) -> None:
        """
        Validate the AI response contains required fields.
        
        Args:
            response: The response dictionary to validate
            
        Raises:
            ContentGenerationError: If required fields are missing
        """
        required_fields = ['title', 'content']
        missing_fields = [field for field in required_fields if not response.get(field)]
        
        if missing_fields:
            raise ContentGenerationError(
                f"AI response missing required fields: {', '.join(missing_fields)}"
            )

    def _parse_json_safely(self, json_str: str) -> Dict[str, Any]:
        """
        Safely parse JSON string with error handling.
        
        Args:
            json_str: The JSON string to parse
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            JSONParsingError: If JSON parsing fails
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise JSONParsingError(f"Failed to parse AI response as JSON: {str(e)}")

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
            AIProviderError: If provider initialization fails or is unsupported
        """
        if not api_key:
            raise AIProviderError(f"API key is required for {provider}")

        provider = provider.lower()
        try:
            if provider == 'openai':
                from .openai_generator import OpenAIGenerator
                return OpenAIGenerator(api_key, model)
            elif provider == 'gemini':
                from .gemini_generator import GeminiGenerator
                return GeminiGenerator(api_key, model)
            else:
                raise AIProviderError(f"Unsupported AI provider: {provider}")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize {provider} generator: {str(e)}")