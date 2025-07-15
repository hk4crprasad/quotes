"""
Data models for the Gen Z Quote Generator
"""

from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field


@dataclass
class Quote:
    """Quote data class"""
    title: str = ""
    content: str = ""
    theme: str = "mixed"
    target_audience: str = "gen-z"
    created_at: Optional[str] = None


class QuoteResponse(BaseModel):
    """Response model for quotes"""
    title: str
    content: str
    theme: str
    target_audience: str
    created_at: Optional[str] = None


class QuoteRequest(BaseModel):
    """Request model for generating quotes"""
    theme: str = Field(default="mixed", description="Theme for the quote")
    target_audience: str = Field(default="gen-z", description="Target audience")
    format_preference: Optional[str] = Field(default=None, description="Preferred format")
