"""
User Models - Pydantic schemas for user-related API operations.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation (signup)."""
    password: str = Field(..., min_length=8)
    # NOTE: If using Supabase Auth, password is handled by Supabase


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    subscription_tier: str
    onboarding_completed: bool
    created_at: datetime

