"""
Brand Kit Models - Pydantic schemas for brand kit management.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class BrandKitBase(BaseModel):
    """Base brand kit schema."""
    brand_name: str
    brand_niche: str
    brand_colors: List[str]
    brand_style: str
    customer_pain_points: str
    product_service_desc: str
    social_media_links: Optional[dict] = None
    logo_url: Optional[str] = None
    brand_images: Optional[List[str]] = None
    past_posts: Optional[List[str]] = None


class BrandKitCreate(BrandKitBase):
    """Schema for brand kit creation."""
    pass


class BrandKitUpdate(BaseModel):
    """Schema for brand kit update (all fields optional)."""
    brand_name: Optional[str] = None
    brand_niche: Optional[str] = None
    brand_colors: Optional[List[str]] = None
    brand_style: Optional[str] = None
    customer_pain_points: Optional[str] = None
    product_service_desc: Optional[str] = None
    social_media_links: Optional[dict] = None
    logo_url: Optional[str] = None
    brand_images: Optional[List[str]] = None
    past_posts: Optional[List[str]] = None


class BrandKitResponse(BrandKitBase):
    """Schema for brand kit response."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

