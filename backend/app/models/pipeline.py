"""
AI Pipeline Models - Pydantic schemas for internal AI agent communication.

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

# =============== Step 3: Strategy Generation ===============

class StrategyGeneratorInput(BasePipelineStep):
    """Schema for strategy generator input."""
    format_type: str = Field(..., description="The type of carousel format")
    num_slides: int = Field(..., ge=3, le=10, description="The number of slides in the carousel")
    brand_kit: BrandKit = Field(..., description="The brand kit")
    user_prompt: str = Field(..., description="The user's content request")

class StrategyGeneratorOutput(BasePipelineStep):
    """Schema for strategy generator output - strategic guidance for slides."""
    hook_slide_strategy: str = Field(..., description="The strategic guidance for the hook slide")
    body_slides_strategy: List[str] = Field(..., description="The strategic guidance for each body slide")
    complete_strategy: str = Field(..., description="The complete strategic approach for the carousel")
    complete_strategy_rationale: str = Field(..., description="The rationale for the strategic approach")

# =============== Step 4: Text Generation ===============

class TextGeneratorInput(BasePipelineStep):
    """
    Schema for text generator input.
    """
    brand_kit: BrandKit = Field(..., description="The brand kit")
    format_type: str = Field(..., description="The type of carousel format")
    hook_slide_strategy: str = Field(..., description="Strategy for the hook slide")
    body_slides_strategy: List[str] = Field(..., description="Strategies for the body slides")
    complete_strategy: str = Field(..., description="The complete strategy for context")
class TextGeneratorOutput(BasePipelineStep):
    """
    Schema for text generator output.
    """
    hook_slide_text: str = Field(..., description="The caption for the hook slide")
    body_slides_text: List[str] = Field(..., description="The captions for the body slides")
    captions_rationale: List[str] = Field(..., description="The rationale for the captions of each slide")

# =============== Step 5: Image Generation ===============

class ImageGeneratorInput(BasePipelineStep):
    """
    Schema for image generator input.
    """
    brand_kit: BrandKit = Field(..., description="The brand kit")
    format_type: str = Field(..., description="The type of carousel format")
    hook_slide_strategy: str = Field(..., description="Strategy for the hook slide")
    complete_strategy: str = Field(..., description="The complete strategy for context")
    body_slides_strategy: List[str] = Field(..., description="Strategies for the body slides")
    hook_slide_text: str = Field(..., description="Caption for the hook slide")
    body_slides_text: List[str] = Field(..., description="Captions for the body slides")

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
    hook_slide_strategy: str = Field(..., description="Hook strategy (for context validation)")
    body_slides_strategy: List[str] = Field(..., description="Body strategies (for context validation)")
    complete_strategy: str = Field(..., description="Complete strategy (for context validation)")
    hook_slide_text: str = Field(..., description="Expected hook text (for validation)")
    body_slides_text: List[str] = Field(..., description="Expected body texts (for validation)")
    hook_slide_image: str = Field(..., description="Generated hook image with text (base64)")
    body_slides_images: List[str] = Field(..., description="Generated body images with text (base64)")
    brand_kit: Optional[BrandKit] = Field(None, description="Brand kit (for brand compliance validation)")

class EvaluationMetrics(BaseModel):
    """Evaluation metrics for the entire pipeline."""
    format_type_evaluation: str = Field(..., description="The type of carousel format evaluation")
    hook_slide_strategy_evaluation: str = Field(..., description="Hook strategy evaluation")
    body_slides_strategy_evaluation: List[str] = Field(..., description="Body strategies evaluation")
    complete_strategy_evaluation: str = Field(..., description="Complete strategy evaluation")
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