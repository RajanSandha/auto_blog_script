"""
OpenAI content generator implementation.
"""

import openai
import re
from typing import Dict, Any, List, Optional
import logging
import json
from .ai_factory import AIGenerator

logger = logging.getLogger(__name__)

class OpenAIGenerator(AIGenerator):
    """
    Content generator using OpenAI's API.
    """
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the OpenAI content generator.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (defaults to gpt-3.5-turbo)
        """
        # Set API key for v0.28.0
        openai.api_key = api_key
        self.model = model or "gpt-3.5-turbo"
        logger.info(f"Initialized OpenAI generator with model: {self.model}")
    
    def generate_blog_post(self, 
                          article_data: Dict[str, Any], 
                          max_words: int = 1000,
                          style: str = "informative and engaging") -> Dict[str, Any]:
        """
        Generate a blog post based on the provided article data using OpenAI.
        
        Args:
            article_data: Dictionary containing article information
            max_words: Maximum word count for the generated post
            style: The writing style to use
            
        Returns:
            Dictionary containing the generated blog post content and metadata
        """
        # Extract relevant information from article data
        title = article_data.get('title', '')
        original_content = article_data.get('content', '')
        description = article_data.get('description', '')
        categories = article_data.get('categories', [])
        source_url = article_data.get('link', '')
        source_name = article_data.get('source_name', '')
        
        # Prepare the prompt
        system_prompt = f"""
        You are a professional tech blog writer. Your task is to create a well-structured, 
        {style} blog post based on the information provided. 
        
        The blog post should be:
        - Around {max_words} words
        - In a {style} style
        - Well-structured with headings, subheadings, and paragraphs
        - Include appropriate HTML formatting for headings (h2, h3, etc.) and emphasis
        - Written in your own words while maintaining factual accuracy
        - Include a proper introduction and conclusion
        
        The output should be in markdown format, including:
        1. A suggested title (if the original needs improvement)
        2. The blog post content
        3. 5-7 relevant tags as a comma-separated list
        4. A suggested meta description (150-160 characters)
        """
        
        # Create user prompt with article information
        user_prompt = f"""
        Here is the information about the article to rewrite:
        
        Original Title: {title}
        Source: {source_name}
        Original URL: {source_url}
        
        Original Description: {description}
        
        Categories/Tags: {', '.join(categories) if categories else 'Not provided'}
        
        Original Content:
        {original_content[:6000]}  # Limit content length to fit within context window
        
        Based on this information, create a unique and engaging blog post. 
        Format your response using the following JSON structure:
        
        {{
            "title": "Your suggested title",
            "content": "The full blog post content in markdown format",
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
            "meta_description": "A concise meta description"
        }}
        
        Return only valid JSON without any explanation or other text.
        """
        
        try:
            # Call OpenAI API (compatible with v0.28.0)
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2500,  # Adjust based on model and content needs
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Try to parse as JSON, but handle cases where the response might not be valid JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, extract and create a simple structure
                logger.warning("Response was not valid JSON, attempting to extract content")
                
                # Simple parsing for title
                title_match = re.search(r'"title":\s*"([^"]+)"', content)
                extract_title = title_match.group(1) if title_match else title
                
                # Simple parsing for content - extract everything between content quotes
                content_match = re.search(r'"content":\s*"(.*?)"(?=,\s*"tags"|,\s*"meta_description"|}})', content, re.DOTALL)
                extract_content = content_match.group(1) if content_match else content
                
                # Create a simple result
                result = {
                    "title": extract_title,
                    "content": extract_content,
                    "tags": [],
                    "meta_description": description[:160]
                }
            
            logger.info(f"Successfully generated blog post: {result.get('title', '')}")
            
            # Return the blog post information
            return {
                "title": result.get("title", title),
                "content": result.get("content", ""),
                "tags": result.get("tags", []),
                "meta_description": result.get("meta_description", ""),
                "source_url": source_url,
                "source_name": source_name
            }
            
        except Exception as e:
            logger.error(f"Error generating content with OpenAI: {str(e)}")
            # Return a minimal response in case of error
            return {
                "title": title,
                "content": f"Failed to generate content: {str(e)}",
                "tags": [],
                "meta_description": description,
                "source_url": source_url,
                "source_name": source_name
            } 