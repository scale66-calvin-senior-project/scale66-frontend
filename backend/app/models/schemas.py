"""
Pydantic Schemas - Request/Response models for API endpoints.

Defines the data structures for:
- API requests (input validation)
- API responses (output serialization)
- Data transfer between layers

These are separate from database models (which use Supabase).
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ================================
# User Schemas
# ================================

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


# ================================
# Brand Kit Schemas
# ================================

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


# ================================
# Campaign Schemas
# ================================

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


# ================================
# Post Schemas
# ================================

class PostBase(BaseModel):
    """Base post schema."""
    campaign_id: Optional[str] = None
    carousel_slides: List[str]
    carousel_metadata: dict
    caption: Optional[str] = None
    platform: str = Field(..., pattern="^(instagram|tiktok|linkedin|twitter)$")
    status: str = Field(default="draft", pattern="^(draft|scheduled|published|failed)$")
    scheduled_for: Optional[datetime] = None


class PostCreate(PostBase):
    """Schema for post creation."""
    pass


class PostUpdate(BaseModel):
    """Schema for post update (all fields optional)."""
    caption: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class PostResponse(PostBase):
    """Schema for post response."""
    id: str
    user_id: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ================================
# Content Generation Schemas
# ================================

class ContentGenerationRequest(BaseModel):
    """Schema for content generation request."""
    user_prompt: str = Field(..., min_length=10, max_length=1000)
    campaign_id: Optional[str] = None
    # Additional parameters can be added:
    # tone: Optional[str] = None
    # num_slides: Optional[int] = Field(default=5, ge=3, le=10)


class ContentGenerationResponse(BaseModel):
    """Schema for content generation response."""
    job_id: str
    status: str
    message: str


class ContentGenerationStatus(BaseModel):
    """Schema for checking generation status."""
    job_id: str
    status: str  # "started", "processing", "completed", "failed"
    progress: Optional[int] = Field(default=0, ge=0, le=100)
    current_step: Optional[str] = None
    carousel_slides: Optional[List[str]] = None
    carousel_metadata: Optional[dict] = None
    error: Optional[str] = None


# ================================
# Social Media Schemas
# ================================

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


# ================================
# Payment Schemas
# ================================

class CheckoutSessionRequest(BaseModel):
    """Schema for Stripe checkout session request."""
    price_id: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Schema for checkout session response."""
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    """Schema for subscription status response."""
    subscription_id: str
    status: str
    plan: str
    current_period_end: datetime


class PaymentTransactionResponse(BaseModel):
    """Schema for payment transaction response."""
    id: str
    user_id: str
    amount: int  # Amount in cents
    currency: str
    status: str
    payment_method: Optional[str] = None
    created_at: datetime


# ================================
# AI Pipeline Schemas (Internal)
# ================================

class CarouselFormatDecision(BaseModel):
    """Schema for carousel format decision (from format_decider agent)."""
    selected_format: str
    num_slides: int = Field(..., ge=3, le=10)
    format_rationale: str
    content_structure: str


class StoryData(BaseModel):
    """Schema for story data (from story_generator agent)."""
    hook: str
    script: str
    slides: List[str]
    cta: str


class TextData(BaseModel):
    """Schema for text data (from text_generator agent)."""
    text_style: str
    hook_text: str
    body_slides_text: List[str]
    text_metadata: dict


class ImageData(BaseModel):
    """Schema for image data (from image_generator agent)."""
    image_style: str
    hook_image_url: str
    body_images_urls: List[str]
    image_metadata: dict


class CarouselOutput(BaseModel):
    """Schema for final carousel output (from orchestrator)."""
    carousel_slides: List[str]
    carousel_format: CarouselFormatDecision
    story_data: StoryData
    text_data: TextData
    image_data: ImageData
    metadata: dict
    pipeline_log: Optional[List[dict]] = None


# ================================
# Common Response Schemas
# ================================

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None

