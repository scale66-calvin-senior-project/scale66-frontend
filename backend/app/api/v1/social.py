"""
Social Media Integration Endpoints - OAuth and account management.

Handles OAuth connections for:
- Instagram
- TikTok
- Future: Twitter, LinkedIn, etc.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client

from app.api.deps import get_supabase_client, get_current_user


router = APIRouter(prefix="/social", tags=["social_media"])


# Request/Response Models
class OAuthInitResponse(BaseModel):
    authorization_url: str
    state: str  # CSRF protection


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str


class SocialAccountResponse(BaseModel):
    id: str
    user_id: str
    platform: str  # "instagram", "tiktok"
    platform_user_id: str
    platform_username: str
    access_token: str  # Encrypted
    refresh_token: Optional[str] = None
    expires_at: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


@router.get("/connect/{platform}", response_model=OAuthInitResponse)
async def initiate_oauth(
    platform: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Initiate OAuth flow for social media platform.
    
    Args:
        platform: Social media platform ("instagram" or "tiktok")
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        OAuth authorization URL and CSRF state
    
    TODO: Implement OAuth initiation:
    1. Generate CSRF state token
    2. Store state in database/cache
    3. Build OAuth authorization URL with proper scopes
    4. Return URL for frontend to redirect
    
    Instagram Scopes: instagram_basic, instagram_content_publish
    TikTok Scopes: user.info.basic, video.upload
    
    Raises:
        HTTPException: 400 if platform not supported
    """
    # TODO: Implement OAuth init
    # if platform not in ["instagram", "tiktok"]:
    #     raise HTTPException(status_code=400, detail="Platform not supported")
    # 
    # import secrets
    # state = secrets.token_urlsafe(32)
    # 
    # # Store state for verification
    # # TODO: Store in Redis or database
    # 
    # if platform == "instagram":
    #     auth_url = f"https://api.instagram.com/oauth/authorize?client_id={INSTAGRAM_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=instagram_basic,instagram_content_publish&response_type=code&state={state}"
    # elif platform == "tiktok":
    #     auth_url = f"https://www.tiktok.com/auth/authorize?client_key={TIKTOK_CLIENT_KEY}&redirect_uri={REDIRECT_URI}&scope=user.info.basic,video.upload&response_type=code&state={state}"
    # 
    # return OAuthInitResponse(authorization_url=auth_url, state=state)
    pass


@router.post("/callback/{platform}", response_model=SocialAccountResponse)
async def oauth_callback(
    platform: str,
    callback_data: OAuthCallbackRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Handle OAuth callback and store access tokens.
    
    Args:
        platform: Social media platform
        callback_data: OAuth code and state from callback
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Connected social account
    
    TODO: Implement OAuth callback:
    1. Verify state token matches stored value
    2. Exchange code for access token
    3. Fetch user profile from platform
    4. Store encrypted access token in database
    5. Return connected account info
    
    Raises:
        HTTPException: 400 if state invalid or token exchange fails
    """
    # TODO: Implement OAuth callback
    # # Verify state
    # # TODO: Check state matches stored value
    # 
    # # Exchange code for token
    # if platform == "instagram":
    #     # POST to https://api.instagram.com/oauth/access_token
    #     # Get long-lived token
    #     pass
    # elif platform == "tiktok":
    #     # POST to https://open-api.tiktok.com/oauth/access_token/
    #     pass
    # 
    # # Store account
    # user_id = current_user["id"]
    # account_data = {
    #     'user_id': user_id,
    #     'platform': platform,
    #     'platform_user_id': platform_user_id,
    #     'platform_username': platform_username,
    #     'access_token': encrypted_token,  # TODO: Encrypt
    #     'refresh_token': refresh_token,
    #     'expires_at': expires_at,
    #     'is_active': True
    # }
    # 
    # response = supabase.table('social_media_accounts') \
    #     .insert(account_data) \
    #     .execute()
    # 
    # return SocialAccountResponse(**response.data[0])
    pass


@router.get("/accounts", response_model=List[SocialAccountResponse])
async def list_connected_accounts(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    List all connected social media accounts for user.
    
    Args:
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        List of connected accounts
    
    TODO: Implement list accounts:
    1. Query social_media_accounts table by user_id
    2. Return list of accounts
    """
    # TODO: Implement list
    pass


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_account(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Disconnect social media account.
    
    Args:
        account_id: Social account UUID
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        None (204 No Content)
    
    TODO: Implement disconnect:
    1. Verify account belongs to user
    2. Optionally revoke token on platform
    3. Delete account record or mark as inactive
    """
    # TODO: Implement disconnect
    pass


@router.post("/accounts/{account_id}/refresh")
async def refresh_access_token(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Refresh expired access token.
    
    Args:
        account_id: Social account UUID
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Updated account with new token
    
    TODO: Implement token refresh:
    1. Fetch account details
    2. Use refresh token to get new access token
    3. Update stored tokens
    4. Return updated account
    """
    # TODO: Implement refresh
    pass

