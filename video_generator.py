#!/usr/bin/env python3
"""
Video generation service using MoviePy and Azure Blob Storage
"""

import os
import uuid
import tempfile
import asyncio
from datetime import datetime
from typing import Optional, Tuple
from io import BytesIO

from moviepy import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.fx.FadeIn import FadeIn
from azure.storage.blob import BlobServiceClient
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

from config import (
    AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME, AZURE_VIDEO_FOLDER,
    DEFAULT_AUDIO_FILE, VIDEO_SIZE, VIDEO_TITLE, FADE_IN_DELAY, FADE_IN_DURATION,
    VIDEO_FPS, BACKGROUND_COLOR, BANNER_COLOR, BANNER_HEIGHT, BANNER_Y_POSITION,
    TITLE_FONT_SIZE, TITLE_COLOR, WIDTH, HEIGHT
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
        
    async def _download_image_from_url(self, image_url: str) -> str:
        """Download image from URL to temporary file asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            # Run the blocking requests call in a thread pool
            response = await loop.run_in_executor(None, lambda: requests.get(image_url, timeout=30))
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg')
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            raise Exception(f"Failed to download image from URL: {str(e)}")
    
    def _load_font(self, size: int):
        """Load font with fallback to default"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font, draw, max_width: int, margin: int = 40):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        line = ""
        
        for word in words:
            test_line = f"{line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width - 2 * margin:
                line = test_line
            else:
                if line:  # Only add line if it's not empty
                    lines.append(line)
                    line = word
                else:  # Single word is too long, add it anyway
                    lines.append(word)
                    line = ""
        
        if line:
            lines.append(line)
        
        return lines
    
    def _get_best_font(self, text: str, draw, max_width: int, max_height: int, margin: int = 40, line_spacing: int = 10):
        """Find the best font size that fits the text within dimensions"""
        for size in range(100, 8, -2):  # Go down to size 8, step by 2 for faster processing
            font = self._load_font(size)
            lines = self._wrap_text(text, font, draw, max_width, margin)
            
            # Calculate actual text height for each line
            line_heights = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]  # Actual height of text
                line_heights.append(line_height)
            
            total_height = sum(line_heights) + (len(lines) - 1) * line_spacing
            
            if total_height <= max_height - 2 * margin:
                return font, lines
        
        # Final fallback with smallest possible font
        return self._load_font(8), self._wrap_text(text, self._load_font(8), draw, max_width, margin)
    
    async def _create_title_banner(self, text: str, width: int = None, height: int = None) -> str:
        """
        Create a title banner image using PIL and save to a temporary file.
        Dynamically adjusts banner height to fit text content.
        """
        loop = asyncio.get_event_loop()
        
        def create_banner():
            banner_width = width or self.video_size[0]
            
            # Settings
            bg_color = BANNER_COLOR
            text_color = TITLE_COLOR
            margin = 40
            line_spacing = 10
            min_banner_height = 100  # Minimum banner height
            max_banner_height = 400  # Maximum banner height
            
            # Create a temporary image for text measurement
            temp_image = Image.new("RGB", (banner_width, 100), bg_color)
            draw = ImageDraw.Draw(temp_image)
            
            # Start with a reasonable font size and find the best fit
            optimal_font_size = 40
            for size in range(60, 20, -2):  # Start from 60, go down to 20
                font = self._load_font(size)
                lines = self._wrap_text(text, font, draw, banner_width, margin)
                
                # Calculate total height needed for this font size
                line_heights = []
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_height = bbox[3] - bbox[1]
                    line_heights.append(line_height)
                
                total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
                needed_height = total_text_height + 2 * margin
                
                # Check if this font size gives us a reasonable banner height
                if needed_height <= max_banner_height:
                    optimal_font_size = size
                    break
            
            # Now create the banner with the optimal font size
            font = self._load_font(optimal_font_size)
            lines = self._wrap_text(text, font, draw, banner_width, margin)
            
            # Calculate the actual banner height needed
            line_heights = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
            
            total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
            
            # Use custom height if provided, otherwise calculate based on text
            if height:
                banner_height = height
            else:
                # Dynamic height with padding
                banner_height = max(min_banner_height, min(max_banner_height, total_text_height + 2 * margin))
            
            # Create the actual banner image
            image = Image.new("RGB", (banner_width, banner_height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # If text still doesn't fit, reduce font size further
            while total_text_height > banner_height - 2 * margin and optimal_font_size > 12:
                optimal_font_size -= 2
                font = self._load_font(optimal_font_size)
                lines = self._wrap_text(text, font, draw, banner_width, margin)
                line_heights = []
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_height = bbox[3] - bbox[1]
                    line_heights.append(line_height)
                total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
            
            # Compute starting Y position for vertical centering
            y = (banner_height - total_text_height) // 2
            
            # Draw each line centered
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                x = (banner_width - line_width) // 2
                draw.text((x, y), line, fill=text_color, font=font)
                y += line_heights[i] + line_spacing
            
            # Save image
            temp_banner_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
            image.save(temp_banner_path)
            return temp_banner_path
        
        # Run banner creation in thread pool
        return await loop.run_in_executor(None, create_banner)

    
    async def _upload_video_to_blob(self, video_path: str, filename: str) -> str:
        """Upload video file to Azure Blob Storage asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            
            # Create blob path with folder
            blob_path = f"{self.video_folder}/{filename}"
            
            # Upload the video
            blob_client = self.container_client.get_blob_client(blob_path)
            
            # Run the blocking upload operation in a thread pool
            def upload_blob():
                with open(video_path, 'rb') as video_file:
                    blob_client.upload_blob(video_file, overwrite=True)
            
            await loop.run_in_executor(None, upload_blob)
            
            # Return the blob URL
            blob_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_path}"
            return blob_url
            
        except Exception as e:
            raise Exception(f"Failed to upload video to blob storage: {str(e)}")
    
    async def generate_quote_video(self, image_url: str, quote_title: str = None) -> Tuple[str, str]:
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
        temp_banner_path = None
        audio_clip = None
        final_video = None
        
        try:
            # Check if audio file exists
            if not os.path.exists(self.audio_file):
                raise Exception(f"Audio file not found: {self.audio_file}")
            
            print(f"🎵 Audio file found: {self.audio_file}")
            
            # Run image download and banner creation concurrently
            print("� Starting parallel operations...")
            title_text = quote_title if quote_title else self.title_text
            
            # Execute download and banner creation in parallel
            download_task = self._download_image_from_url(image_url)
            banner_task = self._create_title_banner(title_text)
            
            temp_image_path, temp_banner_path = await asyncio.gather(
                download_task,
                banner_task
            )
            
            print(f"🖼️ Image downloaded to: {temp_image_path}")
            print(f"📝 Title banner created: {temp_banner_path}")

            print("🔊 Loading audio and setting up video...")
            audio_clip = AudioFileClip(self.audio_file)
            video_duration = audio_clip.duration
            print(f"⏱️ Video duration: {video_duration} seconds")
            
            # Background
            background_clip = ColorClip(
                size=self.video_size, 
                color=BACKGROUND_COLOR
            ).with_duration(video_duration)
            
            # Banner positioned above the quote
            banner_y = BANNER_Y_POSITION
            
            # Create banner clip from PIL-generated image
            banner_clip = (
                ImageClip(temp_banner_path)
                .with_duration(video_duration)
                .with_position(("center", banner_y))
            )
            
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
            layers = [background_clip, banner_clip, quote_clip]
            final_video = CompositeVideoClip(layers).with_audio(audio_clip)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            video_filename = f"quote_video_{timestamp}_{unique_id}.mp4"
            
            # Create temporary output file
            temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            # Export video asynchronously
            print(f"💾 Writing video to temporary file...")
            loop = asyncio.get_event_loop()
            
            # Run video export in thread pool to avoid blocking
            def export_video():
                final_video.write_videofile(
                    temp_video_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=VIDEO_FPS
                )
            
            await loop.run_in_executor(None, export_video)
            
            # Upload to Azure Blob Storage
            print("☁️ Uploading video to Azure Blob Storage...")
            video_blob_url = await self._upload_video_to_blob(temp_video_path, video_filename)
            
            print("✅ Video created and uploaded successfully!")
            return video_filename, video_blob_url
            
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")
        
        finally:
            # Clean up temporary files and resources
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
            if temp_banner_path and os.path.exists(temp_banner_path):
                os.unlink(temp_banner_path)
            if temp_video_path and os.path.exists(temp_video_path):
                os.unlink(temp_video_path)
            if audio_clip:
                audio_clip.close()
            if final_video:
                final_video.close()
    
    async def generate_quote_video_safe(self, image_url: str, quote_title: str = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Safe version of generate_quote_video that returns error instead of raising
        
        Returns:
            Tuple of (filename, blob_url, error_message)
        """
        try:
            print(f"🎬 Starting video generation with image URL: {image_url}")
            print(f"📝 Using title: {quote_title}")
            filename, blob_url = await self.generate_quote_video(image_url, quote_title)
            print(f"✅ Video generation completed: {filename}")
            return filename, blob_url, None
        except Exception as e:
            error_msg = f"Video generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, None, error_msg
