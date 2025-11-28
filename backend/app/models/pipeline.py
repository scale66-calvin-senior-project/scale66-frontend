"""
AI Pipeline Models - Pydantic schemas for internal AI agent communication.

PIPELINE FLOW (Updated for Gemini 3 Pro Image with text generation):
1. Orchestrator - Coordinates the entire pipeline
2. CarouselFormatDecider - Determines optimal carousel format
3. StoryGenerator - Creates verbose, detailed narratives
4. TextGenerator - Converts stories into short, punchy carousel captions
5. ImageGenerator - Generates images WITH text baked in using Gemini 3 Pro
6. Finalizer - Validates image quality, uploads to storage, stores metrics
"""

from typing import Optional, List, Dict
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
    quality_metrics: Optional[List['SlideQualityMetrics']] = Field(None, description="Quality validation metrics from Finalizer")
    

# =============== Step 2: Carousel Format Decision ===============

class CarouselFormatDeciderInput(BasePipelineStep):
    """Schema for carousel format decision input."""
    user_prompt: str
    brand_kit: BrandKit

class CarouselFormatDeciderOutput(BasePipelineStep):
    """Schema for carousel format decision output."""
    format_type: str = Field(..., description="The type of carousel format")
    num_slides: int = Field(..., ge=3, le=10, description="The number of slides in the carousel")
    format_rationale: str = Field(..., description="The rationale for the format decision")

# =============== Step 3: Story Generation ===============

class StoryGeneratorInput(BasePipelineStep):
    """Schema for story generator input."""
    format_type: str = Field(..., description="The type of carousel format")
    num_slides: int = Field(..., ge=3, le=10, description="The number of slides in the carousel")
    brand_kit: BrandKit = Field(..., description="The brand kit")
    user_prompt: str = Field(..., description="The user's content request")

class StoryGeneratorOutput(BasePipelineStep):
    """Schema for story generator output - verbose, detailed narratives."""
    hook_slide_story: str = Field(..., description="The detailed hook story for the carousel")
    body_slides_story: List[str] = Field(..., description="The detailed body slides stories for the carousel")

# =============== Step 4: Text Generation ===============
# CHANGED: Now runs BEFORE image generation, NO image analysis

class TextGeneratorInput(BasePipelineStep):
    """
    Schema for text generator input.
    
    Takes verbose stories and creates short, punchy carousel captions.
    NO image analysis - purely text-based transformation.
    """
    hook_slide_story: str = Field(..., description="The verbose hook story to convert into caption")
    body_slides_story: List[str] = Field(..., description="The verbose body stories to convert into captions")

class TextGeneratorOutput(BasePipelineStep):
    """
    Schema for text generator output.
    
    Short, punchy captions ready for image generation.
    NO styling information - text will be rendered by Gemini 3 Pro.
    """
    hook_slide_text: str = Field(..., description="Short, punchy hook text (3-8 words)")
    body_slides_text: List[str] = Field(..., description="Short, punchy body texts")

# =============== Step 5: Image Generation ===============
# CHANGED: Now receives TEXT in addition to stories, generates images WITH text

class ImageGeneratorInput(BasePipelineStep):
    """
    Schema for image generator input.
    
    Receives both detailed stories (for context) and short captions (to render).
    Gemini 3 Pro will generate images with text baked in.
    """
    hook_slide_story: str = Field(..., description="Detailed hook story for context")
    body_slides_story: List[str] = Field(..., description="Detailed body stories for context")
    hook_slide_text: str = Field(..., description="Short text to render on hook image")
    body_slides_text: List[str] = Field(..., description="Short texts to render on body images")

class ImageGeneratorOutput(BasePipelineStep):
    """
    Schema for image generator output.
    
    Images with text already rendered by Gemini 3 Pro.
    """
    hook_slide_image: str = Field(..., description="Hook slide image with text rendered (base64)")
    body_slides_images: List[str] = Field(..., description="Body slide images with text rendered (base64)")

# =============== Step 6: Finalizer ===============
# CHANGED: Now performs quality validation instead of text overlay

class FinalizerInput(BasePipelineStep):
    """
    Schema for finalizer input.
    
    Receives generated images and validates quality using Claude Vision.
    Stores metrics for pipeline improvement (no retry logic in MVP).
    """
    hook_slide_image: str = Field(..., description="Generated hook image with text (base64)")
    body_slides_images: List[str] = Field(..., description="Generated body images with text (base64)")
    hook_slide_text: str = Field(..., description="Expected hook text (for validation)")
    body_slides_text: List[str] = Field(..., description="Expected body texts (for validation)")
    hook_slide_story: str = Field(..., description="Hook story (for context validation)")
    body_slides_story: List[str] = Field(..., description="Body stories (for context validation)")
    brand_kit: Optional[BrandKit] = Field(None, description="Brand kit (for brand compliance validation)")

class SlideQualityMetrics(BaseModel):
    """Quality metrics for a single slide."""
    slide_index: int = Field(..., description="Index of the slide (0 = hook, 1+ = body)")
    text_readable: bool = Field(..., description="Whether text is clearly readable")
    text_matches_expected: bool = Field(..., description="Whether rendered text matches expected text")
    text_accuracy_score: float = Field(..., ge=0.0, le=1.0, description="Text accuracy (0-1, 1 = perfect match)")
    image_quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall image quality (0-1)")
    brand_alignment_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Brand style alignment (0-1)")
    issues: List[str] = Field(default_factory=list, description="List of identified issues")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")

class FinalizerOutput(BasePipelineStep):
    """
    Schema for finalizer output.
    
    Includes carousel URLs and detailed quality metrics for each slide.
    """
    carousel_id: str = Field(..., description="The ID of the carousel")
    carousel_slides_urls: List[str] = Field(..., description="The public URLs of uploaded carousel slides")
    quality_metrics: List[SlideQualityMetrics] = Field(..., description="Quality validation metrics for each slide")