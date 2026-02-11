"""
Personal Caddie Recommendation Engine

Core physics calculations and club selection logic for golf shot recommendations.
Combines player baseline distances with real-time weather and course conditions.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from models import (
    PlayerBaseline, ClubDistance, ClubType,
    Hole, Hazard, WeatherConditions,
    ShotAnalysis, CaddieRecommendation,
    PrimaryRecommendation, AdjustmentSummary,
    HazardAnalysis, HazardInPlay, RiskLevel,
    AlternativeClub, SafeMissDirection,
)


# ============================================================================
# PHYSICS CALCULATORS
# ============================================================================

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
    Elevation adjustment: +0.116% distance per foot above sea level.

    Physics: Higher elevation → thinner air → less drag → longer flight

    Args:
        elevation_feet: Course elevation above sea level in feet
        baseline_distance: Player's baseline distance in yards

    Returns:
        Additional yards gained from elevation
    """
    if elevation_feet <= 0:
        return 0

    elevation_multiplier = 1 + (elevation_feet * 0.00116)
    adjusted_distance = baseline_distance * elevation_multiplier

    return round(adjusted_distance - baseline_distance)


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


# ============================================================================
# WIND CONVERTER
# ============================================================================

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
        Tuple of (wind_relative_type, wind_adjustment_yards)
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


# ============================================================================
# COMPREHENSIVE DISTANCE CALCULATOR
# ============================================================================

def calculate_adjusted_distance(
    baseline_carry: int,
    baseline_total: int,
    temperature: float,
    elevation_feet: int,
    wind_relative: str,
    wind_speed: float,
    rain: bool,
    ground_conditions: str,
    player_lie: str,
    lie_quality: Optional[str]
) -> Dict:
    """
    Apply all physics adjustments to baseline distance.

    Returns dictionary with adjusted distances and breakdown of adjustments.
    """
    adjusted_carry = baseline_carry

    temp_adj = calculate_temperature_adjustment(temperature, baseline_carry)
    adjusted_carry += temp_adj

    elev_adj = calculate_elevation_adjustment(elevation_feet, baseline_carry)
    adjusted_carry += elev_adj

    wind_adj = calculate_wind_adjustment(wind_relative, wind_speed, baseline_carry)
    adjusted_carry += wind_adj

    ground_wet = ground_conditions in ["damp", "wet", "muddy"]
    rain_pct = calculate_rain_adjustment(rain, ground_wet)

    lie_pct = calculate_lie_adjustment(player_lie, lie_quality)

    combined_pct_reduction = rain_pct + lie_pct
    adjusted_carry = round(adjusted_carry * (1 - combined_pct_reduction))

    roll_distance = baseline_total - baseline_carry
    if ground_wet or rain:
        roll_distance = round(roll_distance * 0.5)
    adjusted_total = adjusted_carry + roll_distance

    return {
        "adjusted_carry": adjusted_carry,
        "adjusted_total": adjusted_total,
        "adjustments": {
            "temperature_yards": temp_adj,
            "elevation_yards": elev_adj,
            "wind_yards": wind_adj,
            "rain_percent": rain_pct,
            "lie_percent": lie_pct,
            "combined_reduction_percent": combined_pct_reduction
        }
    }


# ============================================================================
# HAZARD ANALYZER
# ============================================================================

def analyze_hazards_for_shot(
    expected_distance: int,
    dispersion_margin: int,
    hole_hazards: List[Hazard]
) -> Dict:
    """
    Identify which hazards are in play for a given shot distance.

    A hazard is "in play" if the shot's expected landing area
    (distance ± dispersion) overlaps with the hazard location.

    Args:
        expected_distance: Adjusted total distance for this club
        dispersion_margin: Accuracy margin in yards
        hole_hazards: List of hazards on this hole

    Returns:
        Dictionary with hazards_in_play and safe_miss_direction
    """
    hazards_in_play = []

    min_distance = expected_distance - dispersion_margin
    max_distance = expected_distance + dispersion_margin

    for hazard in hole_hazards:
        hazard_distance = hazard.distance_from_tee_yards

        if (min_distance - 20) <= hazard_distance <= (max_distance + 20):
            if hazard.severity == "out_of_bounds":
                risk = "high"
            elif hazard.severity == "water":
                risk = "high"
            elif hazard.severity == "bunker":
                risk = "medium" if abs(expected_distance - hazard_distance) < 10 else "low"
            else:
                risk = "medium"

            hazards_in_play.append({
                "hazard_type": hazard.hazard_type,
                "location": hazard.location,
                "distance_from_tee": hazard_distance,
                "risk_level": risk,
                "description": hazard.description
            })

    safe_miss = determine_safe_miss_direction(hazards_in_play)

    return {
        "hazards_in_play": hazards_in_play,
        "safe_miss_direction": safe_miss
    }


def determine_safe_miss_direction(hazards: List[Dict]) -> str:
    """
    Determine the safest direction to miss based on hazard locations.

    Args:
        hazards: List of hazards in play

    Returns:
        Safe miss direction (left, right, center, long, short)
    """
    if not hazards:
        return "center"

    left_count = sum(1 for h in hazards if h["location"] == "left" and h["risk_level"] == "high")
    right_count = sum(1 for h in hazards if h["location"] == "right" and h["risk_level"] == "high")

    if left_count > right_count:
        return "right"
    elif right_count > left_count:
        return "left"
    else:
        return "center"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def estimate_dispersion(club_type: str) -> int:
    """Estimate dispersion margin for a club type."""
    dispersion_map = {
        "driver": 20, "wood_3": 18, "wood_5": 15,
        "iron_2": 15, "iron_3": 14, "iron_4": 13,
        "iron_5": 12, "iron_6": 10, "iron_7": 9,
        "iron_8": 8, "iron_9": 7,
        "pitching_wedge": 5, "gap_wedge": 5,
        "sand_wedge": 6, "lob_wedge": 7
    }
    return dispersion_map.get(club_type, 10)


def generate_target_area(hole: Hole, hazard_analysis: Dict, pin_location: str) -> str:
    """Generate human-readable target area description."""
    safe_miss = hazard_analysis["safe_miss_direction"]
    hazards = hazard_analysis["hazards_in_play"]

    if not hazards:
        return f"Aim {pin_location} of green, no major hazards"

    high_risk = [h for h in hazards if h["risk_level"] == "high"]

    if high_risk:
        hazard_desc = ", ".join([f"{h['hazard_type']} {h['location']}" for h in high_risk])
        return f"Aim {safe_miss}, avoid {hazard_desc}"
    else:
        return f"Aim center, {pin_location} pin position"


def generate_alternative_rationale(
    alt_option: Dict,
    primary_option: Dict,
    strategy: str,
    target_distance: int
) -> Optional[str]:
    """Generate rationale for alternative club recommendation."""
    alt_distance = alt_option["adjusted_total"]
    primary_distance = primary_option["adjusted_total"]

    if alt_distance < primary_distance:
        if alt_distance < target_distance - 10:
            return "Conservative play - lays up short, takes hazards out"
        else:
            return "Safer option with less risk"
    else:
        if alt_distance > target_distance + 10:
            return "Aggressive play - carries hazards, goes long"
        else:
            return "More club for confidence"

    return None


def generate_strategy_notes(
    option: Dict,
    hole: Hole,
    strategy: str,
    pin_location: str
) -> str:
    """Generate strategic guidance for the shot."""
    hazards = option["hazard_analysis"]["hazards_in_play"]
    high_risk = [h for h in hazards if h["risk_level"] == "high"]

    if high_risk:
        if strategy == "conservative":
            return f"Conservative play recommended: High-risk {high_risk[0]['hazard_type']} in play. Play for center of green."
        else:
            return f"Caution: {high_risk[0]['hazard_type']} {high_risk[0]['location']} is in play. Commit to your line."
    else:
        if pin_location == "front":
            return "Pin is accessible - front of green, good birdie opportunity."
        elif pin_location == "back":
            return "Back pin - take enough club, don't leave it short."
        else:
            return "Clean look at the flag - trust your distance."


# ============================================================================
# MAIN RECOMMENDATION ENGINE
# ============================================================================

def generate_recommendation(
    shot_analysis: ShotAnalysis,
    player_baseline: PlayerBaseline,
    hole: Hole,
    weather: WeatherConditions,
    course_elevation_feet: int = 0
) -> CaddieRecommendation:
    """
    Main recommendation engine orchestrator.

    Algorithm:
    1. Calculate wind relative to shot (if not provided)
    2. Calculate adjusted distances for ALL player clubs
    3. Filter clubs that can reach pin (within margin)
    4. Analyze hazards for viable clubs
    5. Apply strategy preference (aggressive/conservative)
    6. Select primary club + alternatives
    7. Calculate confidence
    8. Generate recommendation

    Args:
        shot_analysis: Shot context from user
        player_baseline: Player's club distances
        hole: Hole information
        weather: Weather conditions

    Returns:
        CaddieRecommendation with primary club, alternatives, hazards, strategy
    """

    # 1. Calculate wind relative to shot if not provided
    if not shot_analysis.wind_relative_to_shot or shot_analysis.wind_relative_to_shot == "calm":
        wind_relative, _ = calculate_wind_relative_to_shot(
            weather.wind_direction_compass,
            hole.shot_bearing_degrees,
            weather.wind_speed_mph
        )
    else:
        wind_relative = shot_analysis.wind_relative_to_shot.value if hasattr(shot_analysis.wind_relative_to_shot, 'value') else shot_analysis.wind_relative_to_shot

    # 2. Calculate adjusted distances for all player clubs
    club_options = []
    for club_dist in player_baseline.club_distances:
        adjusted = calculate_adjusted_distance(
            baseline_carry=club_dist.carry_distance,
            baseline_total=club_dist.total_distance,
            temperature=weather.temperature_fahrenheit,
            elevation_feet=course_elevation_feet,
            wind_relative=wind_relative,
            wind_speed=weather.wind_speed_mph,
            rain=weather.rain,
            ground_conditions=weather.ground_conditions.value if hasattr(weather.ground_conditions, 'value') else weather.ground_conditions,
            player_lie=shot_analysis.player_lie.value if hasattr(shot_analysis.player_lie, 'value') else shot_analysis.player_lie,
            lie_quality=shot_analysis.lie_quality.value if shot_analysis.lie_quality and hasattr(shot_analysis.lie_quality, 'value') else shot_analysis.lie_quality
        )

        dispersion = estimate_dispersion(club_dist.club_type.value if hasattr(club_dist.club_type, 'value') else club_dist.club_type)

        club_options.append({
            "club_type": club_dist.club_type,
            "adjusted_carry": adjusted["adjusted_carry"],
            "adjusted_total": adjusted["adjusted_total"],
            "dispersion": dispersion,
            "adjustments": adjusted["adjustments"]
        })

    # 3. Filter clubs within range of pin
    target_distance = shot_analysis.current_distance_to_pin_yards
    viable_clubs = []

    for option in club_options:
        min_reach = option["adjusted_total"] - option["dispersion"]
        max_reach = option["adjusted_total"] + option["dispersion"]

        if min_reach <= target_distance <= max_reach:
            distance_diff = abs(option["adjusted_total"] - target_distance)
            match_score = 100 - (distance_diff / option["dispersion"] * 50)
            match_score = max(0, min(100, match_score))

            option["match_score"] = match_score
            viable_clubs.append(option)

    # If no clubs reach, find closest
    if not viable_clubs:
        for option in club_options:
            distance_diff = abs(option["adjusted_total"] - target_distance)
            option["match_score"] = max(0, 100 - distance_diff)
        viable_clubs = sorted(club_options, key=lambda x: abs(x["adjusted_total"] - target_distance))[:3]

    # 4. Analyze hazards for each viable club
    for option in viable_clubs:
        hazard_analysis = analyze_hazards_for_shot(
            expected_distance=option["adjusted_total"],
            dispersion_margin=option["dispersion"],
            hole_hazards=hole.hazards or []
        )
        option["hazard_analysis"] = hazard_analysis

        high_risk_count = sum(1 for h in hazard_analysis["hazards_in_play"] if h["risk_level"] == "high")
        option["match_score"] -= (high_risk_count * 15)

    # 5. Apply strategy preference
    strategy = shot_analysis.pin_placement_strategy.value if shot_analysis.pin_placement_strategy and hasattr(shot_analysis.pin_placement_strategy, 'value') else (shot_analysis.pin_placement_strategy or "balanced")

    if strategy == "conservative":
        for option in viable_clubs:
            if option["adjusted_total"] < target_distance:
                option["match_score"] += 10
    elif strategy == "aggressive":
        for option in viable_clubs:
            if abs(option["adjusted_total"] - target_distance) < 5:
                option["match_score"] += 10

    # 6. Select primary club
    viable_clubs.sort(key=lambda x: x["match_score"], reverse=True)
    primary_option = viable_clubs[0]

    # 7. Generate primary recommendation
    pin_loc = shot_analysis.pin_location.value if hasattr(shot_analysis.pin_location, 'value') else shot_analysis.pin_location
    primary_rec = PrimaryRecommendation(
        club=primary_option["club_type"],
        target_area=generate_target_area(hole, primary_option["hazard_analysis"], pin_loc),
        expected_carry_yards=primary_option["adjusted_carry"],
        expected_total_yards=primary_option["adjusted_total"],
        confidence_percent=min(95, max(50, int(primary_option["match_score"])))
    )

    # 8. Generate adjustment summary
    adj = primary_option["adjustments"]
    summary_lines = []
    if adj["temperature_yards"] != 0:
        summary_lines.append(f"{adj['temperature_yards']:+d} yards for temperature ({weather.temperature_fahrenheit:.0f}°F)")
    if adj["elevation_yards"] != 0:
        summary_lines.append(f"+{adj['elevation_yards']} yards for elevation")
    if adj["wind_yards"] != 0:
        summary_lines.append(f"{adj['wind_yards']:+d} yards for {wind_relative}")
    if adj["rain_percent"] > 0:
        summary_lines.append(f"-{adj['rain_percent']*100:.0f}% for wet conditions")
    if adj["lie_percent"] > 0:
        lie_str = shot_analysis.player_lie.value if hasattr(shot_analysis.player_lie, 'value') else shot_analysis.player_lie
        summary_lines.append(f"-{adj['lie_percent']*100:.0f}% for {lie_str}")

    adjustment_summary = AdjustmentSummary(
        temperature_adjustment_yards=adj["temperature_yards"],
        elevation_adjustment_yards=adj["elevation_yards"],
        wind_adjustment_yards=adj["wind_yards"],
        rain_adjustment_percent=adj["rain_percent"],
        lie_adjustment_percent=adj["lie_percent"],
        human_readable_summary=summary_lines if summary_lines else ["No significant adjustments"]
    )

    # 9. Generate alternatives
    alternatives = []
    for option in viable_clubs[1:3]:
        distance_diff = abs(option["adjusted_total"] - primary_option["adjusted_total"])
        if distance_diff > 10:
            rationale = generate_alternative_rationale(option, primary_option, strategy, target_distance)
            if rationale:
                alternatives.append(AlternativeClub(
                    club=option["club_type"],
                    confidence_percent=min(90, max(40, int(option["match_score"]))),
                    rationale=rationale
                ))

    # 10. Build hazard analysis for output
    hazard_output = HazardAnalysis(
        hazards_in_play=[
            HazardInPlay(
                hazard_type=h["hazard_type"],
                location=h["location"],
                distance_from_tee=h["distance_from_tee"],
                risk_level=h["risk_level"]
            )
            for h in primary_option["hazard_analysis"]["hazards_in_play"]
        ],
        safe_miss_direction=primary_option["hazard_analysis"]["safe_miss_direction"]
    )

    # 11. Generate strategy notes
    strategy_notes = generate_strategy_notes(primary_option, hole, strategy, pin_loc)

    # 12. Return complete recommendation
    return CaddieRecommendation(
        recommendation_id=f"rec_{shot_analysis.analysis_id}",
        shot_analysis_id=shot_analysis.analysis_id,
        primary_recommendation=primary_rec,
        adjustment_summary=adjustment_summary,
        alternative_clubs=alternatives if alternatives else None,
        hazard_analysis=hazard_output,
        strategy_notes=strategy_notes
    )
