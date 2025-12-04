from typing import List
from pydantic import Field
from app.models.brand_kit import BrandKit
from app.models.common import BasePipelineStep


class OrchestratorInput(BasePipelineStep):
    brand_kit_id: str = Field(...)
    user_prompt: str = Field(...)


class OrchestratorOutput(BasePipelineStep):
    carousel_id: str = Field(...)
    carousel_slides_urls: List[str] = Field(...)


class TemplateDeciderInput(BasePipelineStep):
    user_prompt: str = Field(...)
    brand_kit: BrandKit = Field(...)


class TemplateDeciderOutput(BasePipelineStep):
    format_type: str = Field(...)
    num_slides: int = Field(..., ge=3, le=10)
    template_id: str = Field(...)
    format_rationale: str = Field(...)


class CaptionGeneratorInput(BasePipelineStep):
    format_type: str = Field(...)
    user_prompt: str = Field(...)
    brand_kit: BrandKit = Field(...)
    num_slides: int = Field(..., ge=3, le=10)


class CaptionGeneratorOutput(BasePipelineStep):
    slides_text: List[str] = Field(...)
    slides_rationale: List[str] = Field(...)


class SlideGeneratorInput(BasePipelineStep):
    format_type: str = Field(...)
    num_slides: int = Field(..., ge=3, le=10)
    brand_kit: BrandKit = Field(...)
    user_prompt: str = Field(...)
    slides_text: List[str] = Field(...)
    template_id: str = Field(...)


class SlideGeneratorOutput(BasePipelineStep):
    slides_images: List[str] = Field(...)
    images_rationale: List[str] = Field(...)
