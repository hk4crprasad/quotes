#!/usr/bin/env python3
"""
Quote generator service using LangChain and OpenAI
"""

import json
import random
import time
from datetime import datetime
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from models import Quote
from config import (
    OPENAI_API_BASE, OPENAI_API_KEY, MODEL_NAME, TEMPERATURE,
    TITLE_PATTERNS, CONTENT_THEMES, QUOTE_GENERATOR_PROMPT,
    CAPTION_TEMPLATES, MOTIVATIONAL_HASHTAGS
)
from image_generator import QuoteImageGenerator
from video_generator import QuoteVideoGenerator


class ViralQuoteGenerator:
    """AI-powered viral quote generator"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_base=OPENAI_API_BASE,
            openai_api_key=OPENAI_API_KEY,
            model=MODEL_NAME,
            temperature=TEMPERATURE
        )
        self.image_generator = QuoteImageGenerator()
        self.video_generator = QuoteVideoGenerator()
        
    def _generate_ai_quote(self, theme: str = "mixed", target_audience: str = "gen-z", 
                          format_preference: Optional[str] = None) -> dict:
        """Generate quote using AI with variety"""
        variety_phrases = [
            "Create a completely unique and fresh perspective that hasn't been seen before",
            "Generate something that feels authentic and personally relatable", 
            "Make it feel deeply personal and genuine with original insights",
            "Ensure it sounds like authentic Gen Z language with fresh takes",
            "Focus on authentic emotional resonance with unique wisdom",
            "Create something screenshot-worthy with original perspective",
            "Generate fresh content that feels like a personal revelation"
        ]
        
        variety_instruction = random.choice(variety_phrases)
        
        # Add randomness to title selection
        if format_preference and format_preference != "string":
            suggested_title = format_preference
        else:
            suggested_title = random.choice(TITLE_PATTERNS)
        
        # Add randomness to theme content
        if theme and theme != "mixed":
            if theme in CONTENT_THEMES:
                content_inspiration = random.choice(CONTENT_THEMES[theme])
                theme_instruction = f"\nTheme focus: '{theme}' - consider ideas like: {content_inspiration}"
            else:
                theme_instruction = f"\nTheme focus: '{theme}'"
        else:
            themes = list(CONTENT_THEMES.keys())
            chosen_theme = random.choice(themes)
            content_inspiration = random.choice(CONTENT_THEMES[chosen_theme])
            theme_instruction = f"\nTheme focus: '{chosen_theme}' - consider ideas like: {content_inspiration}"
        
        # Add timestamp for uniqueness
        timestamp_variety = int(time.time()) % 1000
        
        # Construct the prompt with more variety
        user_prompt = f"""Generate ONE completely unique viral motivational quote in JSON format. {variety_instruction}.

IMPORTANT: Use a catchy title (3-4 words) similar to: "{suggested_title}"
{theme_instruction}

Target audience: {target_audience}
Uniqueness seed: {timestamp_variety}

Requirements:
- Respond with valid JSON only (title and content fields)
- Make it 100% unique and original (never repeat previous content)
- Use authentic {target_audience} language
- Ensure it's shareable and screenshot-worthy
- Provide genuine wisdom and fresh insight
- Keep content under 25 words
- Make title exactly 3-4 words (catchy and memorable)
- Ensure content complements the title perfectly"""

        messages = [
            SystemMessage(content=QUOTE_GENERATOR_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            response_content = response.content.strip()
            
            # Clean response if needed
            if response_content.startswith('```json'):
                response_content = response_content.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            quote_data = json.loads(response_content)
            
            return {
                "success": True,
                "title": quote_data.get("title", ""),
                "content": quote_data.get("content", ""),
                "theme": theme,
                "target_audience": target_audience
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "raw_response": response_content if 'response_content' in locals() else "No response"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Generation error: {str(e)}"
            }

    def _generate_caption(self, quote_title: str) -> str:
        """Generate social media caption with hashtags"""
        # Choose a random caption template
        caption_template = random.choice(CAPTION_TEMPLATES)
        
        # Add a line about the title
        title_line = f'"{quote_title}" - Let this sink in 💭'
        
        # Select random hashtags (15-20 hashtags for good reach)
        selected_hashtags = random.sample(MOTIVATIONAL_HASHTAGS, 18)
        hashtag_string = " ".join(selected_hashtags)
        
        # Combine all parts
        full_caption = f"{caption_template}\n\n{title_line}\n\n{hashtag_string}"
        
        return full_caption

    def generate_quote(self, theme: str = "mixed", target_audience: str = "gen-z", 
                      format_preference: Optional[str] = None) -> Quote:
        """Generate a viral quote using AI"""
        ai_result = self._generate_ai_quote(theme, target_audience, format_preference)
        
        if ai_result["success"]:
            # Generate caption with hashtags
            caption = self._generate_caption(ai_result["title"])
            
            quote = Quote(
                title=ai_result["title"],
                content=ai_result["content"],
                theme=ai_result["theme"],
                target_audience=ai_result["target_audience"],
                created_at=datetime.now().isoformat(),
                caption=caption
            )
            return quote
        else:
            # Return fallback quote on error
            return Quote(
                title="Error occurred",
                content=f"Quote generation failed: {ai_result.get('error', 'Unknown error')}",
                theme=theme,
                target_audience=target_audience,
                created_at=datetime.now().isoformat(),
                caption="Follow for more content! #motivation #quotes #inspiration"
            )
    
    def generate_quote_with_image(self, theme: str = "mixed", target_audience: str = "gen-z", 
                                 format_preference: Optional[str] = None, 
                                 image_style: str = "paper") -> tuple:
        """Generate a viral quote with optional image"""
        # First generate the quote
        quote = self.generate_quote(theme, target_audience, format_preference)
        
        # If quote generation failed, return quote with no image
        if quote.title == "Error occurred":
            return quote, None, None, quote.content
        
        # Generate image for the quote content only (without title)
        filename, blob_url, error = self.image_generator.generate_quote_image_safe(
            quote.content, image_style  # Only pass the content, not the title
        )
        
        return quote, filename, blob_url, error
    
    async def generate_quote_with_video(self, theme: str = "mixed", target_audience: str = "gen-z", 
                                 format_preference: Optional[str] = None, 
                                 image_style: str = "paper") -> tuple:
        """Generate a viral quote with image and video"""
        # First generate quote with image
        quote, image_filename, image_blob_url, image_error = self.generate_quote_with_image(
            theme, target_audience, format_preference, image_style
        )
        
        # If image generation failed, return with no video
        if image_error or not image_blob_url:
            return quote, image_filename, image_blob_url, None, None, image_error
        
        # Generate video using the image and AI-generated quote title
        video_filename, video_blob_url, video_error = await self.video_generator.generate_quote_video_safe(
            image_blob_url, quote.title  # Use the AI-generated title from the quote
        )
        
        return quote, image_filename, image_blob_url, video_filename, video_blob_url, video_error
