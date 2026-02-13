"""
Recommendation Engine Module

Main orchestrator for club recommendations:
- Combines physics calculations with course strategy
- Filters viable clubs based on distance
- Applies player strategy preferences
- Generates primary and alternative recommendations
"""

from typing import Dict, Optional
import math
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
    AlternativePlay,
    RiskReward,
    ConfidenceScore,
)
from .physics import (
    calculate_temperature_adjustment,
    calculate_elevation_adjustment,
    calculate_shot_elevation_adjustment,
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
from .player_model import player_service
from .round_context import generate_caddie_note


def calculate_adjusted_distance(
    baseline_carry: int,
    baseline_total: int,
    temperature: float,
    elevation_feet: int,
    elevation_change_feet: int,
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

    # Course altitude adjustment (thin air)
    course_elev_adj = calculate_elevation_adjustment(elevation_feet, baseline_carry)
    adjusted_carry += course_elev_adj

    # Uphill/downhill shot adjustment
    shot_elev_adj = calculate_shot_elevation_adjustment(elevation_change_feet, baseline_carry)
    adjusted_carry += shot_elev_adj

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
            "course_elevation_yards": course_elev_adj,
            "shot_elevation_yards": shot_elev_adj,
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


def calculate_confidence_score(
    match_score: float,
    distance_to_target: int,
    adjusted_distance: int,
    dispersion: int,
    has_elevation_data: bool,
    elevation_change_feet: int,
    has_wind_data: bool,
    wind_speed: float,
    player_lie: str,
    lie_quality: Optional[str],
    is_real_player_data: bool
) -> tuple[ConfidenceScore, str]:
    """
    Calculate calibrated confidence score with detailed factors.
    
    Returns:
        Tuple of (ConfidenceScore, explanation_text)
    """
    # 1. Distance certainty: How well does the club match the distance?
    distance_diff = abs(adjusted_distance - distance_to_target)
    if distance_diff <= dispersion / 2:
        distance_certainty = 1.0
    elif distance_diff <= dispersion:
        distance_certainty = 0.85
    elif distance_diff <= dispersion * 1.5:
        distance_certainty = 0.7
    else:
        distance_certainty = max(0.5, 1.0 - (distance_diff / distance_to_target))
    
    # 2. Elevation certainty: Do we have good elevation data?
    if has_elevation_data and elevation_change_feet != 0:
        # We have real elevation data
        if abs(elevation_change_feet) > 10:
            elevation_certainty = 0.95  # Significant elevation, we accounted for it
        else:
            elevation_certainty = 0.9   # Mild elevation
    elif has_elevation_data and elevation_change_feet == 0:
        elevation_certainty = 1.0  # Flat shot, no uncertainty
    else:
        elevation_certainty = 0.7  # No elevation data, assuming flat
    
    # 3. Wind certainty: Is wind data provided?
    if has_wind_data and wind_speed >= 10:
        wind_certainty = 0.8   # Strong wind, accounted for but variable
    elif has_wind_data and wind_speed >= 5:
        wind_certainty = 0.9   # Moderate wind
    elif wind_speed < 5:
        wind_certainty = 1.0   # Calm, no uncertainty
    else:
        wind_certainty = 0.75  # No wind data, assuming calm
    
    # 4. Lie certainty: How predictable is the lie?
    if player_lie in ["tee", "fairway"] and (lie_quality in ["clean", "normal", None]):
        lie_certainty = 1.0
    elif player_lie == "fairway" and lie_quality == "thick":
        lie_certainty = 0.75
    elif player_lie == "semi_rough":
        lie_certainty = 0.8
    elif player_lie == "rough":
        if lie_quality == "thick":
            lie_certainty = 0.6
        else:
            lie_certainty = 0.7
    elif player_lie == "bunker":
        lie_certainty = 0.65
    else:  # woods, plugged
        lie_certainty = 0.5
    
    # 5. Player data quality: Real player data vs defaults?
    if is_real_player_data:
        player_data_quality = 0.95
    else:
        player_data_quality = 0.7  # Using generic defaults
    
    # Calculate overall confidence using weighted geometric mean
    # This ensures that a low score in any factor significantly impacts overall confidence
    weights = {
        'distance': 0.35,
        'elevation': 0.15,
        'wind': 0.15,
        'lie': 0.20,
        'player_data': 0.15
    }
    
    # Weighted geometric mean: product of (factor^weight)
    overall_confidence = (
        distance_certainty ** weights['distance'] *
        elevation_certainty ** weights['elevation'] *
        wind_certainty ** weights['wind'] *
        lie_certainty ** weights['lie'] *
        player_data_quality ** weights['player_data']
    )
    
    # Build explanation
    explanation_parts = []
    if distance_certainty >= 0.9:
        explanation_parts.append("excellent distance match")
    elif distance_certainty >= 0.75:
        explanation_parts.append("good distance match")
    else:
        explanation_parts.append("distance is marginal")
    
    if elevation_certainty < 0.8:
        explanation_parts.append("elevation estimated")
    
    if wind_certainty < 0.85:
        explanation_parts.append("wind variable")
    
    if lie_certainty < 0.8:
        explanation_parts.append(f"challenging lie")
    
    if player_data_quality < 0.8:
        explanation_parts.append("using default distances")
    
    if not explanation_parts:
        explanation = "All factors look great — high confidence in this recommendation."
    else:
        explanation = f"Good recommendation, but note: {', '.join(explanation_parts)}."
    
    confidence_score = ConfidenceScore(
        distance_certainty=round(distance_certainty, 2),
        elevation_certainty=round(elevation_certainty, 2),
        wind_certainty=round(wind_certainty, 2),
        lie_certainty=round(lie_certainty, 2),
        player_data_quality=round(player_data_quality, 2),
        overall_confidence=round(overall_confidence, 2)
    )
    
    return confidence_score, explanation


def generate_recommendation(
    shot_analysis: ShotAnalysis,
    player_baseline: PlayerBaseline,
    hole: Hole,
    weather: WeatherConditions,
    course_elevation_feet: int = 0,
    elevation_change_feet: int = 0,
    round_context: Optional[Dict] = None
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
            elevation_change_feet=elevation_change_feet,
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

    # 4b. Apply player-specific adjustments (Task 2: Player Model)
    player_profile = player_service.repo.get_profile(shot_analysis.player_id)
    
    if player_profile:
        # Apply fatigue adjustment if on back 9
        hole_number = hole.hole_number
        if hole_number > 9:
            fatigue_multiplier = player_service.get_fatigue_adjustment(shot_analysis.player_id, hole_number)
            for option in viable_clubs:
                option["adjusted_carry"] = int(option["adjusted_carry"] * fatigue_multiplier)
                option["adjusted_total"] = int(option["adjusted_total"] * fatigue_multiplier)
        
        # Apply miss tendency vs hazard location penalty
        for option in viable_clubs:
            club_key = option["club_type"].value if hasattr(option["club_type"], 'value') else str(option["club_type"])
            tendency = player_service.get_player_tendency(shot_analysis.player_id, club_key)
            
            if tendency:
                # Check if player's miss direction aligns with high-risk hazards
                hazards = option["hazard_analysis"]["hazards_in_play"]
                high_risk_on_miss_side = any(
                    h["risk_level"] == "high" and h["location"] == tendency.miss_direction.value
                    for h in hazards
                )
                
                if high_risk_on_miss_side:
                    # Penalize clubs where player's miss tendency points at hazard
                    penalty = int(20 * tendency.miss_frequency)
                    option["match_score"] -= penalty
        
        # Apply comfort ratings as tiebreaker
        for option in viable_clubs:
            club_key = option["club_type"].value if hasattr(option["club_type"], 'value') else str(option["club_type"])
            comfort = player_service.get_comfort_rating(shot_analysis.player_id, club_key)
            
            # Comfort is 0.0-1.0, add 0-10 points
            comfort_bonus = int((comfort - 0.5) * 20)  # Scales from -10 to +10
            option["match_score"] += comfort_bonus

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

    # 7. Generate conviction-first recommendation (Task 4)
    pin_loc = shot_analysis.pin_location.value if hasattr(shot_analysis.pin_location, 'value') else shot_analysis.pin_location
    
    # Extract club as string
    club_str = primary_option["club_type"].value if hasattr(primary_option["club_type"], 'value') else str(primary_option["club_type"])
    club_display = club_str.replace("_", " ").title()
    
    # Generate target area
    target_area = generate_target_area(hole, primary_option["hazard_analysis"], pin_loc)
    
    # Generate caddie call (one-liner)
    caddie_call = f"{club_display}, {target_area.lower()}. Trust it."
    
    # Generate caddie note (situational context from RoundContext)
    if round_context:
        # Use round-aware messaging
        caddie_note = generate_caddie_note(
            momentum=round_context.get("momentum", "steady"),
            round_phase=round_context.get("round_phase", "middle"),
            score_to_par=round_context.get("score_to_par", 0),
            last_hole_score=round_context.get("last_hole_score", hole.par),
            last_hole_par=round_context.get("last_hole_par", hole.par),
            hole_par=hole.par,
            hole_difficulty=round_context.get("hole_difficulty", "average")
        )
    else:
        # Default messaging without round context
        if hole.par == 3:
            caddie_note = "Good par 3. Trust your distance."
        elif hole.par == 5:
            caddie_note = "Scoring hole. Let's make birdie."
        else:
            caddie_note = "Fairway first, then we'll go at the pin."
    
    # Generate "why" explanation
    adj = primary_option["adjustments"]
    adj_parts = []
    if adj.get("course_elevation_yards", 0) > 0:
        adj_parts.append(f"+{adj['course_elevation_yards']}y altitude")
    if adj.get("shot_elevation_yards", 0) != 0:
        direction = "uphill" if adj["shot_elevation_yards"] > 0 else "downhill"
        adj_parts.append(f"{adj['shot_elevation_yards']:+d}y {direction}")
    if adj["wind_yards"] != 0:
        adj_parts.append(f"{adj['wind_yards']:+d}y {wind_relative}")
    if adj["temperature_yards"] != 0:
        adj_parts.append(f"{adj['temperature_yards']:+d}y temp")
    
    hazards = primary_option["hazard_analysis"]["hazards_in_play"]
    if hazards:
        hazard_names = [h["hazard_type"] for h in hazards if h["risk_level"] == "high"]
        if hazard_names:
            adj_parts.append(f"avoid {', '.join(hazard_names)}")
    
    if adj_parts:
        why = f"{club_display} plays {primary_option['adjusted_total']} yards here ({', '.join(adj_parts)})."
    else:
        why = f"{club_display} is the right club for {target_distance} yards."
    
    # Optimal miss and danger zone
    safe_miss = primary_option["hazard_analysis"]["safe_miss_direction"]
    optimal_miss = f"Miss {safe_miss} is safe" if safe_miss and safe_miss != "center" else "Center is fine"
    
    high_risk_hazards = [h for h in hazards if h["risk_level"] == "high"]
    if high_risk_hazards:
        danger_desc = ", ".join([f"{h['hazard_type']} {h['location']}" for h in high_risk_hazards])
        danger_zone = f"Do not miss {danger_desc}"
    else:
        danger_zone = "No major danger zones"
    
    # Generate alternatives (max 2)
    alternatives = []
    for option in viable_clubs[1:3]:
        if len(alternatives) >= 2:
            break
        distance_diff = abs(option["adjusted_total"] - primary_option["adjusted_total"])
        if distance_diff > 10:
            alt_club_str = option["club_type"].value if hasattr(option["club_type"], 'value') else str(option["club_type"])
            alt_club_display = alt_club_str.replace("_", " ").title()
            
            # Determine scenario
            if option["adjusted_total"] < primary_option["adjusted_total"]:
                scenario = f"If you want safety or wind picks up"
                target = f"Lay up to {option['adjusted_total']} yards"
            else:
                scenario = f"If you want more club or wind dies"
                target = f"Take dead aim, {option['adjusted_total']} yards"
            
            alternatives.append(AlternativePlay(
                club=option["club_type"],
                target=target,
                scenario=scenario
            ))
    
    # Generate risk/reward framing
    if strategy == "aggressive":
        aggressive_upside = f"Birdie putt from {10 + hole.par * 2} feet"
        aggressive_downside = f"Possible {high_risk_hazards[0]['hazard_type']} if missed" if high_risk_hazards else "Tough up-and-down"
        conservative_upside = f"25-30 foot putt, makeable for birdie"
        conservative_downside = "Easy two-putt par"
    else:
        aggressive_upside = f"Close look at birdie"
        aggressive_downside = f"Risk of {high_risk_hazards[0]['hazard_type']}" if high_risk_hazards else "Difficult recovery"
        conservative_upside = f"Safe par with birdie chance"
        conservative_downside = "Comfortable two-putt"
    
    risk_reward = RiskReward(
        aggressive_upside=aggressive_upside,
        aggressive_downside=aggressive_downside,
        conservative_upside=conservative_upside,
        conservative_downside=conservative_downside
    )
    
    # 8. Calculate confidence score
    has_elevation_data = elevation_change_feet != 0 or course_elevation_feet > 0
    has_wind_data = weather.wind_speed_mph > 0
    is_real_player_data = len(player_baseline.club_distances) >= 8  # Heuristic: 8+ clubs = real data
    
    confidence_score, confidence_explanation = calculate_confidence_score(
        match_score=primary_option["match_score"],
        distance_to_target=target_distance,
        adjusted_distance=primary_option["adjusted_total"],
        dispersion=primary_option["dispersion"],
        has_elevation_data=has_elevation_data,
        elevation_change_feet=elevation_change_feet,
        has_wind_data=has_wind_data,
        wind_speed=weather.wind_speed_mph,
        player_lie=shot_analysis.player_lie.value if hasattr(shot_analysis.player_lie, 'value') else shot_analysis.player_lie,
        lie_quality=shot_analysis.lie_quality.value if shot_analysis.lie_quality and hasattr(shot_analysis.lie_quality, 'value') else shot_analysis.lie_quality,
        is_real_player_data=is_real_player_data
    )
    
    # 9. Return conviction-first recommendation
    return CaddieRecommendation(
        recommendation_id=f"rec_{shot_analysis.analysis_id}",
        shot_analysis_id=shot_analysis.analysis_id,
        primary_club=primary_option["club_type"],
        primary_target=target_area,
        caddie_call=caddie_call,
        caddie_note=caddie_note,
        why=why,
        adjusted_distance=primary_option["adjusted_total"],
        optimal_miss=optimal_miss,
        danger_zone=danger_zone,
        confidence=confidence_score,
        confidence_explanation=confidence_explanation,
        alternatives=alternatives if alternatives else None,
        risk_reward=risk_reward,
        confidence_percent=min(95, max(50, int(confidence_score.overall_confidence * 100))),
        expected_carry_yards=primary_option["adjusted_carry"]
    )
