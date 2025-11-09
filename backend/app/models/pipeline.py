"""
Pipeline Data Models - Type-safe data contracts for the carousel generation pipeline.
Defines all request/response models, enums, and validation logic for the carousel
workflow including requests, strategies, slides, and pipeline state tracking.

Main Models:
    1. PipelineStatus - Enum tracking pipeline lifecycle stages
    2. CarouselRequest - Input schema with business context and auto-generated story_idea
    3. CarouselSlide - Individual slide with purpose, text, and image details
    4. CarouselFormat - Selected format with description and reasoning
    5. CarouselStrategy - Content strategy with hook, flow, tactics, and CTA
    6. CarouselResult - Complete carousel with format, strategy, analysis, and slides
    7. PipelineResult - Full pipeline state with status, request, result, and metadata

Connections:
    - Used by: All agents and core.pipeline for type safety and validation
    - Validated with: Pydantic validators (e.g., story_idea auto-population)
    - Serialized to: JSON for API responses and output files
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, model_validator


class PipelineStatus(str, Enum):
    PLANNING = "planning"
    CAROUSEL_GENERATION = "carousel_generation"
    IMAGE_GENERATION = "image_generation"
    FINAL_ASSEMBLY = "final_assembly"
    COMPLETED = "completed"
    FAILED = "failed"


class CarouselRequest(BaseModel):
    story_idea: Optional[str] = None
    niche: Optional[str] = None
    target_audience: Optional[str] = None
    pain_point: Optional[str] = None
    cta_goal: Optional[str] = None
    num_slides: int = 3

    @model_validator(mode="after")
    def populate_story_idea(self):
        if not self.story_idea:
            parts: List[str] = []
            if self.niche:
                parts.append(f"Create a carousel for the {self.niche} niche")
            if self.target_audience:
                parts.append(f"targeting {self.target_audience}")
            if self.pain_point:
                parts.append(f"addressing {self.pain_point}")
            if self.cta_goal:
                parts.append(f"with a call to action to {self.cta_goal}")
            if parts:
                self.story_idea = ", ".join(parts)
        if not self.story_idea:
            raise ValueError("story_idea or descriptive business context is required")
        if self.num_slides < 1:
            raise ValueError("num_slides must be at least 1")
        return self


class CarouselSlide(BaseModel):
    slide_number: int
    slide_purpose: str
    text_on_screen: str
    image_generation_prompt: str
    image_path: Optional[str] = None


class CarouselFormat(BaseModel):
    format_name: str
    format_description: str
    reasoning: str
    target_slides: int


class CarouselStrategy(BaseModel):
    hook_strategy: str
    content_flow: str
    engagement_tactics: List[str]
    cta_approach: str


class CarouselResult(BaseModel):
    format_type: str
    strategy: CarouselStrategy
    why_this_works: List[str]
    slides: List[CarouselSlide]


class PipelineResult(BaseModel):
    id: str
    status: PipelineStatus
    request: CarouselRequest
    carousel_result: Optional[CarouselResult] = None
    output_folder: Optional[str] = None
    created_at: str
    updated_at: str
    error_message: Optional[str] = None