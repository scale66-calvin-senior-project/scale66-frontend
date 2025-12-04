from typing import List
from pydantic import BaseModel, Field


class ClaudeFormatSelectionOutput(BaseModel):
    format_type: str = Field(..., description="The carousel format type (e.g., 'listicle_tips')")
    format_rationale: str = Field(..., description="Brief explanation of why this format fits the content (50-150 chars)")


class ClaudeTemplateSelectionOutput(BaseModel):
    template_id: str = Field(..., description="The selected template ID (e.g., 'carousel-4')")
    template_rationale: str = Field(..., description="Brief explanation of why this template fits the brand and content (50-150 chars)")


class ClaudeSlidesTextOutput(BaseModel):
    slides_text: List[str] = Field(..., description="Text for each slide in order (first slide is hook, rest are body slides)")
    slides_rationale: List[str] = Field(..., description="Rationale for each slide's text")
