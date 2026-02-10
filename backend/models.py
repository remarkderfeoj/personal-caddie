"""
Pydantic models derived from semantic contracts.
These models validate and serialize data according to the contract specifications.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


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
    club_id: str
    club_type: ClubType
    loft_angle: float = Field(ge=8.5, le=60)
    baseline_carry_distance: int = Field(description="Carry distance in yards under standard conditions")
    baseline_total_distance: int = Field(description="Carry + roll on firm, dry fairway")
    dispersion_margin: int = Field(description="Typical accuracy margin in yards")

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
    carry_distance: int = Field(description="Player's carry distance in yards")
    total_distance: int = Field(description="Carry + roll on dry, firm fairway")
    consistency_notes: Optional[str] = None
    measurement_method: MeasurementMethod


class GeneralCharacteristics(BaseModel):
    """Player's general golf characteristics"""
    gender: Optional[Gender] = None
    typical_swing_speed: Optional[int] = None
    miss_pattern: Optional[MissPattern] = None
    short_game_strength: Optional[ShortGameStrength] = None


class PlayerBaseline(BaseModel):
    """Player baseline contract - personal club distances and characteristics"""
    player_id: str
    player_name: str
    created_date: datetime
    last_updated: Optional[datetime] = None
    club_distances: List[ClubDistance]
    general_characteristics: Optional[GeneralCharacteristics] = None


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
    distance_from_tee_yards: int
    severity: HazardSeverity
    description: Optional[str] = None


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
    hole_id: str
    hole_number: int = Field(ge=1, le=18)
    par: int = Field(enum=[3, 4, 5])
    handicap_index: int = Field(ge=1, le=18)
    distance_to_pin_yards: int
    shot_bearing_degrees: int = Field(ge=0, le=359, description="Compass bearing of shot direction")
    elevation_change_feet: Optional[int] = None
    fairway_type: FairwayType
    hazards: Optional[List[Hazard]] = None
    green_shape: Optional[GreenShape] = None
    notes: Optional[str] = None


class CourseHoles(BaseModel):
    """Complete course information"""
    course_id: str
    course_name: str
    course_elevation_feet: int
    holes: List[Hole] = Field(min_items=18, max_items=18)


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
    condition_id: str
    timestamp: datetime
    temperature_fahrenheit: float
    wind_speed_mph: float = Field(ge=0)
    wind_direction_compass: WindDirection
    humidity_percent: int = Field(ge=0, le=100)
    rain: bool
    ground_conditions: GroundConditions
    recent_rain_history: Optional[RecentRainHistory] = None
    dew_point_fahrenheit: Optional[float] = None


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
    analysis_id: str
    player_id: str
    hole_id: str
    weather_condition_id: str
    pin_location: PinLocation
    current_distance_to_pin_yards: int
    player_lie: PlayerLie
    lie_quality: Optional[LieQuality] = None
    wind_relative_to_shot: Optional[WindRelativeToShot] = None
    wind_strength_estimate: Optional[WindStrengthEstimate] = None
    pin_placement_strategy: Optional[PinPlacementStrategy] = None
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# CADDIE RECOMMENDATION CONTRACT MODELS
# ============================================================================

class PrimaryRecommendation(BaseModel):
    """The main club recommendation"""
    club: ClubType
    target_area: str = Field(description="Where to aim, not just 'center'")
    expected_carry_yards: int
    expected_total_yards: int
    confidence_percent: int = Field(ge=0, le=100)


class AdjustmentSummary(BaseModel):
    """Breakdown of distance adjustments"""
    temperature_adjustment_yards: int = 0
    elevation_adjustment_yards: int = 0
    wind_adjustment_yards: int = 0
    rain_adjustment_percent: float = 0.0
    lie_adjustment_percent: float = 0.0
    human_readable_summary: List[str]


class AlternativeClub(BaseModel):
    """Alternative club option with reasoning"""
    club: ClubType
    confidence_percent: int = Field(ge=0, le=100)
    rationale: str = Field(description="Why this club - must have strategic value")


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
    location: str
    distance_from_tee: int
    risk_level: RiskLevel


class HazardAnalysis(BaseModel):
    """Analysis of hazards for this shot"""
    hazards_in_play: List[HazardInPlay] = []
    safe_miss_direction: Optional[SafeMissDirection] = None


class CaddieRecommendation(BaseModel):
    """Output of caddie recommendation engine"""
    recommendation_id: str
    shot_analysis_id: str
    primary_recommendation: PrimaryRecommendation
    adjustment_summary: AdjustmentSummary
    alternative_clubs: Optional[List[AlternativeClub]] = None
    hazard_analysis: HazardAnalysis
    strategy_notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
