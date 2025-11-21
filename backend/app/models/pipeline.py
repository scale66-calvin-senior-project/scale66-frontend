"""
AI Pipeline Models - Pydantic schemas for internal AI agent communication.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class CarouselFormatDecision(BaseModel):
    """Schema for carousel format decision (from format_decider agent)."""
    selected_format: str
    num_slides: int = Field(..., ge=3, le=10)
    format_rationale: str
    content_structure: str


class StoryData(BaseModel):
    """Schema for story data (from story_generator agent)."""
    hook: str
    script: str
    slides: List[str]
    cta: str


class TextData(BaseModel):
    """Schema for text data (from text_generator agent)."""
    text_style: str
    hook_text: str
    body_slides_text: List[str]
    text_metadata: dict


class ImageData(BaseModel):
    """Schema for image data (from image_generator agent)."""
    image_style: str
    hook_image_url: str
    body_images_urls: List[str]
    image_metadata: dict


class CarouselOutput(BaseModel):
    """Schema for final carousel output (from orchestrator)."""
    carousel_slides: List[str]
    carousel_format: CarouselFormatDecision
    story_data: StoryData
    text_data: TextData
    image_data: ImageData
    metadata: dict
    pipeline_log: Optional[List[dict]] = None

