"""
Common Models - Shared response schemas used across the API.
"""

from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# =============== Responses ============

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None

# =============== Mixins ===============

class TimestampedMixin(BaseModel):
    """Mixin for timestamped models."""
    created_at: datetime
    updated_at: datetime

# =============== Enums ===============

class PostStatus(str, Enum):
    """Status of the generated posts."""
    DRAFT = "draft"
    PUBLISHED = "published"
    FAILED = "failed"

class PipelineStatus(str, Enum):
    """Status of the pipeline."""
    INITIALIZED = "initialized"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SocialPlatform(str, Enum):
    """Supported social platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"

# =============== Pipeline Base ===============

class BasePipelineStep(BaseModel):
    """Base class for pipeline steps."""
    step_name: str = Field(default="", description="Name of the pipeline step")
    success: bool = Field(default=True, description="Whether the step succeeded")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[int] = Field(default=None, description="Execution time in milliseconds")