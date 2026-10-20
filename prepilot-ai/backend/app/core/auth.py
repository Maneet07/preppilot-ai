import os
import json
import httpx
from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError
from typing import Optional

# Supabase JWT verification settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

# OAuth2 scheme for Bearer tokens
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",
    tokenUrl="",
)


async def get_current_user(request: Request) -> dict:
    """Extract and verify the current user from the Supabase JWT token.
    
    This dependency extracts the Supabase access token from the Authorization header
    and verifies it using the Supabase JWT secret. It returns the user's UUID
    and email, or raises an HTTPException if the token is invalid.
    """
    authorization: str = request.headers.get("Authorization", "")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token"
        )
    
    # Verify the JWT token using Supabase's JWT secret
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID"
            )
        return {"id": user_id, "email": payload.get("email", "")}
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication token: {str(e)}"
        )


async def get_optional_current_user(request: Request) -> Optional[dict]:
    """Optional authentication - returns user if token present, None otherwise."""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


def require_auth(dependencies=None):
    """Decorator to mark routes as requiring authentication."""
    def decorator(func):
        if dependencies is None:
            dependencies = []
        dependencies.append(Depends(get_current_user))
        # Note: FastAPI doesn't easily modify dependencies at runtime,
        # so this is documented for manual application of
        return func
    return decorator