"""
Player Model Module

Manages player profiles, tendencies, and performance history.
Implements learning and adaptation based on accumulated data.

Uses repository pattern for data persistence - designed to swap
between JSON file storage (MVP) and PostgreSQL (Phase 2).
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime
import json
import os
from pathlib import Path

from models import (
    PlayerProfile,
    DispersionTendency,
    HoleTypeStats,
    ScoringHistory,
    ScoringByPar,
    FatigueModel,
    ClubType,
)


# ============================================================================
# REPOSITORY PATTERN
# ============================================================================

class PlayerRepository(ABC):
    """Abstract repository for player profile persistence"""
    
    @abstractmethod
    def get_profile(self, player_id: str) -> Optional[PlayerProfile]:
        """Retrieve player profile by ID"""
        pass
    
    @abstractmethod
    def save_profile(self, profile: PlayerProfile) -> None:
        """Save or update player profile"""
        pass
    
    @abstractmethod
    def profile_exists(self, player_id: str) -> bool:
        """Check if profile exists"""
        pass


class JSONPlayerRepository(PlayerRepository):
    """JSON file-based player profile storage"""
    
    def __init__(self, data_dir: str = "data/players"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, player_id: str) -> Path:
        """Get file path for player profile"""
        return self.data_dir / f"{player_id}.json"
    
    def get_profile(self, player_id: str) -> Optional[PlayerProfile]:
        """Load profile from JSON file"""
        file_path = self._get_file_path(player_id)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return PlayerProfile(**data)
        except Exception as e:
            print(f"Error loading profile {player_id}: {e}")
            return None
    
    def save_profile(self, profile: PlayerProfile) -> None:
        """Save profile to JSON file"""
        file_path = self._get_file_path(profile.player_id)
        profile.last_updated = datetime.now()
        
        try:
            with open(file_path, 'w') as f:
                json.dump(profile.model_dump(mode='json'), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving profile {profile.player_id}: {e}")
            raise
    
    def profile_exists(self, player_id: str) -> bool:
        """Check if profile file exists"""
        return self._get_file_path(player_id).exists()


# ============================================================================
# PLAYER MODEL SERVICE
# ============================================================================

class PlayerModelService:
    """Service for player profile management and learning"""
    
    def __init__(self, repository: PlayerRepository):
        self.repo = repository
    
    def get_or_create_profile(self, player_id: str, player_name: str) -> PlayerProfile:
        """Get existing profile or create new one"""
        profile = self.repo.get_profile(player_id)
        if profile:
            return profile
        
        # Create new profile with defaults
        profile = PlayerProfile(
            profile_id=f"profile_{player_id}",
            player_id=player_id,
            player_name=player_name,
            created_date=datetime.now(),
            dispersion_tendencies={},
            comfort_ratings={},
            scoring_history=ScoringHistory(
                by_par=ScoringByPar(),
                by_distance_range={}
            ),
            fatigue_model=FatigueModel()
        )
        self.repo.save_profile(profile)
        return profile
    
    def update_player_after_shot(
        self,
        player_id: str,
        club_type: str,
        actual_distance: int,
        expected_distance: int,
        miss_direction: Optional[str] = None
    ) -> None:
        """
        Update player profile after a shot.
        
        Args:
            player_id: Player identifier
            club_type: Club used
            actual_distance: Actual distance achieved
            expected_distance: Expected distance
            miss_direction: Direction of miss (left/right/straight)
        """
        profile = self.repo.get_profile(player_id)
        if not profile:
            return
        
        if not profile.dispersion_tendencies:
            profile.dispersion_tendencies = {}
        
        # Update or create dispersion tendency for this club
        if club_type in profile.dispersion_tendencies:
            tendency = profile.dispersion_tendencies[club_type]
            
            # Update running average for distance variance
            old_variance = tendency.distance_variance_yards
            old_sample = tendency.sample_size
            distance_diff = abs(actual_distance - expected_distance)
            
            new_variance = ((old_variance * old_sample) + distance_diff) / (old_sample + 1)
            tendency.distance_variance_yards = int(new_variance)
            tendency.sample_size += 1
            
            # Update miss direction if provided
            if miss_direction:
                # Simple exponential moving average
                if tendency.miss_direction.value == miss_direction:
                    tendency.miss_frequency = min(1.0, tendency.miss_frequency + 0.1)
                else:
                    tendency.miss_frequency = max(0.0, tendency.miss_frequency - 0.05)
        else:
            # Create new tendency
            profile.dispersion_tendencies[club_type] = DispersionTendency(
                miss_direction=miss_direction or "straight",
                miss_frequency=0.5,
                distance_variance_yards=abs(actual_distance - expected_distance),
                sample_size=1
            )
        
        self.repo.save_profile(profile)
    
    def update_player_after_round(
        self,
        player_id: str,
        round_summary: Dict
    ) -> None:
        """
        Update player profile after a complete round.
        
        Args:
            player_id: Player identifier
            round_summary: Dictionary containing:
                - scores_by_hole: List of scores
                - pars_by_hole: List of pars
                - front_nine_score: Total for front 9
                - back_nine_score: Total for back 9
        """
        profile = self.repo.get_profile(player_id)
        if not profile:
            return
        
        # Update fatigue model
        if not profile.fatigue_model:
            profile.fatigue_model = FatigueModel()
        
        front_score = round_summary.get('front_nine_score', 0)
        back_score = round_summary.get('back_nine_score', 0)
        front_par = round_summary.get('front_nine_par', 36)
        back_par = round_summary.get('back_nine_par', 36)
        
        front_to_par = front_score - front_par
        back_to_par = back_score - back_par
        
        # Update running averages
        if profile.fatigue_model.front_nine_average is None:
            profile.fatigue_model.front_nine_average = float(front_to_par)
            profile.fatigue_model.back_nine_average = float(back_to_par)
        else:
            # Exponential moving average with alpha=0.3
            alpha = 0.3
            profile.fatigue_model.front_nine_average = (
                alpha * front_to_par + (1 - alpha) * profile.fatigue_model.front_nine_average
            )
            profile.fatigue_model.back_nine_average = (
                alpha * back_to_par + (1 - alpha) * profile.fatigue_model.back_nine_average
            )
        
        # Calculate fatigue factor
        if profile.fatigue_model.front_nine_average != 0:
            profile.fatigue_model.fatigue_factor = (
                profile.fatigue_model.back_nine_average / profile.fatigue_model.front_nine_average
            )
        
        self.repo.save_profile(profile)
    
    def get_player_tendency(
        self,
        player_id: str,
        club_type: str
    ) -> Optional[DispersionTendency]:
        """
        Get player's tendency for a specific club.
        
        Returns:
            DispersionTendency or None if not enough data
        """
        profile = self.repo.get_profile(player_id)
        if not profile or not profile.dispersion_tendencies:
            return None
        
        return profile.dispersion_tendencies.get(club_type)
    
    def get_comfort_rating(self, player_id: str, club_type: str) -> float:
        """
        Get player's comfort rating for a club (0.0-1.0).
        
        Returns:
            Comfort rating, defaults to 0.5 if unknown
        """
        profile = self.repo.get_profile(player_id)
        if not profile or not profile.comfort_ratings:
            return 0.5
        
        return profile.comfort_ratings.get(club_type, 0.5)
    
    def set_comfort_rating(
        self,
        player_id: str,
        club_type: str,
        rating: float
    ) -> None:
        """Set player's comfort rating for a club"""
        profile = self.repo.get_profile(player_id)
        if not profile:
            return
        
        if not profile.comfort_ratings:
            profile.comfort_ratings = {}
        
        profile.comfort_ratings[club_type] = max(0.0, min(1.0, rating))
        self.repo.save_profile(profile)
    
    def get_fatigue_adjustment(self, player_id: str, hole_number: int) -> float:
        """
        Get distance adjustment factor for fatigue.
        
        Args:
            player_id: Player identifier
            hole_number: Current hole (1-18)
        
        Returns:
            Multiplier for distance (e.g., 0.95 = 5% reduction)
        """
        profile = self.repo.get_profile(player_id)
        if not profile or not profile.fatigue_model:
            return 1.0
        
        if hole_number <= 9:
            return 1.0
        
        # Back 9 - apply fatigue
        distance_loss = profile.fatigue_model.distance_loss_back_nine_yards
        if distance_loss > 0:
            # Assume baseline distance of 150 yards for calculation
            return 1.0 - (distance_loss / 150.0)
        
        return 1.0


# ============================================================================
# GLOBAL SERVICE INSTANCE
# ============================================================================

# Initialize with JSON repository (can be swapped to PostgreSQL later)
_default_repository = JSONPlayerRepository()
player_service = PlayerModelService(_default_repository)
