"""
Pydantic models derived from semantic contracts.
These models validate and serialize data according to the contract specifications.

SECURITY: All models include validation constraints to prevent injection attacks.
"""

from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
import re
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# CLUBS CONTRACT MODELS
# ============================================================================

class ClubType(str, Enum):
    """Club types from clubs.json"""
    DRIVER = "driver"
    WOOD_3 = "wood_3"
    WOOD_5 = "wood_5"
    IRON_2 = "iron_2"
    IRON_3 = "iron_3"
    IRON_4 = "iron_4"
    IRON_5 = "iron_5"
    IRON_6 = "iron_6"
    IRON_7 = "iron_7"
    IRON_8 = "iron_8"
    IRON_9 = "iron_9"
    PITCHING_WEDGE = "pitching_wedge"
    GAP_WEDGE = "gap_wedge"
    SAND_WEDGE = "sand_wedge"
    LOB_WEDGE = "lob_wedge"


class Club(BaseModel):
    """Individual club specification from clubs.json"""
    club_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    club_type: ClubType
    loft_angle: float = Field(ge=8.5, le=60)
    baseline_carry_distance: int = Field(ge=0, le=400, description="Carry distance in yards under standard conditions")
    baseline_total_distance: int = Field(ge=0, le=450, description="Carry + roll on firm, dry fairway")
    dispersion_margin: int = Field(ge=0, le=100, description="Typical accuracy margin in yards")

    class Config:
        use_enum_values = False


# ============================================================================
# PLAYER BASELINE CONTRACT MODELS
# ============================================================================

class MeasurementMethod(str, Enum):
    """How was distance measured?"""
    RANGEFINDER = "rangefinder"
    GPS_WATCH = "gps_watch"
    COURSE_MARKERS = "course_markers"
    ESTIMATED = "estimated"


class Gender(str, Enum):
    """Player gender"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MissPattern(str, Enum):
    """Primary miss pattern"""
    SLICE = "slice"
    HOOK = "hook"
    PULL = "pull"
    PUSH = "push"
    NEUTRAL = "neutral"


class ShortGameStrength(str, Enum):
    """Short game capability"""
    WEAK = "weak"
    AVERAGE = "average"
    STRONG = "strong"


class ClubDistance(BaseModel):
    """Player's baseline distance for a specific club"""
    club_type: ClubType
    carry_distance: int = Field(ge=0, le=400, description="Player's carry distance in yards")
    total_distance: int = Field(ge=0, le=450, description="Carry + roll on dry, firm fairway")
    consistency_notes: Optional[str] = Field(None, max_length=500)
    measurement_method: MeasurementMethod


class GeneralCharacteristics(BaseModel):
    """Player's general golf characteristics"""
    gender: Optional[Gender] = None
    typical_swing_speed: Optional[int] = None
    miss_pattern: Optional[MissPattern] = None
    short_game_strength: Optional[ShortGameStrength] = None


class PlayerBaseline(BaseModel):
    """Player baseline contract - personal club distances and characteristics"""
    player_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    player_name: str = Field(max_length=100)
    created_date: datetime
    last_updated: Optional[datetime] = None
    club_distances: List[ClubDistance]
    general_characteristics: Optional[GeneralCharacteristics] = None
    
    @field_validator('player_name')
    @classmethod
    def sanitize_player_name(cls, v: str) -> str:
        """Strip whitespace and reject HTML/special chars"""
        v = v.strip()
        if '<' in v or '>' in v or '\x00' in v:
            raise ValueError('Invalid characters in player name')
        return v


# ============================================================================
# COURSE HOLES CONTRACT MODELS
# ============================================================================

class HazardType(str, Enum):
    """Types of hazards"""
    WATER = "water"
    BUNKER = "bunker"
    OUT_OF_BOUNDS = "out_of_bounds"
    TREES = "trees"


class HazardLocation(str, Enum):
    """Hazard location"""
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    SHORT = "short"
    LONG = "long"


class HazardSeverity(str, Enum):
    """Hazard severity/penalty"""
    WATER = "water"  # Penalty stroke + drop
    BUNKER = "bunker"  # No penalty, just difficult
    OUT_OF_BOUNDS = "out_of_bounds"  # Penalty stroke + rehit


class Hazard(BaseModel):
    """Hazard on a hole"""
    hazard_type: HazardType
    location: HazardLocation
    distance_from_tee_yards: int = Field(ge=0, le=800)
    severity: HazardSeverity
    description: Optional[str] = Field(None, max_length=500)


class GreenShape(str, Enum):
    """General shape of green"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    NARROW = "narrow"
    WIDE = "wide"
    ELEVATED = "elevated"


class FairwayType(str, Enum):
    """Type of fairway surface"""
    FAIRWAY = "fairway"
    ROUGH = "rough"
    SAND = "sand"
    WATER = "water"


class Hole(BaseModel):
    """Single hole on a golf course"""
    hole_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    hole_number: int = Field(ge=1, le=18)
    par: int = Field(ge=3, le=5)
    handicap_index: int = Field(ge=1, le=18)
    distance_to_pin_yards: int = Field(ge=50, le=700)
    shot_bearing_degrees: int = Field(ge=0, le=359, description="Compass bearing of shot direction")
    elevation_change_feet: Optional[int] = Field(None, ge=-500, le=500)
    fairway_type: FairwayType
    hazards: Optional[List[Hazard]] = None
    green_shape: Optional[GreenShape] = None
    notes: Optional[str] = Field(None, max_length=1000)


class CourseHoles(BaseModel):
    """Complete course information"""
    course_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    course_name: str = Field(max_length=200)
    course_elevation_feet: int = Field(ge=-1000, le=15000)
    holes: List[Hole]
    
    @field_validator('course_name')
    @classmethod
    def sanitize_course_name(cls, v: str) -> str:
        """Strip whitespace and reject HTML/special chars"""
        v = v.strip()
        if '<' in v or '>' in v or '\x00' in v:
            raise ValueError('Invalid characters in course name')
        return v


# ============================================================================
# WEATHER CONDITIONS CONTRACT MODELS
# ============================================================================

class WindDirection(str, Enum):
    """Compass wind direction"""
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"
    CALM = "calm"


class GroundConditions(str, Enum):
    """Fairway moisture conditions"""
    DRY = "dry"
    DAMP = "damp"
    WET = "wet"
    MUDDY = "muddy"


class EstimatedFairwayWetness(str, Enum):
    """Estimated fairway wetness from history"""
    DRY = "dry"
    SLIGHTLY_DAMP = "slightly_damp"
    DAMP = "damp"
    WET = "wet"


class RecentRainHistory(BaseModel):
    """Historical rain data for inferring fairway conditions"""
    rain_past_7_days: bool
    rain_past_14_days: bool
    estimated_fairway_wetness: EstimatedFairwayWetness


class WeatherConditions(BaseModel):
    """Real-time weather data"""
    condition_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    timestamp: datetime
    temperature_fahrenheit: float = Field(ge=-50, le=150)
    wind_speed_mph: float = Field(ge=0, le=100)
    wind_direction_compass: WindDirection
    humidity_percent: int = Field(ge=0, le=100)
    rain: bool
    ground_conditions: GroundConditions
    recent_rain_history: Optional[RecentRainHistory] = None
    dew_point_fahrenheit: Optional[float] = Field(None, ge=-50, le=150)


# ============================================================================
# SHOT ANALYSIS CONTRACT MODELS
# ============================================================================

class PinLocation(str, Enum):
    """Pin location on green"""
    FRONT = "front"
    CENTER = "center"
    BACK = "back"


class PlayerLie(str, Enum):
    """Where the ball is"""
    TEE = "tee"
    FAIRWAY = "fairway"
    ROUGH = "rough"
    BUNKER = "bunker"
    WOODS = "woods"
    SEMI_ROUGH = "semi_rough"


class LieQuality(str, Enum):
    """Quality of the lie"""
    CLEAN = "clean"
    NORMAL = "normal"
    THICK = "thick"
    PLUGGED = "plugged"


class WindRelativeToShot(str, Enum):
    """Wind direction relative to shot direction"""
    HEADWIND = "headwind"
    TAILWIND = "tailwind"
    CROSSWIND_LEFT = "crosswind_left"
    CROSSWIND_RIGHT = "crosswind_right"
    CALM = "calm"


class WindStrengthEstimate(str, Enum):
    """Qualitative wind strength"""
    CALM = "calm"
    LIGHT = "light"
    MODERATE = "moderate"
    STRONG = "strong"


class PinPlacementStrategy(str, Enum):
    """Player's shot strategy"""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"


class ShotAnalysis(BaseModel):
    """Input for caddie recommendation engine"""
    analysis_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    player_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    hole_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    weather_condition_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    pin_location: PinLocation
    current_distance_to_pin_yards: int = Field(ge=1, le=700)
    player_lie: PlayerLie
    lie_quality: Optional[LieQuality] = None
    wind_relative_to_shot: Optional[WindRelativeToShot] = None
    wind_strength_estimate: Optional[WindStrengthEstimate] = None
    pin_placement_strategy: Optional[PinPlacementStrategy] = None
    notes: Optional[str] = Field(None, max_length=1000)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @field_validator('notes')
    @classmethod
    def sanitize_notes(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace and reject HTML/special chars"""
        if v is None:
            return v
        v = v.strip()
        if '<' in v or '>' in v or '\x00' in v:
            raise ValueError('Invalid characters in notes')
        return v


# ============================================================================
# CADDIE RECOMMENDATION CONTRACT MODELS (Task 4: Conviction-First Format)
# ============================================================================

class SafeMissDirection(str, Enum):
    """Safe miss direction given hazards"""
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    LONG = "long"
    SHORT = "short"


class RiskLevel(str, Enum):
    """Risk level of hazard"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HazardInPlay(BaseModel):
    """Hazard relevant to this shot"""
    hazard_type: HazardType
    location: str = Field(max_length=50)
    distance_from_tee: int = Field(ge=0, le=800)
    risk_level: RiskLevel


class AlternativePlay(BaseModel):
    """Alternative club option - clearly secondary"""
    club: ClubType
    target: str = Field(max_length=200, description="Where to aim with this club")
    scenario: str = Field(max_length=300, description="When you'd pick this: 'If wind picks up' or 'If you want safety'")


class RiskReward(BaseModel):
    """Risk/reward framing for aggressive vs conservative play"""
    aggressive_upside: str = Field(max_length=200, description="Best case if aggressive")
    aggressive_downside: str = Field(max_length=200, description="Worst case if aggressive")
    conservative_upside: str = Field(max_length=200, description="Best case if conservative")
    conservative_downside: str = Field(max_length=200, description="Worst case if conservative")


class CaddieRecommendation(BaseModel):
    """
    Conviction-first caddie recommendation.
    
    Philosophy: A great caddie gives you THE play, not a menu of options.
    Alternatives exist but are clearly secondary.
    """
    recommendation_id: str = Field(max_length=50)
    shot_analysis_id: str = Field(max_length=50)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # THE CALL — what a great caddie would say
    primary_club: ClubType
    primary_target: str = Field(max_length=200, description="Where to aim (specific)")
    caddie_call: str = Field(max_length=200, description="The one-liner: '7-iron, center green. Trust it.'")
    caddie_note: str = Field(max_length=500, description="Situational context from round awareness")
    
    # THE REASONING — expandable detail
    why: str = Field(max_length=500, description="Brief explanation of why this is the play")
    adjusted_distance: int = Field(ge=0, le=450, description="Expected total distance")
    optimal_miss: str = Field(max_length=200, description="Where to miss if you miss")
    danger_zone: str = Field(max_length=200, description="Where you absolutely cannot go")
    
    # ALTERNATIVES — max 2, clearly secondary
    alternatives: Optional[List[AlternativePlay]] = Field(None, max_length=2)
    
    # RISK FRAMING
    risk_reward: RiskReward
    
    # LEGACY FIELDS (for backward compatibility during transition)
    confidence_percent: Optional[int] = Field(None, ge=0, le=100)
    expected_carry_yards: Optional[int] = Field(None, ge=0, le=400)


# ============================================================================
# LEGACY MODELS (deprecated, kept for backward compatibility)
# ============================================================================

class PrimaryRecommendation(BaseModel):
    """DEPRECATED: Use CaddieRecommendation fields directly"""
    club: ClubType
    target_area: str = Field(max_length=200)
    expected_carry_yards: int = Field(ge=0, le=400)
    expected_total_yards: int = Field(ge=0, le=450)
    confidence_percent: int = Field(ge=0, le=100)


class AdjustmentSummary(BaseModel):
    """DEPRECATED: Physics adjustments now in 'why' field"""
    temperature_adjustment_yards: int = 0
    elevation_adjustment_yards: int = 0
    wind_adjustment_yards: int = 0
    rain_adjustment_percent: float = 0.0
    lie_adjustment_percent: float = 0.0
    human_readable_summary: List[str]


class AlternativeClub(BaseModel):
    """DEPRECATED: Use AlternativePlay instead"""
    club: ClubType
    confidence_percent: int = Field(ge=0, le=100)
    rationale: str = Field(max_length=500)


class HazardAnalysis(BaseModel):
    """DEPRECATED: Hazards now in optimal_miss and danger_zone fields"""
    hazards_in_play: List[HazardInPlay] = []
    safe_miss_direction: Optional[SafeMissDirection] = None


# ============================================================================
# PLAYER PROFILE CONTRACT MODELS (Task 2)
# ============================================================================

class MissDirection(str, Enum):
    """Primary miss direction"""
    LEFT = "left"
    RIGHT = "right"
    STRAIGHT = "straight"
    INCONSISTENT = "inconsistent"


class DispersionTendency(BaseModel):
    """Miss patterns and accuracy data for a specific club"""
    miss_direction: MissDirection
    miss_frequency: float = Field(ge=0.0, le=1.0, description="Fraction of shots that miss in this direction")
    distance_variance_yards: int = Field(ge=0, le=50, description="Typical distance inconsistency")
    sample_size: int = Field(ge=0, description="Number of shots tracked")


class HoleTypeStats(BaseModel):
    """Performance statistics for a hole type"""
    rounds_played: int = Field(ge=0)
    average_score: float = Field(ge=1.0, le=20.0)
    average_to_par: float = Field(ge=-5.0, le=15.0)
    best_score: int = Field(ge=1, le=20)
    worst_score: int = Field(ge=1, le=20)


class ScoringByPar(BaseModel):
    """Scoring breakdown by par"""
    par_3: Optional[HoleTypeStats] = None
    par_4: Optional[HoleTypeStats] = None
    par_5: Optional[HoleTypeStats] = None


class ScoringHistory(BaseModel):
    """Performance patterns by hole type"""
    by_par: Optional[ScoringByPar] = None
    by_distance_range: Optional[Dict[str, HoleTypeStats]] = None


class FatigueModel(BaseModel):
    """Performance degradation patterns"""
    front_nine_average: Optional[float] = None
    back_nine_average: Optional[float] = None
    fatigue_factor: float = Field(ge=0.0, le=2.0, default=1.0, description="1.0 = no change, >1.0 = worse on back 9")
    distance_loss_back_nine_yards: int = Field(ge=0, le=50, default=0)


class CaddieVoicePreference(str, Enum):
    """Preferred caddie communication style"""
    DECISIVE = "decisive"  # One call, no alternatives
    ANALYTICAL = "analytical"  # Show all the data
    BALANCED = "balanced"  # Primary + context


class RiskTolerance(str, Enum):
    """Default risk tolerance"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class PlayerProfile(BaseModel):
    """Comprehensive player profile with tendencies and learning"""
    profile_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    player_id: str = Field(max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    player_name: str = Field(max_length=100)
    created_date: datetime
    last_updated: Optional[datetime] = None
    dispersion_tendencies: Optional[Dict[str, DispersionTendency]] = None
    comfort_ratings: Optional[Dict[str, float]] = None  # club_type -> 0.0-1.0
    scoring_history: Optional[ScoringHistory] = None
    fatigue_model: Optional[FatigueModel] = None
    caddie_voice_preference: CaddieVoicePreference = CaddieVoicePreference.BALANCED
    risk_tolerance: RiskTolerance = RiskTolerance.BALANCED
    notes: Optional[str] = Field(None, max_length=2000)
    
    @field_validator('player_name')
    @classmethod
    def sanitize_player_name_profile(cls, v: str) -> str:
        """Strip whitespace and reject HTML/special chars"""
        v = v.strip()
        if '<' in v or '>' in v or '\x00' in v:
            raise ValueError('Invalid characters in player name')
        return v
    
    @field_validator('notes')
    @classmethod
    def sanitize_notes_profile(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace and reject HTML/special chars"""
        if v is None:
            return v
        v = v.strip()
        if '<' in v or '>' in v or '\x00' in v:
            raise ValueError('Invalid characters in notes')
        return v


# ============================================================================
# ROUND CONTEXT MODELS (Task 3)
# ============================================================================

class Momentum(str, Enum):
    """Player momentum indicator"""
    HOT = "hot"
    STEADY = "steady"
    COLD = "cold"


class RoundPhase(str, Enum):
    """Phase of the round"""
    EARLY = "early"  # Holes 1-6
    MIDDLE = "middle"  # Holes 7-12
    CLOSING = "closing"  # Holes 13-18


class RoundContext(BaseModel):
    """Context about how the round is progressing"""
    current_hole: int = Field(ge=1, le=18)
    score_to_par: int = Field(ge=-18, le=50, description="Current round score relative to par")
    last_3_holes_scores: List[int] = Field(max_length=3, description="Scores on last 3 holes")
    last_3_holes_pars: List[int] = Field(max_length=3, description="Pars for last 3 holes")
    momentum: Momentum
    round_phase: RoundPhase
