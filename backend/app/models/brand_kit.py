"""
Brand Kit Models - Pydantic schemas for brand kit management.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# =============== Brand Kit ===============

class BrandKit(BaseModel):
    """Schema for a brand kit."""
    brand_name: str
    brand_niche: str
    brand_style: str
    customer_pain_points: List[str]
    product_service_desc: str