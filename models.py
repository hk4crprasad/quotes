"""
Data models for the Gen Z Quote Generator
"""

from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


@dataclass
class Quote:
    """Quote data class"""
    title: str = ""
    content: str = ""
    theme: str = "mixed"
    target_audience: str = "gen-z"
    created_at: Optional[str] = None
    caption: str = ""


class QuoteResponse(BaseModel):
    """Response model for quotes"""
    title: str
    content: str
    theme: str
    target_audience: str
    created_at: Optional[str] = None
    caption: str
    image_url: Optional[str] = None
    image_filename: Optional[str] = None
    video_url: Optional[str] = None
    video_filename: Optional[str] = None


class QuoteRequest(BaseModel):
    """Request model for generating quotes"""
    theme: str = Field(default="mixed", description="Theme for the quote")
    target_audience: str = Field(default="gen-z", description="Target audience")
    format_preference: Optional[str] = Field(default=None, description="Preferred format")
    image: bool = Field(default=False, description="Whether to generate an image")
    image_style: str = Field(default="paper", description="Image style: paper, modern, minimal")
    video: bool = Field(default=False, description="Whether to generate a video (requires image=true)")

class ReelUploadRequest(BaseModel):
    video_url: HttpUrl
    caption: str = ""
    share_to_feed: bool = True
    thumb_offset: Optional[int] = None
    location_id: Optional[str] = None

class QuickReelRequest(BaseModel):
    video_url: HttpUrl
    caption: str

# Response models
class ReelUploadResponse(BaseModel):
    success: bool
    message: str
    container_id: Optional[str] = None
    media_id: Optional[str] = None
    status: Optional[str] = None

class StatusResponse(BaseModel):
    success: bool
    status: str
    message: str
