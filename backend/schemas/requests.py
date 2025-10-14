"""
═══════════════════════════════════════════════════════════════════════════
                               REQUESTS.PY
        API REQUEST SCHEMAS - DEFINES PYDANTIC MODELS FOR INCOMING
             API REQUESTS INCLUDING IMAGE GENERATION PARAMETERS

MODELS:
    ImageGenerationRequest -> REQUEST MODEL FOR IMAGE GENERATION ENDPOINT
═══════════════════════════════════════════════════════════════════════════
"""

from pydantic import BaseModel, Field  # type: ignore
from typing import Literal, Optional

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    aspect_ratio: Literal["1:1", "3:4", "4:3", "9:16", "16:9"] = Field(
        default="1:1",
        description="Aspect ratio of the generated image"
    )
    brand_id: str = Field(
        ...,
        description="Brand ID for loading stored brand images and saving generated images"
    )
    input_image_path: Optional[str] = Field(
        default=None,
        description="Path to image within brand directory (e.g., 'instagram/image_1.png')"
    )
