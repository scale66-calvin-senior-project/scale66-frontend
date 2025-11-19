"""
Authentication Endpoints - Login, signup, and session management.

Uses Supabase Auth for authentication (recommended for MVP):
- Supabase handles password hashing automatically
- JWT tokens are issued by Supabase
- Email verification can be enabled in Supabase dashboard
- OAuth providers (Google, Apple) can be added in Supabase settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import Client

from app.api.deps import get_supabase_client, get_current_user


router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    # TODO: Add additional fields if needed (e.g., name)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict
    # TODO: Add session expiry info


class UserProfile(BaseModel):
    id: str
    email: str
    subscription_tier: str
    onboarding_completed: bool
    # TODO: Add other profile fields


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Register new user account via Supabase Auth.
    
    Args:
        request: Signup credentials
        supabase: Supabase client
        
    Returns:
        Access token, refresh token, and user profile
    
    TODO: Implement signup flow:
    1. Call supabase.auth.sign_up(email, password)
    2. Create user profile in public.users table (if using custom fields)
    3. Send verification email (handled by Supabase if enabled)
    4. Return tokens and user data
    
    Raises:
        HTTPException: 400 if email already exists or validation fails
    """
    # TODO: Implement Supabase signup
    # try:
    #     response = supabase.auth.sign_up({
    #         "email": request.email,
    #         "password": request.password
    #     })
    #     
    #     # Optionally create user profile in public.users
    #     # supabase.table('users').insert({
    #         'id': response.user.id,
    #         'email': request.email,
    #         'subscription_tier': 'free'
    #     }).execute()
    #     
    #     return AuthResponse(
    #         access_token=response.session.access_token,
    #         refresh_token=response.session.refresh_token,
    #         user=response.user
    #     )
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    pass


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Authenticate user and return JWT tokens.
    
    Args:
        request: Login credentials
        supabase: Supabase client
        
    Returns:
        Access token, refresh token, and user profile
    
    TODO: Implement login flow:
    1. Call supabase.auth.sign_in_with_password(email, password)
    2. Return tokens issued by Supabase
    3. Frontend stores access_token and uses in Authorization header
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # TODO: Implement Supabase login
    # try:
    #     response = supabase.auth.sign_in_with_password({
    #         "email": request.email,
    #         "password": request.password
    #     })
    #     
    #     return AuthResponse(
    #         access_token=response.session.access_token,
    #         refresh_token=response.session.refresh_token,
    #         user=response.user
    #     )
    # except Exception as e:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    pass


@router.post("/logout")
async def logout(
    supabase: Client = Depends(get_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Sign out user and invalidate session.
    
    Args:
        supabase: Supabase client
        current_user: Authenticated user
        
    Returns:
        Success message
    
    TODO: Implement logout:
    1. Call supabase.auth.sign_out()
    2. Frontend should delete stored tokens
    """
    # TODO: Implement Supabase logout
    # supabase.auth.sign_out()
    # return {"message": "Logged out successfully"}
    pass


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get current authenticated user's profile.
    
    Args:
        current_user: Authenticated user from JWT
        supabase: Supabase client
        
    Returns:
        User profile data
    
    TODO: Implement profile fetch:
    1. Extract user_id from current_user
    2. Fetch full profile from public.users table
    3. Return profile data
    """
    # TODO: Fetch user profile
    # user_id = current_user["id"]
    # response = supabase.table('users') \
    #     .select('*') \
    #     .eq('id', user_id) \
    #     .single() \
    #     .execute()
    # 
    # return UserProfile(**response.data)
    pass


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_token: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Valid refresh token
        supabase: Supabase client
        
    Returns:
        New access token and refresh token
    
    TODO: Implement token refresh:
    1. Call supabase.auth.refresh_session(refresh_token)
    2. Return new tokens
    
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    # TODO: Implement token refresh
    # try:
    #     response = supabase.auth.refresh_session(refresh_token)
    #     return AuthResponse(
    #         access_token=response.session.access_token,
    #         refresh_token=response.session.refresh_token,
    #         user=response.user
    #     )
    # except Exception as e:
    #     raise HTTPException(status_code=401, detail="Invalid refresh token")
    pass

