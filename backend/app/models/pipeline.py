"""
AI Pipeline Models - Pydantic schemas for internal AI agent communication.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.brand_kit import BrandKit
from app.models.common import BasePipelineStep

# =============== Step 1: Orchestrator ===============

class OrchestratorInput(BasePipelineStep):
    """Schema for orchestrator input."""
    brand_kit_id: str = Field(..., description="The ID of the brand kit")
    user_prompt: str = Field(..., description="The user's content request")

class OrchestratorOutput(BasePipelineStep):
    """Schema for orchestrator output."""
    carousel_id: str = Field(..., description="The ID of the generated carousel")
    carousel_slides_urls: List[str] = Field(..., description="The URLs of the carousel slides")
    

# =============== Step 2: Carousel Format Decision ===============

class CarouselFormatDeciderInput(BasePipelineStep):
    """Schema for carousel format decision (from carousel_format_decider agent)."""
    user_prompt: str
    brand_kit: BrandKit

class CarouselFormatDeciderOutput(BasePipelineStep):
    """Schema for carousel format decision (from carousel_format_decider agent)."""
    format_type: str = Field(..., description="The type of carousel format")
    num_slides: int = Field(..., ge=3, le=10, description="The number of slides in the carousel")
    format_rationale: str = Field(..., description="The rationale for the format decision")

# =============== Step 3: Story Generation ===============

class StoryGeneratorInput(BasePipelineStep):
    """Schema for story data (from story_generator agent)."""
    format_type: str = Field(..., description="The type of carousel format")
    num_slides: int = Field(..., ge=3, le=10, description="The number of slides in the carousel")
    brand_kit: BrandKit = Field(..., description="The brand kit")
    user_prompt: str = Field(..., description="The user's content request")

class StoryGeneratorOutput(BasePipelineStep):
    """Schema for text data (from text_generator agent)."""
    hook_slide_story: str = Field(..., description="The hook story for the carousel")
    body_slides_story: List[str] = Field(..., description="The body slides stories for the carousel")

# =============== Step 4: Image Generation ===============

class ImageGeneratorInput(BasePipelineStep):
    """Schema for image data (from image_generator agent)."""
    hook_slide_story: str = Field(..., description="The hook slide story for the carousel")
    body_slides_story: List[str] = Field(..., description="The body slides stories for the carousel")

class ImageGeneratorOutput(BasePipelineStep):
    """Schema for image data (from image_generator agent)."""
    hook_slide_image: str = Field(..., description="The hook slide image for the carousel")
    body_slides_images: List[str] = Field(..., description="The body slides images for the carousel")

# =============== Step 5: Text Generation ===============

class TextGeneratorInput(BasePipelineStep):
    """Schema for text data (from text_generator agent)."""
    hook_slide_story: str = Field(..., description="The hook slide story for the carousel")
    body_slides_story: List[str] = Field(..., description="The body slides stories for the carousel")
    hook_slide_image: str = Field(..., description="The hook slide image for the carousel")
    body_slides_images: List[str] = Field(..., description="The body slides images for the carousel")

class TextGeneratorOutput(BasePipelineStep):
    """Schema for text data (from text_generator agent)."""
    hook_slide_text: str = Field(..., description="The hook slide text for the carousel")
    body_slides_text: List[str] = Field(..., description="The body slides text for the carousel")
    hook_slide_text_style: str = Field(..., description="The text style for the hook slide")
    body_slides_text_styles: List[str] = Field(..., description="The text styles for the body slides")

# =============== Step 6: Finalizer ===============

class FinalizerInput(BasePipelineStep):
    """Schema for finalizer input."""
    hook_slide_text: str = Field(..., description="The hook slide text for the carousel")
    body_slides_text: List[str] = Field(..., description="The body slides text for the carousel")
    hook_slide_text_style: str = Field(..., description="The text style for the hook slide")
    body_slides_text_styles: List[str] = Field(..., description="The text styles for the body slides")
    hook_slide_image: str = Field(..., description="The hook slide image for the carousel")
    body_slides_images: List[str] = Field(..., description="The body slides images for the carousel")

class FinalizerOutput(BasePipelineStep):
    """Schema for finalizer output."""
    carousel_id: str = Field(..., description="The ID of the carousel")
    carousel_slides_urls: List[str] = Field(..., description="The URLs of the carousel slides")