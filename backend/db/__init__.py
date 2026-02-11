"""
Database Module

Provides SQLAlchemy ORM models and session management.
Ready for PostgreSQL integration in Phase 2.
"""

from .database import Base, engine, get_db, SessionLocal
from . import models
from . import repository

__all__ = ["Base", "engine", "get_db", "SessionLocal", "models", "repository"]
