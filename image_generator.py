#!/usr/bin/env python3
"""
Image generation service using Azure OpenAI DALL-E
"""

import os
import requests
import base64
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO
from typing import Optional, Tuple

from config import (
    AZURE_OPENAI_ENDPOINT, AZURE_DEPLOYMENT_NAME, 
    AZURE_API_VERSION, AZURE_SUBSCRIPTION_KEY,
    IMAGE_STYLE_TEMPLATES
)


class QuoteImageGenerator:
    """Azure OpenAI DALL-E image generator for quotes"""
    
    def __init__(self):
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.deployment = AZURE_DEPLOYMENT_NAME
        self.api_version = AZURE_API_VERSION
        self.subscription_key = AZURE_SUBSCRIPTION_KEY
        self.images_dir = "generated_images"
        
        # Create images directory if it doesn't exist
        os.makedirs(self.images_dir, exist_ok=True)
        
    def _decode_and_save_image(self, b64_data: str, filename: str) -> str:
        """Decode base64 image data and save to file"""
        try:
            image = Image.open(BytesIO(base64.b64decode(b64_data)))
            filepath = os.path.join(self.images_dir, filename)
            image.save(filepath)
            return filepath
        except Exception as e:
            raise Exception(f"Failed to decode and save image: {str(e)}")
    
    def _build_image_prompt(self, quote_text: str, style: str = "paper") -> str:
        """Build the image generation prompt based on style"""
        template = IMAGE_STYLE_TEMPLATES.get(style, IMAGE_STYLE_TEMPLATES["paper"])
        return template.format(quote_text=quote_text).strip()
    
    def generate_quote_image(self, quote_text: str, style: str = "paper") -> Tuple[str, str]:
        """
        Generate an image for the given quote
        
        Args:
            quote_text: The complete quote text (title + content)
            style: Image style (paper, modern, minimal)
            
        Returns:
            Tuple of (image_filename, image_filepath)
        """
        try:
            # Build the custom prompt
            custom_prompt = self._build_image_prompt(quote_text, style)
            
            # Build request URL
            base_path = f'openai/deployments/{self.deployment}/images'
            params = f'?api-version={self.api_version}'
            generation_url = f"{self.endpoint}{base_path}/generations{params}"
            
            # Request body
            generation_body = {
                "prompt": custom_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "medium",
                "output_format": "jpeg",
            }
            
            # Call Azure OpenAI API
            generation_response = requests.post(
                generation_url,
                headers={
                    'Api-Key': self.subscription_key,
                    'Content-Type': 'application/json',
                },
                json=generation_body,
                timeout=60  # 60 second timeout
            )
            
            # Check response
            if generation_response.status_code != 200:
                raise Exception(f"API request failed with status {generation_response.status_code}: {generation_response.text}")
            
            # Parse response
            try:
                json_response = generation_response.json()
            except Exception as e:
                raise Exception(f"Failed to parse JSON response: {str(e)}")
            
            # Extract image data
            if 'data' not in json_response or not json_response['data']:
                raise Exception("No image data in response")
            
            # Get the first image
            image_data = json_response['data'][0]
            if 'b64_json' not in image_data:
                raise Exception("No base64 image data in response")
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"quote_image_{timestamp}_{unique_id}.jpeg"
            
            # Save image
            filepath = self._decode_and_save_image(image_data['b64_json'], filename)
            
            return filename, filepath
            
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    def generate_quote_image_safe(self, quote_text: str, style: str = "paper") -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Safe version of generate_quote_image that returns error instead of raising
        
        Returns:
            Tuple of (filename, filepath, error_message)
        """
        try:
            filename, filepath = self.generate_quote_image(quote_text, style)
            return filename, filepath, None
        except Exception as e:
            return None, None, str(e)
