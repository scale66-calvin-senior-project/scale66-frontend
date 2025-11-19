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
    
    TODO: Implement Supabase client initialization:
    
    ```python
    from supabase import create_client
    from app.core.config import settings
    
    client = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key  # anon key
    )
    
    return client
    ```
    
    The anon key respects RLS policies, so users can only access
    their own data (if RLS is configured correctly).
    
    NOTE: Using @lru_cache() to ensure single instance (singleton pattern)
    """
    # TODO: Initialize Supabase client with anon key
    # if not settings.supabase_url or not settings.supabase_key:
    #     raise ValueError("Supabase URL and Key must be configured")
    # 
    # return create_client(settings.supabase_url, settings.supabase_key)
    pass


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
    
    TODO: Implement Supabase admin client initialization:
    
    ```python
    from supabase import create_client
    from app.core.config import settings
    
    client = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_key  # service role key
    )
    
    return client
    ```
    
    Use Cases:
    - Creating users after signup
    - System-wide analytics
    - Data migrations
    - Admin dashboards
    
    NOTE: Using @lru_cache() to ensure single instance
    """
    # TODO: Initialize Supabase admin client with service role key
    # if not settings.supabase_url or not settings.supabase_service_key:
    #     raise ValueError("Supabase URL and Service Key must be configured")
    # 
    # return create_client(settings.supabase_url, settings.supabase_service_key)
    pass


# Dependency injection functions for FastAPI
def get_supabase_dep() -> Client:
    """
    FastAPI dependency for Supabase client.
    
    Usage in endpoints:
    ```python
    @router.get("/example")
    async def example(supabase: Client = Depends(get_supabase_dep)):
        # Use supabase client
        pass
    ```
    
    TODO: Return Supabase client instance
    """
    return get_supabase_client()


def get_supabase_admin_dep() -> Client:
    """
    FastAPI dependency for Supabase admin client.
    
    Usage in endpoints:
    ```python
    @router.get("/admin/example")
    async def admin_example(supabase: Client = Depends(get_supabase_admin_dep)):
        # Use admin client
        pass
    ```
    
    TODO: Return Supabase admin client instance
    """
    return get_supabase_admin_client()

