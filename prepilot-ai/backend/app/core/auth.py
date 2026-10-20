import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Optional

# Freebuff native authentication
# In Freebuff Sites, authentication is handled via Sign in with Freebuff (OIDC)
# The env.FREEBUFF_CLIENT_ID, env.FREEBUFF_ISSUER, and env.APP_ORIGIN are injected

# OAuth2 scheme for Bearer tokens
# Token URL and authorization URL are set based on Freebuff configuration
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",
    tokenUrl="",
)


async def get_current_user(request: Request) -> dict:
    """Extract and verify the current user from Freebuff authentication.

    In Freebuff Sites, users are authenticated via Sign in with Freebuff (OIDC).
    The user's identity is available through the request's user object or
    through session management.

    Returns the user's ID and email, or raises HTTPException if not authenticated.
    """
    # Try to get user from request state (Freebuff injects user in development)
    user = getattr(request, 'state', {}).get('user', None)

    if user:
        return {"id": str(user.get("sub", "")), "email": user.get("email", "")}

    # Fall back to checking Authorization header with Freebuff JWT
    authorization: str = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
        )

    # Verify the token using Freebuff's public key
    # In production, use the FREEBUFF_JWT_SECRET from environment
    freebuff_jwt_secret = os.getenv("FREEBUFF_JWT_SECRET", "")

    try:
        import jwt as jose_jwt
        from jose import JWTError

        payload = jose_jwt.decode(
            token,
            freebuff_jwt_secret,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{os.getenv('FREEBUFF_ISSUER', '')}/auth/v1",
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID",
            )
        return {"id": user_id, "email": payload.get("email", "")}
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication token: {str(e)}",
        )


async def get_optional_current_user(request: Request) -> Optional[dict]:
    """Optional authentication - returns user if token present, None otherwise."""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


def require_auth():
    """Decorator marker for routes requiring authentication.

    Note: FastAPI uses Depends(get_current_user) directly on route functions.
    This is a marker function for documentation purposes.
    """
    from fastapi import Depends
    return Depends(get_current_user)
