"""
Models Package - Pydantic schemas for API request/response validation.

All models are organized by feature and exported here for convenient imports.
"""

# User models
from .user import UserBase, UserCreate, UserResponse

# Brand Kit models
from .brand_kit import (
    BrandKitBase,
    BrandKitCreate,
    BrandKitUpdate,
    BrandKitResponse,
)

# Campaign models
from .campaign import (
    CampaignBase,
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
)

# Post models
from .post import PostBase, PostCreate, PostUpdate, PostResponse

# Content generation models
from .content import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentGenerationStatus,
)

# Social media models
from .social import (
    OAuthInitResponse,
    OAuthCallbackRequest,
    SocialAccountResponse,
)

# Payment models
from .payment import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionResponse,
    PaymentTransactionResponse,
)

# AI pipeline models
from .pipeline import (
    OrchestratorInput,
    OrchestratorOutput,
    CarouselFormatDeciderInput,
    CarouselFormatDeciderOutput,
    StoryGeneratorInput,
    StoryGeneratorOutput,
    ImageGeneratorInput,
    ImageGeneratorOutput,
    TextGeneratorInput,
    TextGeneratorOutput,
    FinalizerInput,
    FinalizerOutput,
    SlideQualityMetrics,
)

# Common models
from .common import MessageResponse, ErrorResponse

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    # Brand Kit
    "BrandKitBase",
    "BrandKitCreate",
    "BrandKitUpdate",
    "BrandKitResponse",
    # Campaign
    "CampaignBase",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    # Post
    "PostBase",
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    # Content
    "ContentGenerationRequest",
    "ContentGenerationResponse",
    "ContentGenerationStatus",
    # Social
    "OAuthInitResponse",
    "OAuthCallbackRequest",
    "SocialAccountResponse",
    # Payment
    "CheckoutSessionRequest",
    "CheckoutSessionResponse",
    "SubscriptionResponse",
    "PaymentTransactionResponse",
    # Pipeline
    "OrchestratorInput",
    "OrchestratorOutput",
    "CarouselFormatDeciderInput",
    "CarouselFormatDeciderOutput",
    "StoryGeneratorInput",
    "StoryGeneratorOutput",
    "ImageGeneratorInput",
    "ImageGeneratorOutput",
    "TextGeneratorInput",
    "TextGeneratorOutput",
    "FinalizerInput",
    "FinalizerOutput",
    "SlideQualityMetrics",
    # Common
    "MessageResponse",
    "ErrorResponse",
]

