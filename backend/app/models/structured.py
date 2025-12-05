from typing import List, Optional
from pydantic import BaseModel, Field


class ClaudeFormatSelectionOutput(BaseModel):
    format_type: str = Field(..., description="The carousel format type (e.g., 'listicle_tips')")
    num_body_slides: int = Field(..., ge=1, le=8, description="Number of body/content slides needed (1-8). Hook and CTA are separate.")
    cta_slide: bool = Field(..., description="Whether to include a CTA slide")


class ClaudeTemplateSelectionOutput(BaseModel):
    template_id: str = Field(..., description="The selected template ID (e.g., 'carousel-4')")


class ClaudeSlidesTextOutput(BaseModel):
    hook_text: str = Field(..., description="Hook slide caption text")
    body_texts: List[str] = Field(..., description="Body slide caption texts in order")
    cta_text: Optional[str] = Field(None, description="CTA slide caption text (only if CTA slide is needed)")
