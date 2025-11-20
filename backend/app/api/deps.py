"""
API Dependencies - Reusable dependencies for FastAPI endpoints.

This module provides:
- get_current_user: Verify JWT token from frontend (issued by Supabase Auth)
- get_supabase_client: Inject Supabase client for database operations
- get_supabase_admin: Inject Supabase admin client (bypasses RLS)

Authentication Flow:
1. Frontend authenticates with Supabase Auth directly (signup/login)
2. Supabase issues JWT access token
3. Frontend includes token in Authorization: Bearer <token>
4. Backend validates token and extracts user info via get_current_user()
"""

from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from supabase import Client

from app.core.supabase import get_supabase_client, get_supabase_admin_client


async def get_current_user(
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase_client)
) -> dict:
    """
    Verify Supabase JWT token from Authorization header and return user info.
    
    Args:
        authorization: Authorization header with format "Bearer <token>"
        supabase: Supabase client instance
        
    Returns:
        User object with id, email, and other profile data
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    
    TODO: Implement token verification:
    1. Extract token from "Bearer <token>" format
    2. Verify JWT signature using Supabase JWT secret
    3. Extract user_id from token claims
    4. Optionally fetch user profile from database
    5. Return user object or raise 401
    """
    # TODO: Implement JWT verification
    # if not authorization.startswith("Bearer "):
    #     raise HTTPException(status_code=401, detail="Invalid authorization header")
    # 
    # token = authorization.replace("Bearer ", "")
    # 
    # try:
    #     # Verify token with Supabase
    #     user = supabase.auth.get_user(token)
    #     return user
    # except Exception as e:
    #     raise HTTPException(status_code=401, detail="Invalid or expired token")
    pass


async def get_supabase_admin(
    supabase: Client = Depends(get_supabase_admin_client)
) -> Client:
    """
    Return Supabase client with service role key for admin operations.
    
    Use this for operations that need to bypass Row Level Security (RLS):
    - System-level operations
    - Admin dashboards
    - Background jobs
    
    Args:
        supabase: Supabase admin client instance
        
    Returns:
        Supabase client with service role privileges
    
    TODO: Already implemented by dependency injection
    """
    return supabase


async def verify_subscription(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify user has active paid subscription.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if subscription is active
        
    Raises:
        HTTPException: 403 if user doesn't have active subscription
    
    TODO: Implement subscription verification:
    1. Check user.subscription_tier from database
    2. Verify subscription is active (not expired/cancelled)
    3. Return user if active, raise 403 if not
    """
    # TODO: Implement subscription check
    # if current_user.get("subscription_tier") == "free":
    #     raise HTTPException(
    #         status_code=403, 
    #         detail="This feature requires a paid subscription"
    #     )
    # return current_user
    pass

