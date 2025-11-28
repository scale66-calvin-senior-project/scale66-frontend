"""
Brand Kit Models - Pydantic schemas for brand kit management.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# =============== Brand Kit (Internal/Pipeline) ===============

class BrandKit(BaseModel):
    """Schema for a brand kit used in AI pipeline."""
    brand_name: str
    brand_niche: str
    brand_style: str
    customer_pain_points: List[str]
    product_service_desc: str


# =============== Brand Kit API Models ===============

class BrandKitBase(BaseModel):
    """Base schema for brand kit with common fields."""
    brand_name: str
    brand_niche: str
    brand_style: str
    customer_pain_points: Optional[List[str]] = None
    product_service_desc: str


class BrandKitCreate(BrandKitBase):
    """Schema for creating a new brand kit."""
    pass


class BrandKitUpdate(BaseModel):
    """Schema for updating a brand kit (all fields optional)."""
    brand_name: Optional[str] = None
    brand_niche: Optional[str] = None
    brand_style: Optional[str] = None
    customer_pain_points: Optional[List[str]] = None
    product_service_desc: Optional[str] = None


class BrandKitResponse(BrandKitBase):
    """Schema for brand kit API response."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime