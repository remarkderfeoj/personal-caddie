"""
Round Context Module

Situational and emotional awareness for shot recommendations.
Adjusts strategy based on how the round is progressing.

Philosophy: A great caddie reads the player's momentum and adjusts
their advice accordingly - conservative after a blowup hole,
steady during a good run, measured on closing holes.
"""

from typing import Literal, List, Tuple


def calculate_momentum(
    last_3_scores: List[int],
    last_3_pars: List[int]
) -> Literal["hot", "steady", "cold"]:
    """
    Determine player momentum from recent holes.
    
    Args:
        last_3_scores: Scores on last 3 holes
        last_3_pars: Pars for last 3 holes
    
    Returns:
        "hot" (playing well), "steady" (normal), or "cold" (struggling)
    """
    if len(last_3_scores) < 3 or len(last_3_pars) < 3:
        return "steady"
    
    # Calculate scores relative to par
    relative_scores = [score - par for score, par in zip(last_3_scores, last_3_pars)]
    average_to_par = sum(relative_scores) / len(relative_scores)
    
    # Check for recent blowups (double bogey or worse)
    has_blowup = any(score >= (par + 2) for score, par in zip(last_3_scores, last_3_pars))
    
    # Check for birdies
    birdie_count = sum(1 for score, par in zip(last_3_scores, last_3_pars) if score < par)
    
    if has_blowup:
        return "cold"
    elif birdie_count >= 2:
        return "hot"
    elif average_to_par <= -0.5:
        return "hot"
    elif average_to_par >= 1.0:
        return "cold"
    else:
        return "steady"


def get_round_phase(hole_number: int) -> Literal["early", "middle", "closing"]:
    """
    Determine phase of round.
    
    Args:
        hole_number: Current hole (1-18)
    
    Returns:
        "early" (1-6), "middle" (7-12), or "closing" (13-18)
    """
    if hole_number <= 6:
        return "early"
    elif hole_number <= 12:
        return "middle"
    else:
        return "closing"


def get_strategy_adjustment(
    momentum: Literal["hot", "steady", "cold"],
    round_phase: Literal["early", "middle", "closing"],
    score_to_par: int,
    hole_difficulty: str = "average"
) -> Tuple[str, float]:
    """
    Get strategy adjustment based on round context.
    
    Args:
        momentum: hot/steady/cold
        round_phase: early/middle/closing
        score_to_par: Current round score relative to par
        hole_difficulty: easy/average/hard
    
    Returns:
        Tuple of (adjustment_type, magnitude)
        - adjustment_type: "conservative", "standard", "aggressive"
        - magnitude: 0.0-1.0 (strength of adjustment)
    """
    # After struggling, play conservative
    if momentum == "cold":
        return ("conservative", 0.8)
    
    # On a hot streak, maintain approach
    if momentum == "hot":
        if round_phase == "closing":
            # Don't change what's working
            return ("standard", 0.5)
        else:
            # Stay aggressive early/middle when hot
            return ("aggressive", 0.6)
    
    # Closing holes with a good score - protect it
    if round_phase == "closing" and score_to_par <= 0:
        return ("conservative", 0.7)
    
    # Closing holes while behind - calculated aggression
    if round_phase == "closing" and score_to_par > 3:
        if hole_difficulty == "easy":
            return ("aggressive", 0.8)
        else:
            return ("standard", 0.5)
    
    # Default: standard approach
    return ("standard", 0.5)


def generate_caddie_note(
    momentum: Literal["hot", "steady", "cold"],
    round_phase: Literal["early", "middle", "closing"],
    score_to_par: int,
    last_hole_score: int,
    last_hole_par: int,
    hole_par: int,
    hole_difficulty: str = "average"
) -> str:
    """
    Generate contextual caddie note based on round situation.
    
    Uses deterministic template logic, NOT an LLM.
    
    Args:
        momentum: hot/steady/cold
        round_phase: early/middle/closing
        score_to_par: Current round score relative to par
        last_hole_score: Score on previous hole
        last_hole_par: Par of previous hole
        hole_par: Par of current hole
        hole_difficulty: easy/average/hard
    
    Returns:
        Natural language caddie note
    """
    # After a blowup hole
    if last_hole_score >= (last_hole_par + 2):
        return "Let's just find the fairway here and give ourselves a look. Shake off that last one."
    
    # On a birdie streak
    if momentum == "hot":
        if hole_difficulty == "easy":
            if hole_par == 3:
                return "Good number here. This is a birdie hole for you — let's be aggressive to the pin."
            else:
                return "You're swinging well. Trust your line and be aggressive."
        else:
            return "Stay patient. You're playing great golf."
    
    # Closing holes with good round going
    if round_phase == "closing" and score_to_par <= 0:
        if hole_difficulty == "easy":
            return "Smart play here. Let's take what the hole gives us."
        else:
            return "Conservative is smart. Protect your score."
    
    # Closing holes while chasing
    if round_phase == "closing" and score_to_par > 3:
        if hole_difficulty == "easy":
            return "We need this one. Birdie opportunity — let's attack it."
        else:
            return "Stay aggressive but smart. Par is fine here."
    
    # Early round, after a bogey
    if round_phase == "early" and last_hole_score == (last_hole_par + 1):
        return "Plenty of golf left. Let's get that shot back."
    
    # Standard situations by par
    if hole_par == 3:
        return "Good par 3. Trust your distance."
    elif hole_par == 5:
        return "Scoring hole. Let's make birdie."
    else:
        return "Fairway first, then we'll go at the pin."


def should_modify_aggression(
    momentum: Literal["hot", "steady", "cold"],
    strategy_adjustment: str
) -> bool:
    """
    Determine if we should modify the player's stated strategy preference.
    
    Args:
        momentum: hot/steady/cold
        strategy_adjustment: Recommended adjustment
    
    Returns:
        True if we should override player's preference
    """
    # Override to conservative after cold streak
    if momentum == "cold" and strategy_adjustment == "conservative":
        return True
    
    # Otherwise respect player's stated preference
    return False
