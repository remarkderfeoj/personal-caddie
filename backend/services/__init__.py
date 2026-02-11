"""
Services Module

Re-exports for backward compatibility with main.py.
"""

from .recommendation import generate_recommendation
from .physics import (
    calculate_temperature_adjustment,
    calculate_elevation_adjustment,
    calculate_wind_adjustment,
    calculate_rain_adjustment,
    calculate_lie_adjustment,
    calculate_wind_relative_to_shot,
)
from .course_strategy import (
    analyze_hazards_for_shot,
    determine_safe_miss_direction,
    generate_target_area,
    generate_strategy_notes,
)

__all__ = [
    "generate_recommendation",
    "calculate_temperature_adjustment",
    "calculate_elevation_adjustment",
    "calculate_wind_adjustment",
    "calculate_rain_adjustment",
    "calculate_lie_adjustment",
    "calculate_wind_relative_to_shot",
    "analyze_hazards_for_shot",
    "determine_safe_miss_direction",
    "generate_target_area",
    "generate_strategy_notes",
]
