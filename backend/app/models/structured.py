"""
Structured Output Models for Anthropic Claude API.

These Pydantic models are used with Anthropic's structured outputs feature
to guarantee schema-compliant responses without manual JSON parsing.

Models contain only the fields Claude generates (no step_name, success, etc.).
Agents transform these structured outputs into full pipeline output models.

Documentation: https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs
"""

from typing import List
from pydantic import BaseModel, Field


class ClaudeStoryOutput(BaseModel):
    """
    Structured output model for Strategy Generator using Claude.
    
    Used with generate_structured_output() to ensure valid strategy generation
    without JSON parsing errors.
    """
    complete_strategy: str = Field(
        ..., 
        description="The complete overarching strategic approach for the entire carousel (200-400 chars)"
    )
    complete_strategy_rationale: str = Field(
        ..., 
        description="Explanation of why this strategy works for this format and brand (100-200 chars)"
    )
    hook_slide_strategy: str = Field(
        ..., 
        description="The detailed hook strategy for the carousel (30-150 chars)"
    )
    body_slides_strategy: List[str] = Field(
        ..., 
        description="The detailed body slides strategies for the carousel (each 30-150 chars)"
    )


class ClaudeTextOutput(BaseModel):
    """
    Structured output model for Text Generator using Claude.
    
    Used per-slide to convert verbose stories into short, punchy captions.
    """
    caption: str = Field(
        ..., 
        description="Short, punchy caption (3-8 words ideal, max 10 words)"
    )
    rationale: str = Field(
        ..., 
        description="Brief explanation of why this caption works (50-150 chars)"
    )


class ClaudeFormatDecisionOutput(BaseModel):
    """
    Structured output model for Carousel Format Decider using Claude.
    
    Determines the optimal carousel format and number of slides.
    """
    format_type: str = Field(
        ..., 
        description="The type of carousel format (e.g., 'Top 5', 'Tutorial', 'Story/Case Study')"
    )
    num_slides: int = Field(
        ..., 
        description="The number of slides in the carousel (between 3 and 10)"
    )
    format_rationale: str = Field(
        ..., 
        description="Explanation of why this format was chosen"
    )


class ClaudeEvaluationOutput(BaseModel):
    """
    Structured output model for Finalizer evaluation using Claude.
    
    Provides comprehensive quality assessment for the entire carousel pipeline.
    Used for logging and quality analysis only (does not affect pipeline).
    """
    format_type_evaluation: str = Field(
        ..., 
        description="Assessment of format appropriateness for the content and brand"
    )
    hook_slide_strategy_evaluation: str = Field(
        ..., 
        description="Assessment of hook strategy quality and effectiveness"
    )
    body_slides_strategy_evaluation: List[str] = Field(
        ..., 
        description="Assessment of each body slide strategy quality"
    )
    complete_strategy_evaluation: str = Field(
        ..., 
        description="Assessment of the complete strategy coherence and messaging"
    )
    hook_slide_text_evaluation: str = Field(
        ..., 
        description="Assessment of hook text brevity and impact"
    )
    body_slides_text_evaluation: List[str] = Field(
        ..., 
        description="Assessment of each body slide text quality"
    )
    hook_slide_image_evaluation: str = Field(
        ..., 
        description="Assessment of hook image suitability based on text and story"
    )
    body_slides_images_evaluation: List[str] = Field(
        ..., 
        description="Assessment of each body slide image suitability"
    )
    brand_kit_evaluation: str = Field(
        ..., 
        description="Assessment of overall brand alignment and consistency"
    )

