#!/usr/bin/env python3
"""
Video generation service using MoviePy and Azure Blob Storage
"""

import os
import uuid
import tempfile
from datetime import datetime
from typing import Optional, Tuple
from io import BytesIO

from moviepy import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.fx.FadeIn import FadeIn
from azure.storage.blob import BlobServiceClient
import requests

from config import (
    AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME, AZURE_VIDEO_FOLDER,
    DEFAULT_AUDIO_FILE, VIDEO_SIZE, VIDEO_TITLE, FADE_IN_DELAY, FADE_IN_DURATION,
    VIDEO_FPS, BACKGROUND_COLOR, BANNER_COLOR, BANNER_HEIGHT, BANNER_Y_POSITION,
    TITLE_FONT_SIZE, TITLE_COLOR
)


class QuoteVideoGenerator:
    """Generate quote videos with MoviePy and upload to Azure Blob Storage"""
    
    def __init__(self):
        self.connection_string = AZURE_STORAGE_CONNECTION_STRING
        self.container_name = AZURE_CONTAINER_NAME
        self.video_folder = AZURE_VIDEO_FOLDER
        
        # Initialize blob service client
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        # Video settings
        self.audio_file = DEFAULT_AUDIO_FILE
        self.video_size = VIDEO_SIZE
        self.title_text = VIDEO_TITLE
        self.fade_in_delay = FADE_IN_DELAY
        self.fade_in_duration = FADE_IN_DURATION
        
    def _download_image_from_url(self, image_url: str) -> str:
        """Download image from URL to temporary file"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg')
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            raise Exception(f"Failed to download image from URL: {str(e)}")
    
    def _upload_video_to_blob(self, video_path: str, filename: str) -> str:
        """Upload video file to Azure Blob Storage"""
        try:
            # Create blob path with folder
            blob_path = f"{self.video_folder}/{filename}"
            
            # Upload the video
            blob_client = self.container_client.get_blob_client(blob_path)
            
            with open(video_path, 'rb') as video_file:
                blob_client.upload_blob(video_file, overwrite=True)
            
            # Return the blob URL
            blob_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_path}"
            return blob_url
            
        except Exception as e:
            raise Exception(f"Failed to upload video to blob storage: {str(e)}")
    
    def generate_quote_video(self, image_url: str, quote_title: str = None) -> Tuple[str, str]:
        """
        Generate a quote video with the given image and upload to Azure Blob Storage
        
        Args:
            image_url: URL of the quote image (from blob storage)
            quote_title: The AI-generated quote title to use in the video
            
        Returns:
            Tuple of (video_filename, video_blob_url)
        """
        temp_image_path = None
        temp_video_path = None
        audio_clip = None
        final_video = None
        
        try:
            # Check if audio file exists
            if not os.path.exists(self.audio_file):
                raise Exception(f"Audio file not found: {self.audio_file}")
            
            print(f"🎵 Audio file found: {self.audio_file}")
            
            # Download image from URL to temporary file
            temp_image_path = self._download_image_from_url(image_url)
            print(f"🖼️ Image downloaded to: {temp_image_path}")

            print("🔊 Loading audio and image...")
            audio_clip = AudioFileClip(self.audio_file)
            video_duration = audio_clip.duration
            print(f"⏱️ Video duration: {video_duration} seconds")
            
            # Background
            background_clip = ColorClip(
                size=self.video_size, 
                color=BACKGROUND_COLOR
            ).with_duration(video_duration)
            
            # Use font file path directly for better compatibility
            font_main = "/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf"
            if not os.path.exists(font_main):
                # Fallback to standard DejaVu Sans
                font_main = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                if not os.path.exists(font_main):
                    # Final fallback - use default font
                    font_main = None
            
            print(f"📝 Using font: {font_main}")
            print("📝 Creating text clips...")
            
            # Banner just above the quote
            banner_y = BANNER_Y_POSITION
            banner_height = BANNER_HEIGHT
            
            # White banner background
            banner_clip = ColorClip(
                size=(self.video_size[0], banner_height), 
                color=BANNER_COLOR
            ).with_duration(video_duration).with_position(("center", banner_y))
            
            # Title text centered inside banner
            title_text = quote_title if quote_title else self.title_text
            
            # Dynamic font sizing based on text length
            if len(title_text) > 15:
                dynamic_font_size = 35  # Smaller for longer titles
                print(f"📝 Long title ({len(title_text)} chars), using font size: {dynamic_font_size}")
            elif len(title_text) > 10:
                dynamic_font_size = 40  # Medium for medium titles
                print(f"📝 Medium title ({len(title_text)} chars), using font size: {dynamic_font_size}")
            else:
                dynamic_font_size = TITLE_FONT_SIZE  # Default for short titles
                print(f"📝 Short title ({len(title_text)} chars), using font size: {dynamic_font_size}")
            
            print(f"📝 Title text: '{title_text}'")
            
            try:
                title_clip = TextClip(
                    text=title_text,
                    font=font_main,
                    method='caption',
                    size=(self.video_size[0] - 200, banner_height - 40),  # More padding and height constraint
                    font_size=dynamic_font_size,
                    color=TITLE_COLOR
                ).with_duration(video_duration).with_position(("center", banner_y + 20))  # Better vertical centering
            except Exception as font_error:
                print(f"⚠️ Font error, using default font: {font_error}")
                # Fallback without specifying font
                title_clip = TextClip(
                    text=title_text,
                    method='caption',
                    size=(self.video_size[0] - 200, banner_height - 40),  # More padding and height constraint
                    font_size=dynamic_font_size,
                    color=TITLE_COLOR
                ).with_duration(video_duration).with_position(("center", banner_y + 20))  # Better vertical centering
            
            # Quote image fades in after delay
            print("🖼️ Creating quote image clip...")
            quote_clip = (
                ImageClip(temp_image_path)
                .with_duration(video_duration - self.fade_in_delay)
                .with_start(self.fade_in_delay)
                .resized(width=self.video_size[0])
                .with_position("center")
                .with_effects([FadeIn(self.fade_in_duration)])
            )
            
            # Final composition
            print("🎬 Compositing video...")
            layers = [background_clip, banner_clip, title_clip, quote_clip]
            final_video = CompositeVideoClip(layers).with_audio(audio_clip)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            video_filename = f"quote_video_{timestamp}_{unique_id}.mp4"
            
            # Create temporary output file
            temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            # Export video
            print(f"💾 Writing video to temporary file...")
            final_video.write_videofile(
                temp_video_path, 
                codec="libx264", 
                audio_codec="aac", 
                fps=VIDEO_FPS,
                logger=None  # Suppress moviepy output
            )
            
            # Upload to Azure Blob Storage
            print("☁️ Uploading video to Azure Blob Storage...")
            video_blob_url = self._upload_video_to_blob(temp_video_path, video_filename)
            
            print("✅ Video created and uploaded successfully!")
            return video_filename, video_blob_url
            
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")
        
        finally:
            # Clean up temporary files and resources
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
            if temp_video_path and os.path.exists(temp_video_path):
                os.unlink(temp_video_path)
            if audio_clip:
                audio_clip.close()
            if final_video:
                final_video.close()
    
    def generate_quote_video_safe(self, image_url: str, quote_title: str = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Safe version of generate_quote_video that returns error instead of raising
        
        Returns:
            Tuple of (filename, blob_url, error_message)
        """
        try:
            print(f"🎬 Starting video generation with image URL: {image_url}")
            print(f"📝 Using title: {quote_title}")
            filename, blob_url = self.generate_quote_video(image_url, quote_title)
            print(f"✅ Video generation completed: {filename}")
            return filename, blob_url, None
        except Exception as e:
            error_msg = f"Video generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, None, error_msg
