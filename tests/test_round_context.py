"""
Unit tests for round context and emotional awareness.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.round_context import (
    calculate_momentum,
    get_round_phase,
    get_strategy_adjustment,
    generate_caddie_note,
)


def test_momentum_hot_streak():
    """Test momentum calculation for hot streak (two birdies)"""
    scores = [3, 3, 4]
    pars = [4, 4, 4]
    momentum = calculate_momentum(scores, pars)
    assert momentum == "hot", "Two birdies should be hot momentum"


def test_momentum_cold_streak():
    """Test momentum calculation for cold streak (blowup hole)"""
    scores = [6, 4, 5]
    pars = [4, 4, 4]
    momentum = calculate_momentum(scores, pars)
    assert momentum == "cold", "Double bogey or worse should be cold momentum"


def test_momentum_steady():
    """Test momentum calculation for steady play"""
    scores = [4, 5, 4]
    pars = [4, 4, 4]
    momentum = calculate_momentum(scores, pars)
    assert momentum == "steady", "Pars and bogeys should be steady"


def test_round_phase_early():
    """Test round phase for early holes"""
    assert get_round_phase(1) == "early"
    assert get_round_phase(6) == "early"


def test_round_phase_middle():
    """Test round phase for middle holes"""
    assert get_round_phase(7) == "middle"
    assert get_round_phase(12) == "middle"


def test_round_phase_closing():
    """Test round phase for closing holes"""
    assert get_round_phase(13) == "closing"
    assert get_round_phase(18) == "closing"


def test_strategy_adjustment_after_blowup():
    """Test strategy adjustment after cold streak"""
    adjustment, magnitude = get_strategy_adjustment("cold", "early", 0, "average")
    assert adjustment == "conservative", "Should recommend conservative after cold streak"
    assert magnitude > 0.5, "Should have strong conservative bias"


def test_strategy_adjustment_hot_early():
    """Test strategy adjustment when hot early in round"""
    adjustment, magnitude = get_strategy_adjustment("hot", "early", 0, "average")
    assert adjustment == "aggressive", "Should stay aggressive when hot early"


def test_strategy_adjustment_protecting_score():
    """Test strategy adjustment when protecting good score on closing holes"""
    adjustment, magnitude = get_strategy_adjustment("steady", "closing", -2, "average")
    assert adjustment == "conservative", "Should protect good score on closing holes"


def test_caddie_note_after_blowup():
    """Test caddie note after a blowup hole"""
    note = generate_caddie_note(
        momentum="cold",
        round_phase="middle",
        score_to_par=3,
        last_hole_score=7,
        last_hole_par=4,
        hole_par=4
    )
    assert "shake" in note.lower() or "find the fairway" in note.lower(), \
        "Should have calming message after blowup"


def test_caddie_note_birdie_streak():
    """Test caddie note during hot streak"""
    note = generate_caddie_note(
        momentum="hot",
        round_phase="middle",
        score_to_par=-2,
        last_hole_score=3,
        last_hole_par=4,
        hole_par=3,
        hole_difficulty="easy"
    )
    assert "aggressive" in note.lower() or "birdie" in note.lower(), \
        "Should encourage aggression when hot"


def test_caddie_note_standard_par_3():
    """Test caddie note for standard par 3"""
    note = generate_caddie_note(
        momentum="steady",
        round_phase="middle",
        score_to_par=0,
        last_hole_score=4,
        last_hole_par=4,
        hole_par=3
    )
    assert "trust" in note.lower() or "distance" in note.lower(), \
        "Should focus on distance for par 3"


def run_all_tests():
    """Run all round context tests"""
    test_functions = [
        test_momentum_hot_streak,
        test_momentum_cold_streak,
        test_momentum_steady,
        test_round_phase_early,
        test_round_phase_middle,
        test_round_phase_closing,
        test_strategy_adjustment_after_blowup,
        test_strategy_adjustment_hot_early,
        test_strategy_adjustment_protecting_score,
        test_caddie_note_after_blowup,
        test_caddie_note_birdie_streak,
        test_caddie_note_standard_par_3,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test_func.__name__}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
