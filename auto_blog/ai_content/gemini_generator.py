"""
Google Gemini content generator implementation.
"""

import google.generativeai as genai
from typing import Dict, Any, List, Optional
import logging
import json
from .ai_factory import AIGenerator

logger = logging.getLogger(__name__)

class GeminiGenerator(AIGenerator):
    """
    Content generator using Google's Gemini AI.
    """
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the Gemini content generator.
        
        Args:
            api_key: Google Gemini API key
            model: Gemini model to use (defaults to gemini-pro)
        """
        genai.configure(api_key=api_key)
        self.model = model or "gemini-pro"
        self.genai = genai
        logger.info(f"Initialized Gemini generator with model: {self.model}")
    
    def generate_blog_post(self, 
                          article_data: Dict[str, Any], 
                          max_words: int = 1000,
                          style: str = "informative and engaging") -> Dict[str, Any]:
        """
        Generate a blog post based on the provided article data using Gemini.
        
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
        prompt = f"""
        You are a professional tech blog writer. Your task is to create a well-structured, warm, humanized, 
        {style} blog post based on the information provided. Use clear, everyday language and an encouraging, forward-thinking tone.
        
        The blog post should be:
        - Around {max_words} words
        - In a {style} style
        - Well-structured with headings, subheadings, and paragraphs
        - Include appropriate HTML formatting for headings (h2, h3, etc.) and emphasis
        - Written in your own words while maintaining factual accuracy
        - Include a proper introduction and conclusion
        
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
            "meta_description": "A concise meta description (150-160 characters)",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
            "categories": ["category1", "category2", "category3", "category4", "category5"],
            "relevant_to_niche": true  # Boolean: true if the topic is relevant to our niche (tech, software, programming, artificial intelligence and more.), false otherwise

        }}
        
        Return only valid JSON without any explanation or other text.Only generate blogs relevant to Tech, Software, and Programming. Do not create posts about gaming, TV series, deals, offers, promotions, or unrelated topics. Always set relevant_to_niche accordingly: true when the content fits our tech-focused niche, false when it does not. Based on that flag, you can skip writing non-relevant posts or mark them clearly.

        """
        
        try:
            # Get the model
            model = self.genai.GenerativeModel(self.model)
            
            # Configure response
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            def _generate_and_parse():
                """
                Helper function to generate content and parse JSON. Returns (result_dict, error_msg).
                """
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                content_text = response.text
                json_start = content_text.find('{')
                json_end = content_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = content_text[json_start:json_end]
                    try:
                        result = json.loads(json_content)
                        return result, None
                    except json.JSONDecodeError as json_err:
                        return None, f"JSONDecodeError: {str(json_err)}"
                else:
                    # No JSON found at all
                    return None, "No JSON structure found in response."

            # First attempt
            result, error_msg = _generate_and_parse()
            if result is None:
                logger.warning(f"First attempt to parse Gemini response failed: {error_msg}. Retrying once...")
                # Retry once more
                result, error_msg = _generate_and_parse()
                if result is None:
                    logger.error(f"Second attempt to parse Gemini response failed: {error_msg}")
                    # throw an error
                    raise Exception(f"Gemini response could not be parsed as JSON after 2 attempts: {error_msg}")

            logger.info(f"Successfully generated blog post: {result.get('title', '')}")
            # Return the blog post information
            return {
                "title": result.get("title", title),
                "content": result.get("content", ""),
                "tags": result.get("tags", []),
                "meta_description": result.get("meta_description", ""),
                "source_url": source_url,
                "source_name": source_name,
                "categories": result.get("categories", []),
                "keywords": result.get("keywords", []),
                "relevant_to_niche": result.get("relevant_to_niche", True)  # Include the relevance flag
            }
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            raise Exception(f"Error generating content with Gemini: {str(e)}")