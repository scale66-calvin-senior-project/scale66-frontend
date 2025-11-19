"""
Content Generation Models - Pydantic schemas for AI content generation API.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ContentGenerationRequest(BaseModel):
    """Schema for content generation request."""
    user_prompt: str = Field(..., min_length=10, max_length=1000)
    campaign_id: Optional[str] = None
    # Additional parameters can be added:
    # tone: Optional[str] = None
    # num_slides: Optional[int] = Field(default=5, ge=3, le=10)


class ContentGenerationResponse(BaseModel):
    """Schema for content generation response."""
    job_id: str
    status: str
    message: str


class ContentGenerationStatus(BaseModel):
    """Schema for checking generation status."""
    job_id: str
    status: str  # "started", "processing", "completed", "failed"
    progress: Optional[int] = Field(default=0, ge=0, le=100)
    current_step: Optional[str] = None
    carousel_slides: Optional[List[str]] = None
    carousel_metadata: Optional[dict] = None
    error: Optional[str] = None

