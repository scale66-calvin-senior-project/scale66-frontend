"""
Post Models - Pydantic schemas for post/carousel management.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """Base post schema."""
    campaign_id: Optional[str] = None
    carousel_slides: List[str]
    carousel_metadata: dict
    caption: Optional[str] = None
    platform: str = Field(..., pattern="^(instagram|tiktok)$")
    status: str = Field(default="draft", pattern="^(draft|scheduled|published|failed)$")
    scheduled_for: Optional[datetime] = None


class PostCreate(PostBase):
    """Schema for post creation."""
    pass


class PostUpdate(BaseModel):
    """Schema for post update (all fields optional)."""
    caption: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class PostResponse(PostBase):
    """Schema for post response."""
    id: str
    user_id: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

