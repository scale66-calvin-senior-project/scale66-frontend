"""
Payment Endpoints - Stripe integration for subscriptions.

Handles:
- Subscription creation and management
- Payment webhooks from Stripe
- Billing portal access
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from supabase import Client

from app.api.deps import get_supabase_client, get_current_user
from app.core.config import settings


router = APIRouter(prefix="/payment", tags=["payment"])


# Request/Response Models
class CheckoutSessionRequest(BaseModel):
    price_id: str  # Stripe price ID for subscription plan
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    subscription_id: str
    status: str  # "active", "canceled", "past_due", etc.
    plan: str
    current_period_end: str


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create Stripe checkout session for subscription.
    
    Args:
        request: Checkout session parameters
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Checkout URL for redirect
    
    TODO: Implement Stripe checkout:
    1. Import stripe library
    2. Get or create Stripe customer for user
    3. Create checkout session with price_id
    4. Store session info in database
    5. Return checkout URL
    
    Example:
    ```python
    import stripe
    stripe.api_key = settings.stripe_secret_key
    
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": request.price_id, "quantity": 1}],
        success_url=request.success_url,
        cancel_url=request.cancel_url,
        metadata={"user_id": current_user["id"]}
    )
    ```
    """
    # TODO: Implement Stripe checkout
    pass


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    This endpoint receives events from Stripe about:
    - Successful payments
    - Subscription updates
    - Payment failures
    - Subscription cancellations
    
    Args:
        request: Raw webhook request
        
    Returns:
        Success acknowledgment
    
    TODO: Implement webhook handler:
    1. Verify webhook signature using Stripe webhook secret
    2. Parse event type
    3. Handle relevant events:
       - checkout.session.completed: Activate subscription
       - customer.subscription.updated: Update subscription status
       - customer.subscription.deleted: Cancel subscription
       - invoice.payment_failed: Handle failed payment
    4. Update user subscription in database
    5. Send confirmation email if needed
    
    IMPORTANT: This endpoint should NOT require authentication (Stripe calls it)
    IMPORTANT: Must verify webhook signature for security
    
    Example:
    ```python
    import stripe
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Update user subscription
    ```
    """
    # TODO: Implement webhook handler
    pass


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get current user's subscription status.
    
    Args:
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Subscription details
    
    TODO: Implement subscription fetch:
    1. Get user's Stripe customer ID from database
    2. Fetch subscription from Stripe
    3. Return subscription details
    """
    # TODO: Implement get subscription
    pass


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Cancel user's subscription.
    
    Args:
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Cancellation confirmation
    
    TODO: Implement subscription cancellation:
    1. Get user's Stripe subscription ID
    2. Cancel subscription in Stripe (immediate or at period end)
    3. Update database
    4. Return confirmation
    """
    # TODO: Implement cancel
    pass


@router.post("/create-portal-session")
async def create_billing_portal_session(
    return_url: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create Stripe billing portal session for subscription management.
    
    Args:
        return_url: URL to return to after portal session
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Billing portal URL
    
    TODO: Implement billing portal:
    1. Get user's Stripe customer ID
    2. Create portal session
    3. Return portal URL
    
    Example:
    ```python
    portal_session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url
    )
    return {"url": portal_session.url}
    ```
    """
    # TODO: Implement billing portal
    pass

