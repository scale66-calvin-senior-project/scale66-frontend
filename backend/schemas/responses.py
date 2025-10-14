"""
═══════════════════════════════════════════════════════════════════════════
                              RESPONSES.PY
       API RESPONSE SCHEMAS - DEFINES PYDANTIC MODELS FOR API RESPONSES
═══════════════════════════════════════════════════════════════════════════
"""

from pydantic import BaseModel  # type: ignore
from typing import List, Optional

class ImageGenerationResponse(BaseModel):
    saved_image_path: str
    prompt: str
    aspect_ratio: str
    status: str
    input_image_provided: bool

class Brand(BaseModel):
    brand_id: str
    brand_name: str

class BrandsListResponse(BaseModel):
    brands: List[Brand]

class BrandImage(BaseModel):
    path: str
    full_path: str
    description: str
    filename: str

class BrandLogo(BaseModel):
    path: str
    full_path: str
    description: str

class BrandDetailsResponse(BaseModel):
    brand_id: str
    brand_name: str
    logo: Optional[BrandLogo]
    instagram_images: List[BrandImage]