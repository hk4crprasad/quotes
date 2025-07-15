#!/usr/bin/env python3
"""
Image generation service using Azure OpenAI DALL-E with Azure Blob Storage
"""

import os
import requests
import base64
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO
from typing import Optional, Tuple

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from config import (
    AZURE_OPENAI_ENDPOINT, AZURE_DEPLOYMENT_NAME, 
    AZURE_API_VERSION, AZURE_SUBSCRIPTION_KEY,
    IMAGE_STYLE_TEMPLATES, AZURE_STORAGE_CONNECTION_STRING,
    AZURE_CONTAINER_NAME, AZURE_BLOB_FOLDER
)


class QuoteImageGenerator:
    """Azure OpenAI DALL-E image generator for quotes with Azure Blob Storage"""
    
    def __init__(self):
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.deployment = AZURE_DEPLOYMENT_NAME
        self.api_version = AZURE_API_VERSION
        self.subscription_key = AZURE_SUBSCRIPTION_KEY
        
        # Azure Blob Storage setup
        self.connection_string = AZURE_STORAGE_CONNECTION_STRING
        self.container_name = AZURE_CONTAINER_NAME
        self.blob_folder = AZURE_BLOB_FOLDER
        
        # Initialize blob service client
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        # Ensure container exists (it should already exist)
        try:
            self.container_client.get_container_properties()
        except Exception:
            # Container doesn't exist, but we won't create it since it's managed by Azure ML
            pass
        
    def _upload_image_to_blob(self, image_data: bytes, filename: str) -> str:
        """Upload image data to Azure Blob Storage"""
        try:
            # Create blob path with folder
            blob_path = f"{self.blob_folder}/{filename}"
            
            # Upload the image
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.upload_blob(image_data, overwrite=True)
            
            # Return the blob URL
            blob_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_path}"
            return blob_url
            
        except Exception as e:
            raise Exception(f"Failed to upload image to blob storage: {str(e)}")
    
    def _decode_image_to_bytes(self, b64_data: str) -> bytes:
        """Decode base64 image data to bytes"""
        try:
            image = Image.open(BytesIO(base64.b64decode(b64_data)))
            
            # Convert to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=90)
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
        except Exception as e:
            raise Exception(f"Failed to decode image: {str(e)}")
    
    def _build_image_prompt(self, quote_text: str, style: str = "paper") -> str:
        """Build the image generation prompt based on style"""
        template = IMAGE_STYLE_TEMPLATES.get(style, IMAGE_STYLE_TEMPLATES["paper"])
        return template.format(quote_text=quote_text).strip()
    
    def generate_quote_image(self, quote_text: str, style: str = "paper") -> Tuple[str, str]:
        """
        Generate an image for the given quote and upload to Azure Blob Storage
        
        Args:
            quote_text: The complete quote text (content only, no title)
            style: Image style (paper, modern, minimal)
            
        Returns:
            Tuple of (image_filename, blob_url)
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
            
            # Convert image to bytes
            image_bytes = self._decode_image_to_bytes(image_data['b64_json'])
            
            # Upload to Azure Blob Storage
            blob_url = self._upload_image_to_blob(image_bytes, filename)
            
            return filename, blob_url
            
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    def generate_quote_image_safe(self, quote_text: str, style: str = "paper") -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Safe version of generate_quote_image that returns error instead of raising
        
        Returns:
            Tuple of (filename, blob_url, error_message)
        """
        try:
            filename, blob_url = self.generate_quote_image(quote_text, style)
            return filename, blob_url, None
        except Exception as e:
            return None, None, str(e)
