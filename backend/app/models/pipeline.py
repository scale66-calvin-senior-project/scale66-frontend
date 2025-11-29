"""
AI Pipeline Models - Pydantic schemas for internal AI agent communication.

PIPELINE FLOW (Updated for Gemini 3 Pro Image with text generation):
1. Orchestrator - Coordinates the entire pipeline
2. CarouselFormatDecider - Determines optimal carousel format
3. StoryGenerator - Creates verbose, detailed narratives
4. TextGenerator - Converts stories into short, punchy carousel captions
5. ImageGenerator - Generates images WITH text baked in using Gemini 3 Pro
6. Finalizer - Validates the entire pipeline output using Claude Vision and uploads the carousel to storage

Note: For Claude structured output models, see app.models.structured
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
    evaluation_metrics: Optional['EvaluationMetrics'] = Field(None, description="Quality validation metrics from Finalizer")
    

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
    complete_story: str = Field(..., description="The complete story for the carousel")
    complete_story_rationale: str = Field(..., description="The rationale for the complete story")

# =============== Step 4: Text Generation ===============

class TextGeneratorInput(BasePipelineStep):
    """
    Schema for text generator input.
    
    Takes verbose stories and creates short, punchy carousel captions.
    NO image analysis - purely text-based transformation.
    """
    hook_slide_story: str = Field(..., description="The verbose hook story to convert into caption")
    body_slides_story: List[str] = Field(..., description="The verbose body stories to convert into captions")
    complete_story: str = Field(..., description="The complete story for context")
class TextGeneratorOutput(BasePipelineStep):
    """
    Schema for text generator output.
    
    Short, punchy captions ready for image generation.
    NO styling information - text will be rendered by Gemini 3 Pro.
    """
    hook_slide_text: str = Field(..., description="Short, punchy hook text (3-8 words)")
    body_slides_text: List[str] = Field(..., description="Short, punchy body texts")
    captions_rationale: List[str] = Field(..., description="The rationale for the captions of each slide")

# =============== Step 5: Image Generation ===============

class ImageGeneratorInput(BasePipelineStep):
    """
    Schema for image generator input.
    
    Receives both complete story, individual slide stories (for context) and short captions (to render).
    Gemini 3 Pro will generate images with text baked in.
    """
    complete_story: str = Field(..., description="The complete story for the carousel")
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
    images_rationale: List[str] = Field(..., description="The rationale for the images of each slide")
    

# =============== Step 6: Finalizer ===============

class FinalizerInput(BasePipelineStep):
    """
    Schema for finalizer input.
    
    Receives generated output from the entire pipeline and validates quality using Claude Vision.
    """
    format_type: str = Field(..., description="The type of carousel format")
    hook_slide_story: str = Field(..., description="Hook story (for context validation)")
    body_slides_story: List[str] = Field(..., description="Body stories (for context validation)")
    complete_story: str = Field(..., description="Complete story (for context validation)")
    hook_slide_text: str = Field(..., description="Expected hook text (for validation)")
    body_slides_text: List[str] = Field(..., description="Expected body texts (for validation)")
    hook_slide_image: str = Field(..., description="Generated hook image with text (base64)")
    body_slides_images: List[str] = Field(..., description="Generated body images with text (base64)")
    brand_kit: Optional[BrandKit] = Field(None, description="Brand kit (for brand compliance validation)")

class EvaluationMetrics(BaseModel):
    """Evaluation metrics for the entire pipeline."""
    format_type_evaluation: str = Field(..., description="The type of carousel format evaluation")
    hook_slide_story_evaluation: str = Field(..., description="Hook story evaluation")
    body_slides_story_evaluation: List[str] = Field(..., description="Body stories evaluation")
    complete_story_evaluation: str = Field(..., description="Complete story evaluation")
    hook_slide_text_evaluation: str = Field(..., description="Hook text evaluation")
    body_slides_text_evaluation: List[str] = Field(..., description="Body texts evaluation")
    hook_slide_image_evaluation: str = Field(..., description="Hook image evaluation")
    body_slides_images_evaluation: List[str] = Field(..., description="Body images evaluation")
    brand_kit_evaluation: str = Field(..., description="Brand kit evaluation")

class FinalizerOutput(BasePipelineStep):
    """
    Schema for finalizer output.
    
    Includes carousel URLs and detailed quality metrics for the entire pipeline.
    """
    carousel_id: str = Field(..., description="The ID of the carousel")
    carousel_slides_urls: List[str] = Field(..., description="The public URLs of uploaded carousel slides")
    evaluation_metrics: EvaluationMetrics = Field(..., description="Quality validation metrics for the entire pipeline")