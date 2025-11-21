"""
Campaign Models - Pydantic schemas for campaign management.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    goals: Optional[str] = None


class CampaignCreate(CampaignBase):
    """Schema for campaign creation."""
    pass


class CampaignUpdate(BaseModel):
    """Schema for campaign update (all fields optional)."""
    name: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    goals: Optional[str] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign response."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

