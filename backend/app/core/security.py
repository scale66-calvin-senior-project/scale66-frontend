"""
Security Utilities - JWT verification and authentication helpers.

This module provides:
- JWT token verification (for Supabase tokens)
- Password hashing (if using custom auth instead of Supabase Auth)
- Token generation helpers
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


# Password hashing functions (if using custom auth instead of Supabase Auth)
def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    
    TODO: Implement password hashing:
    
    NOTE: Only needed if using CUSTOM auth instead of Supabase Auth!
    If using Supabase Auth, password hashing is handled by Supabase.
    
    ```python
    return pwd_context.hash(password)
    ```
    """
    # TODO: Implement if using custom auth
    # return pwd_context.hash(password)
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    
    TODO: Implement password verification:
    
    NOTE: Only needed if using CUSTOM auth instead of Supabase Auth!
    If using Supabase Auth, password verification is handled by Supabase.
    
    ```python
    return pwd_context.verify(plain_password, hashed_password)
    ```
    """
    # TODO: Implement if using custom auth
    # return pwd_context.verify(plain_password, hashed_password)
    pass


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token (e.g., {"sub": user_id})
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    
    TODO: Implement token creation:
    
    NOTE: Only needed if using CUSTOM auth instead of Supabase Auth!
    If using Supabase Auth, tokens are issued by Supabase.
    
    ```python
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm="HS256"
    )
    
    return encoded_jwt
    ```
    """
    # TODO: Implement if using custom auth
    pass

