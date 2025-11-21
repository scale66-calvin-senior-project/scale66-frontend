"""
Social Media Models - Pydantic schemas for social media OAuth and account management.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class OAuthInitResponse(BaseModel):
    """Schema for OAuth initialization response."""
    authorization_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """Schema for OAuth callback request."""
    code: str
    state: str


class SocialAccountResponse(BaseModel):
    """Schema for social media account response."""
    id: str
    user_id: str
    platform: str
    platform_user_id: str
    platform_username: Optional[str] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

