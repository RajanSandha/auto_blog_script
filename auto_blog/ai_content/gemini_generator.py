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
        You are a professional tech blog writer with expertise in creating unique, humanized, and friendly blog posts. Your task is to rewrite the provided article information into a well-structured, SEO-first blog post in markdown format approx ${max_words} words. Ensure the content is engaging, forward-thinking, and adheres to the following guidelines:

        - Use a friendly and conversational tone while maintaining professionalism.
        - Write in a way that is easy to read and understand, avoiding overly complex language.
        - Focus on providing value to the reader by explaining concepts clearly and concisely.
        - Structure the blog post with proper markdown syntax, including:
          - HTML headings (<h2>, <h3>, etc.) for logical sections.
          - Emphasis tags for important points.
          - Bullet points or numbered lists where appropriate.
        - Write an introduction that naturally incorporates primary keywords and hooks the reader.
        - Use logical sectioning with H2 and H3 subheadings that reflect search intent and improve readability.
        - Keep paragraphs short and concise for better readability.
        - Include placeholders for external links (e.g., [link text](External Link)) where relevant, but only if valid links are available.
        - Conclude with a clear call-to-action or summary that leaves a lasting impression.
        - Optimize the content for SEO by:
          - Using each provided keyword at least once while maintaining readability.
          - Writing a compelling title tag and meta description (150–160 characters) that reflect primary keywords.
          - Suggesting a URL slug that aligns with the content and keywords.
        - Ensure the blog post is relevant to our niche (tech news, software, programming, AI, emerging technologies). If the topic is not relevant, return the JSON with empty strings or empty arrays for all fields except "relevant_to_niche": false.
        - Always return only this JSON structure (no extra text):        
        {{
            "title": "suggested SEO-optimized title or '' if not relevant",
            "content": "full markdown blog post or '' if not relevant",
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
            "meta_description": "150–160 char SEO-friendly description or '' if not relevant",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
            "categories": ["category1", "category2", "category3", "category4", "category5"],
            "relevant_to_niche": true  # Boolean: true if the topic is relevant to our niche (tech news, software, programming, AI, emerging technologies), false otherwise
        }}
        
        Here is the information about the article to rewrite:
        Original Title: {title}
        Source: {source_name}
        Original URL: {source_url}
        Original Description: {description}
        Categories/Tags: {', '.join(categories) if categories else 'Not provided'}
        Original Content:
        {original_content[:6000]}  # Limit content length to fit within context window
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