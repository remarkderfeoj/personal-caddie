"""
Authentication Dependencies

TODO: Replace with JWT/OAuth2 auth before deploying to production.

This is a stub implementation for now - just scaffolds the pattern.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)


class User:
    """User model (stub)"""
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Get current authenticated user.
    
    TODO: Implement real JWT/OAuth2 validation here.
    For now, returns a hardcoded user for testing.
    
    Production implementation should:
    1. Validate JWT token
    2. Check token expiration
    3. Load user from database
    4. Verify permissions
    
    Args:
        credentials: Bearer token from Authorization header
    
    Returns:
        User object
    
    Raises:
        HTTPException: If authentication fails
    """
    # TODO: Remove this hardcoded user and implement real auth
    return User(user_id="joe_kramer_001", username="Joe Kramer")
    
    # Future implementation:
    # if not credentials:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Not authenticated",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # 
    # try:
    #     # Validate JWT token
    #     payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    #     user_id = payload.get("sub")
    #     if user_id is None:
    #         raise HTTPException(status_code=401, detail="Invalid token")
    #     
    #     # Load user from database
    #     user = get_user_from_db(user_id)
    #     return user
    # except jwt.JWTError:
    #     raise HTTPException(status_code=401, detail="Invalid token")


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Use for endpoints that work both authenticated and anonymous.
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
