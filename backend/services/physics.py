"""
Physics Calculations Module

Distance adjustments based on environmental conditions:
- Temperature effects on air density
- Elevation effects on air pressure
- Wind resistance and tailwind assistance
- Rain and wet ground effects
- Lie quality penalties
"""

from typing import Optional, Tuple


def calculate_temperature_adjustment(temp_f: float, baseline_distance: int) -> int:
    """
    Temperature adjustment: ±2 yards per 10°F from 70°F baseline.

    Physics: Cold air is denser → more drag → shorter flight
            Hot air is less dense → less drag → longer flight

    Args:
        temp_f: Current temperature in Fahrenheit
        baseline_distance: Player's baseline distance in yards

    Returns:
        Adjustment in yards (positive = add distance, negative = subtract)
    """
    temp_diff = temp_f - 70.0
    adjustment_per_10f = 2
    adjustment = (temp_diff / 10.0) * adjustment_per_10f
    return round(adjustment)


def calculate_elevation_adjustment(elevation_feet: int, baseline_distance: int) -> int:
    """
    Elevation adjustment: ~2% distance per 1000 feet above sea level.

    Physics: Higher elevation → thinner air → less drag → longer flight

    Args:
        elevation_feet: Course elevation above sea level in feet
        baseline_distance: Player's baseline distance in yards

    Returns:
        Additional yards gained from elevation
    """
    if elevation_feet <= 0:
        return 0

    # Rule of thumb: 2% per 1000 ft elevation = 0.00002 per foot
    elevation_multiplier = 1 + (elevation_feet * 0.00002)
    adjusted_distance = baseline_distance * elevation_multiplier

    return round(adjusted_distance - baseline_distance)


def calculate_shot_elevation_adjustment(
    elevation_change_feet: int,
    baseline_distance: int
) -> int:
    """
    Calculate uphill/downhill shot elevation adjustment.
    
    Rule of thumb: 1 yard per 3 feet of elevation change
    - Uphill (positive elevation_change): ball plays LONGER (add distance)
    - Downhill (negative elevation_change): ball plays SHORTER (subtract distance)
    
    Distance-dependent scaling:
    - Longer shots (>200y): elevation matters more (100% adjustment)
    - Mid-range (150-200y): moderate effect (80% adjustment)
    - Short shots (<150y): less effect (60% adjustment)
    
    Clamped to ±15% of baseline distance for realism.
    
    Args:
        elevation_change_feet: Elevation change from ball to target (feet)
                              Positive = uphill, Negative = downhill
        baseline_distance: Shot distance in yards
    
    Returns:
        Adjustment in yards (positive = add, negative = subtract)
    """
    if elevation_change_feet == 0:
        return 0
    
    # Base adjustment: 1 yard per 3 feet
    base_adjustment = elevation_change_feet / 3.0
    
    # Distance-dependent scaling
    if baseline_distance >= 200:
        scaling_factor = 1.0  # 100% effect for long shots
    elif baseline_distance >= 150:
        scaling_factor = 0.8  # 80% effect for mid-range
    else:
        scaling_factor = 0.6  # 60% effect for short shots
    
    adjusted_yards = base_adjustment * scaling_factor
    
    # Clamp to ±15% of baseline distance
    max_adjustment = baseline_distance * 0.15
    adjusted_yards = max(-max_adjustment, min(max_adjustment, adjusted_yards))
    
    return round(adjusted_yards)


def calculate_wind_adjustment(
    wind_relative: str,
    wind_speed_mph: float,
    baseline_distance: int
) -> int:
    """
    Wind adjustment based on relative wind direction.

    Physics:
    - Headwind: -3% to -5% distance (uses -4% average)
    - Tailwind: +3% to +5% distance (uses +4% average)
    - Crosswind: Minimal distance effect, mostly accuracy

    Args:
        wind_relative: Wind direction relative to shot
        wind_speed_mph: Wind speed in mph
        baseline_distance: Player's baseline distance in yards

    Returns:
        Adjustment in yards (positive or negative)
    """
    if wind_relative == "calm" or wind_speed_mph < 5:
        return 0

    # Scale adjustment by wind strength
    if wind_speed_mph < 10:
        strength_factor = 0.5
    elif wind_speed_mph < 15:
        strength_factor = 1.0
    else:
        strength_factor = 1.5

    # Base adjustment percentages
    if wind_relative == "headwind":
        adjustment_pct = -0.04 * strength_factor
    elif wind_relative == "tailwind":
        adjustment_pct = 0.04 * strength_factor
    else:  # crosswind
        adjustment_pct = -0.01 * strength_factor

    adjustment = baseline_distance * adjustment_pct
    return round(adjustment)


def calculate_rain_adjustment(rain: bool, ground_wet: bool) -> float:
    """
    Rain/wet conditions adjustment: -3% to -5% distance reduction.

    Physics:
    - Rain during flight: Wet ball, reduced spin
    - Wet fairway: Reduced roll, ball plugging
    - Wet grooves: Poor contact, less spin

    Args:
        rain: Is it currently raining?
        ground_wet: Is ground wet/damp?

    Returns:
        Percentage reduction (e.g., 0.04 = 4% reduction)
    """
    if rain:
        return 0.05
    elif ground_wet:
        return 0.03
    return 0.0


def calculate_lie_adjustment(lie: str, lie_quality: Optional[str]) -> float:
    """
    Lie adjustment based on ball position.

    Args:
        lie: PlayerLie enum (tee, fairway, rough, bunker, etc.)
        lie_quality: LieQuality enum (clean, normal, thick, plugged)

    Returns:
        Percentage reduction (e.g., 0.10 = 10% reduction)
    """
    if lie in ["tee", "fairway"] and lie_quality in ["clean", "normal", None]:
        return 0.0

    if lie == "semi_rough":
        return 0.05

    if lie == "rough":
        if lie_quality == "thick":
            return 0.25
        return 0.15

    if lie == "bunker":
        return 0.20

    if lie == "woods" or lie_quality == "plugged":
        return 0.35

    return 0.0


def compass_to_degrees(compass: str) -> int:
    """
    Convert compass direction to degrees.

    Args:
        compass: N, NE, E, SE, S, SW, W, NW

    Returns:
        Degrees (0=N, 90=E, 180=S, 270=W)
    """
    compass_map = {
        "N": 0, "NE": 45, "E": 90, "SE": 135,
        "S": 180, "SW": 225, "W": 270, "NW": 315,
        "calm": -1
    }
    return compass_map.get(compass.upper(), -1)


def calculate_wind_relative_to_shot(
    wind_direction_compass: str,
    shot_bearing_degrees: int,
    wind_speed_mph: float
) -> Tuple[str, int]:
    """
    Convert compass wind direction to shot-relative wind.

    Wind direction is where wind is blowing FROM.
    Shot bearing is where shot is headed TO.

    Args:
        wind_direction_compass: Compass direction (N, NE, E, etc.)
        shot_bearing_degrees: Shot direction in degrees (0-359)
        wind_speed_mph: Wind speed

    Returns:
        Tuple of (wind_relative_type, angle_difference)
    """
    if wind_direction_compass == "calm" or wind_speed_mph < 5:
        return ("calm", 0)

    wind_degrees = compass_to_degrees(wind_direction_compass)
    if wind_degrees < 0:
        return ("calm", 0)

    angle_diff = (wind_degrees - shot_bearing_degrees) % 360

    if angle_diff <= 45 or angle_diff >= 315:
        return ("headwind", angle_diff)
    elif 45 < angle_diff <= 135:
        return ("crosswind_left", angle_diff)
    elif 135 < angle_diff <= 225:
        return ("tailwind", angle_diff)
    else:
        return ("crosswind_right", angle_diff)
