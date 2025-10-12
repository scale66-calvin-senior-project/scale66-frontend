"""
═══════════════════════════════════════════════════════════════════════════
                              RESPONSES.PY
       API RESPONSE SCHEMAS - DEFINES PYDANTIC MODELS FOR API RESPONSES
             INCLUDING IMAGE GENERATION RESULTS AND BRAND DATA

MODELS:
    GeneratedImage -> SINGLE GENERATED IMAGE DATA MODEL
    ImageGenerationResponse -> RESPONSE MODEL FOR IMAGE GENERATION
    Brand -> BASIC BRAND INFORMATION MODEL
    BrandsListResponse -> RESPONSE MODEL FOR BRANDS LIST
    BrandImage -> BRAND IMAGE METADATA MODEL
    BrandLogo -> BRAND LOGO METADATA MODEL
    BrandDetailsResponse -> RESPONSE MODEL FOR BRAND DETAILS
═══════════════════════════════════════════════════════════════════════════
"""

from pydantic import BaseModel  # type: ignore
from typing import List, Optional, Dict, Any

class GeneratedImage(BaseModel):
    image_data: str
    index: int

class ImageGenerationResponse(BaseModel):
    images: List[GeneratedImage]
    prompt: str
    aspect_ratio: str
    status: str
    saved_image_path: Optional[str] = None

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
    industry: str
    logo: Optional[BrandLogo]
    instagram_images: List[BrandImage]
    brand_voice: Dict[str, Any]
    target_audience: Dict[str, Any]
    messaging: Dict[str, Any]
