"""
Authentication Module

Provides auth dependencies for FastAPI endpoints.
"""

from .dependencies import get_current_user, get_optional_user, User

__all__ = ["get_current_user", "get_optional_user", "User"]
