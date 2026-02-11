"""
SQLAlchemy ORM Models

SECURITY: All database queries MUST use parameterized queries or ORM methods.
Raw string interpolation in SQL is forbidden.

NOTE: These are separate from Pydantic models.
Pydantic = API validation, SQLAlchemy = database schema.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class PlayerBaseline(Base):
    """Player baseline distances - ORM model"""
    __tablename__ = "player_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String(50), unique=True, index=True, nullable=False)
    player_name = Column(String(100), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    club_distances = relationship("ClubDistance", back_populates="player")


class ClubDistance(Base):
    """Individual club distances"""
    __tablename__ = "club_distances"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String(50), ForeignKey("player_baselines.player_id"), nullable=False)
    club_type = Column(String(50), nullable=False)
    carry_distance = Column(Integer, nullable=False)
    total_distance = Column(Integer, nullable=False)
    
    # Relationships
    player = relationship("PlayerBaseline", back_populates="club_distances")


class Course(Base):
    """Golf course"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), unique=True, index=True, nullable=False)
    course_name = Column(String(200), nullable=False)
    course_elevation_feet = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    holes = relationship("Hole", back_populates="course")


class Hole(Base):
    """Individual hole"""
    __tablename__ = "holes"
    
    id = Column(Integer, primary_key=True, index=True)
    hole_id = Column(String(50), unique=True, index=True, nullable=False)
    course_id = Column(String(50), ForeignKey("courses.course_id"), nullable=False)
    hole_number = Column(Integer, nullable=False)
    par = Column(Integer, nullable=False)
    distance_to_pin_yards = Column(Integer, nullable=False)
    shot_bearing_degrees = Column(Integer, nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="holes")


# NOTE: Add more models as needed (PlayerProfile, ShotHistory, etc.)
