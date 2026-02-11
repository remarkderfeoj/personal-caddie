"""
Database Repository Pattern

SECURITY: All database queries MUST use parameterized queries or ORM methods.
Raw string interpolation in SQL is forbidden.

Example of CORRECT usage:
    session.query(Player).filter(Player.id == player_id).first()
    session.execute(text("SELECT * FROM players WHERE id = :id"), {"id": player_id})

Example of FORBIDDEN usage:
    session.execute(f"SELECT * FROM players WHERE id = '{player_id}'")  # NEVER DO THIS
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from . import models


class PlayerRepository:
    """Repository for player-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_player_by_id(self, player_id: str) -> Optional[models.PlayerBaseline]:
        """
        Get player by ID using ORM.
        
        SECURITY: Uses parameterized ORM query.
        """
        return self.db.query(models.PlayerBaseline).filter(
            models.PlayerBaseline.player_id == player_id
        ).first()
    
    def create_player(self, player_id: str, player_name: str) -> models.PlayerBaseline:
        """
        Create new player.
        
        SECURITY: Uses ORM model creation (safe).
        """
        player = models.PlayerBaseline(
            player_id=player_id,
            player_name=player_name
        )
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player
    
    def example_raw_query_if_needed(self, player_id: str):
        """
        Example of raw SQL if ORM isn't sufficient.
        
        SECURITY: Uses parameterized query with :parameter syntax.
        NEVER use f-strings or .format() in SQL.
        """
        result = self.db.execute(
            text("SELECT * FROM player_baselines WHERE player_id = :id"),
            {"id": player_id}
        )
        return result.fetchall()


# NOTE: Add more repositories as needed (CourseRepository, etc.)
