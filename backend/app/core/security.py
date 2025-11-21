"""
Security Utilities - JWT token verification for Supabase Auth.

This module provides JWT verification for tokens issued by Supabase Auth.

Frontend Authentication Flow:
1. Frontend calls Supabase Auth directly (signup, login, OAuth)
2. Supabase issues JWT access token
3. Frontend includes token in Authorization header
4. Backend validates token using functions in this module

Backend's Role:
- Verify JWT tokens issued by Supabase
- Extract user info from token claims
- Protect endpoints via get_current_user dependency

This module does NOT:
- Handle signup/login (frontend → Supabase)
- Hash passwords (Supabase handles this)
- Issue tokens (Supabase issues tokens)
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context (if using custom auth)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_supabase_jwt(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Supabase JWT token and extract claims.
    
    Args:
        token: JWT token string (without "Bearer " prefix)
        
    Returns:
        Token payload (claims) if valid, None if invalid
    
    TODO: Implement JWT verification:
    
    Supabase uses JWT tokens issued by their Auth service.
    These tokens need to be verified using the Supabase JWT secret.
    
    ```python
    from jose import jwt, JWTError
    
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"  # Supabase default audience
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            return None  # Token expired
        
        return payload  # Contains user_id, email, etc.
        
    except JWTError:
        return None  # Invalid token
    ```
    
    Token payload structure:
    {
        "sub": "user-uuid",  # User ID
        "email": "user@example.com",
        "aud": "authenticated",
        "role": "authenticated",
        "exp": 1234567890,
        "iat": 1234567890
    }
    
    Usage in API:
    ```python
    token = "eyJhbGciOiJIUzI1NiIs..."
    payload = verify_supabase_jwt(token)
    if payload:
        user_id = payload["sub"]
        email = payload["email"]
    ```
    """
    # TODO: Implement JWT verification
    # try:
    #     payload = jwt.decode(
    #         token,
    #         settings.supabase_jwt_secret,
    #         algorithms=["HS256"],
    #         audience="authenticated"
    #     )
    #     return payload
    # except JWTError:
    #     return None
    pass


def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
        
    Returns:
        Token string if valid format, None otherwise
    
    TODO: Implement token extraction:
    
    Expected format: "Bearer <token>"
    
    ```python
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    # Extract token after "Bearer "
    token = authorization.replace("Bearer ", "", 1)
    return token
    ```
    """
    # TODO: Implement token extraction
    # if not authorization or not authorization.startswith("Bearer "):
    #     return None
    # return authorization.replace("Bearer ", "", 1)
    pass


# Note: Password hashing, verification, and token creation functions
# are NOT needed because we use Supabase Auth.
#
# Supabase Auth handles:
# - Password hashing (bcrypt)
# - Password verification
# - JWT token issuance
# - Token refresh
# - OAuth flows
#
# Backend only needs to VERIFY tokens issued by Supabase (see verify_supabase_jwt above)

