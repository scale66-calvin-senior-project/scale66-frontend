"""
Common Models - Shared response schemas used across the API.
"""

from typing import Optional
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None

