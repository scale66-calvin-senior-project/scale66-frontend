"""
Payment Models - Pydantic schemas for Stripe payment and subscription management.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


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

