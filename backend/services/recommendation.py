"""
Recommendation Engine Module

Main orchestrator for club recommendations:
- Combines physics calculations with course strategy
- Filters viable clubs based on distance
- Applies player strategy preferences
- Generates primary and alternative recommendations
"""

from typing import Dict, Optional
from models import (
    PlayerBaseline,
    Hole,
    WeatherConditions,
    ShotAnalysis,
    CaddieRecommendation,
    PrimaryRecommendation,
    AdjustmentSummary,
    HazardAnalysis,
    HazardInPlay,
    AlternativeClub,
)
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
    generate_target_area,
    generate_strategy_notes,
)


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


def estimate_dispersion(club_type: str) -> int:
    """
    Estimate dispersion margin for a club type.
    
    Args:
        club_type: Club type identifier
    
    Returns:
        Dispersion in yards
    """
    dispersion_map = {
        "driver": 20, "wood_3": 18, "wood_5": 15,
        "iron_2": 15, "iron_3": 14, "iron_4": 13,
        "iron_5": 12, "iron_6": 10, "iron_7": 9,
        "iron_8": 8, "iron_9": 7,
        "pitching_wedge": 5, "gap_wedge": 5,
        "sand_wedge": 6, "lob_wedge": 7
    }
    return dispersion_map.get(club_type, 10)


def generate_alternative_rationale(
    alt_option: Dict,
    primary_option: Dict,
    strategy: str,
    target_distance: int
) -> Optional[str]:
    """
    Generate rationale for alternative club recommendation.
    
    Args:
        alt_option: Alternative club option
        primary_option: Primary club option
        strategy: Player strategy
        target_distance: Target distance to pin
    
    Returns:
        Rationale string or None
    """
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
        course_elevation_feet: Course elevation above sea level

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
