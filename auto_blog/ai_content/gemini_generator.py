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
        artical_image = article_data.get('image_url', '')
        
        #ToDo:  Add following prompt parameters to the prompt
        # -Suggest at least one internal link to a related article (use a placeholder if needed, e.g. [Related Article](Internal Link)).

        # Prepare the prompt
        prompt = f"""
        You are a professional tech blog writer with expertise in creating unique, high-quality, and valuable blog posts. Your task is to rewrite the provided article information into a well-structured, SEO-first blog post in markdown format of approximately {max_words} words. 

        IMPORTANT: Write in a clear, simple, and conversational style that is easy to read and understand for an average adult audience. Avoid jargon and complex sentences. Use short paragraphs, bullet points, and plain language wherever possible. Aim for a Flesch Reading Ease score of 60 or higher (average readability).

        Ensure the content is engaging, actionable, and adheres to the following guidelines:
        - Focus on providing maximum value by explaining concepts clearly and concisely.
        - Provide unique insights, analysis, or predictions about the topic (not just a summary).
        - Include at least one actionable takeaway or practical tip for readers.
        - If possible, cite reputable sources or include expert commentary (real or simulated).
        - Add a short FAQ section addressing common questions about the topic at end of the content.
        - Use logical sectioning with H2 and H3 subheadings that reflect search intent and improve readability.
        - Add a Key Takeaways or Summary section at the end.
        - Add the provided image URL at a relevant place in the blog post using markdown image syntax to make the post more engaging.
        - Optimize the content for SEO by:
          - Using each provided keyword at least once while maintaining readability.
          - Writing a compelling title tag and meta description (150–160 characters) that reflect primary keywords.
          - Suggesting a URL slug that aligns with the content and keywords.
        - Ensure the blog post is relevant to our niche (tech news, software, programming, AI, emerging technologies).
        - If the article is about any sale, discount, shopping deal, or promotional offer, or if the main focus is on deals or discounts, DO NOT create a blog post. Instead, return the JSON with empty strings or empty arrays for all fields except "relevant_to_niche": false.
        - Always return only this JSON structure (no extra text):        
        {{
            "title": "55-60 char suggested SEO-optimized title or '' if not relevant",
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
        Image URL: {artical_image if artical_image else 'Not provided'}
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