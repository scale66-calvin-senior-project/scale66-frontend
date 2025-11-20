"""
Supabase Client Configuration - Initialize and provide Supabase client.

This module provides:
- get_supabase_client(): Client with anon key (respects RLS)
- get_supabase_admin_client(): Client with service role key (bypasses RLS)
"""

from supabase import create_client, Client
from functools import lru_cache

from app.core.config import settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client with anon key (respects Row Level Security).
    
    This client should be used for:
    - User-facing operations
    - Operations that respect RLS policies
    - Frontend-like access patterns
    
    Returns:
        Supabase client instance
    
    Raises:
        ValueError: If Supabase URL or anon key is not configured
    
    The anon key respects RLS policies, so users can only access
    their own data (if RLS is configured correctly).
    
    NOTE: Using @lru_cache() to ensure single instance (singleton pattern)
    """
    if not settings.supabase_url:
        raise ValueError(
            "SUPABASE_URL is not configured. "
            "Please set it in your .env file."
        )
    
    if not settings.supabase_key:
        raise ValueError(
            "SUPABASE_KEY (anon key) is not configured. "
            "Please set it in your .env file."
        )
    
    return create_client(settings.supabase_url, settings.supabase_key)


@lru_cache()
def get_supabase_admin_client() -> Client:
    """
    Get Supabase client with service role key (bypasses Row Level Security).
    
    This client should be used for:
    - Admin operations
    - System-level operations
    - Background jobs
    - Operations that need to bypass RLS
    
    ⚠️ WARNING: This client can access ALL data, bypassing RLS!
    Only use when absolutely necessary.
    
    Returns:
        Supabase admin client instance
    
    Raises:
        ValueError: If Supabase URL or service role key is not configured
    
    Use Cases:
    - Creating users after signup
    - System-wide analytics
    - Data migrations
    - Admin dashboards
    
    NOTE: Using @lru_cache() to ensure single instance (singleton pattern)
    """
    if not settings.supabase_url:
        raise ValueError(
            "SUPABASE_URL is not configured. "
            "Please set it in your .env file."
        )
    
    if not settings.supabase_service_key:
        raise ValueError(
            "SUPABASE_SERVICE_KEY is not configured. "
            "Please set it in your .env file."
        )
    
    return create_client(settings.supabase_url, settings.supabase_service_key)


# Dependency injection functions for FastAPI
def get_supabase_dep() -> Client:
    """
    FastAPI dependency for Supabase client.
    
    Usage in endpoints:
    ```python
    @router.get("/example")
    async def example(supabase: Client = Depends(get_supabase_dep)):
        # Use supabase client (respects RLS)
        result = supabase.table("posts").select("*").execute()
        return result.data
    ```
    
    Returns:
        Supabase client instance (anon key, respects RLS)
    """
    return get_supabase_client()


def get_supabase_admin_dep() -> Client:
    """
    FastAPI dependency for Supabase admin client.
    
    ⚠️ WARNING: This bypasses Row Level Security. Use with caution!
    
    Usage in endpoints:
    ```python
    @router.post("/admin/users")
    async def create_user_system(
        supabase: Client = Depends(get_supabase_admin_dep)
    ):
        # Use admin client (bypasses RLS)
        result = supabase.table("users").insert(user_data).execute()
        return result.data
    ```
    
    Returns:
        Supabase admin client instance (service role key, bypasses RLS)
    """
    return get_supabase_admin_client()

