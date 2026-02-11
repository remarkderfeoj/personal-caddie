"""
Course Strategy Module

Hazard analysis and risk assessment:
- Identify hazards in play for a given shot
- Determine safe miss directions
- Generate target area recommendations
- Calculate risk levels
"""

from typing import Dict, List
from models import Hole, Hazard


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


def generate_target_area(hole: Hole, hazard_analysis: Dict, pin_location: str) -> str:
    """
    Generate human-readable target area description.
    
    Args:
        hole: Hole information
        hazard_analysis: Result from analyze_hazards_for_shot
        pin_location: front/center/back
    
    Returns:
        Target area description string
    """
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


def generate_strategy_notes(
    option: Dict,
    hole: Hole,
    strategy: str,
    pin_location: str
) -> str:
    """
    Generate strategic guidance for the shot.
    
    Args:
        option: Club option with hazard analysis
        hole: Hole information
        strategy: Player strategy (aggressive/balanced/conservative)
        pin_location: front/center/back
    
    Returns:
        Strategy notes string
    """
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
