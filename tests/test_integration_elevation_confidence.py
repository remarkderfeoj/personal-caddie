"""
Integration test for elevation adjustment and confidence scoring.

This test demonstrates that:
1. Uphill/downhill elevation adjustment flows through the system
2. Confidence scoring is calculated and returned
3. All components work together end-to-end
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.physics import (
    calculate_shot_elevation_adjustment,
    calculate_adjusted_distance
)
from services.recommendation import calculate_confidence_score


def test_elevation_integration():
    """
    Test that elevation adjustments work end-to-end.
    
    Scenario: 150-yard shot, 30 feet uphill
    Expected: ~8 yards added (30/3 * 0.8 scaling)
    """
    print("\n=== ELEVATION ADJUSTMENT INTEGRATION TEST ===")
    
    baseline_distance = 150
    elevation_change = 30  # 30 feet uphill
    
    # Calculate shot elevation adjustment
    shot_elevation_adj = calculate_shot_elevation_adjustment(elevation_change, baseline_distance)
    print(f"Baseline distance: {baseline_distance} yards")
    print(f"Elevation change: {elevation_change} feet uphill")
    print(f"Shot elevation adjustment: {shot_elevation_adj:+d} yards")
    assert shot_elevation_adj == 8, f"Expected 8 yards, got {shot_elevation_adj}"
    
    # Calculate full adjusted distance
    adjusted = calculate_adjusted_distance(
        baseline_carry=145,
        baseline_total=150,
        temperature=70.0,
        elevation_feet=0,  # Sea level
        elevation_change_feet=elevation_change,
        wind_relative="calm",
        wind_speed=0.0,
        rain=False,
        ground_conditions="dry",
        player_lie="fairway",
        lie_quality="normal"
    )
    
    print(f"Adjusted carry: {adjusted['adjusted_carry']} yards")
    print(f"Adjusted total: {adjusted['adjusted_total']} yards")
    print(f"Course elevation adj: {adjusted['adjustments']['course_elevation_yards']} yards")
    print(f"Shot elevation adj: {adjusted['adjustments']['shot_elevation_yards']} yards")
    
    assert adjusted['adjustments']['shot_elevation_yards'] == 8
    assert adjusted['adjusted_total'] == 158  # 150 + 8
    
    print("✅ Elevation adjustment working correctly!\n")
    return True


def test_confidence_integration():
    """
    Test that confidence scoring works with elevation data.
    
    Scenario: Good distance match, uphill shot with data, calm conditions
    Expected: High overall confidence
    """
    print("=== CONFIDENCE SCORING INTEGRATION TEST ===")
    
    confidence, explanation = calculate_confidence_score(
        match_score=92.0,
        distance_to_target=150,
        adjusted_distance=158,  # After uphill adjustment
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=30,  # Significant uphill
        has_wind_data=True,
        wind_speed=5,
        player_lie="fairway",
        lie_quality="normal",
        is_real_player_data=True
    )
    
    print(f"Match score: 92.0")
    print(f"Confidence factors:")
    print(f"  - Distance certainty: {confidence.distance_certainty}")
    print(f"  - Elevation certainty: {confidence.elevation_certainty}")
    print(f"  - Wind certainty: {confidence.wind_certainty}")
    print(f"  - Lie certainty: {confidence.lie_certainty}")
    print(f"  - Player data quality: {confidence.player_data_quality}")
    print(f"Overall confidence: {confidence.overall_confidence:.2f} ({int(confidence.overall_confidence * 100)}%)")
    print(f"Explanation: {explanation}")
    
    assert confidence.overall_confidence >= 0.85, f"Expected high confidence, got {confidence.overall_confidence}"
    assert confidence.elevation_certainty == 0.95, "Significant elevation should be 0.95"
    
    print("✅ Confidence scoring working correctly!\n")
    return True


def test_downhill_clamping():
    """
    Test that extreme downhill shots are clamped to ±15%.
    
    Scenario: 150-yard shot, 90 feet downhill (extreme)
    Expected: Clamped to -23 yards (15% of 150)
    """
    print("=== DOWNHILL CLAMPING TEST ===")
    
    baseline_distance = 150
    elevation_change = -90  # 90 feet downhill (extreme)
    
    shot_elevation_adj = calculate_shot_elevation_adjustment(elevation_change, baseline_distance)
    print(f"Baseline distance: {baseline_distance} yards")
    print(f"Elevation change: {elevation_change} feet downhill")
    print(f"Shot elevation adjustment: {shot_elevation_adj:+d} yards")
    
    max_adjustment = int(baseline_distance * 0.15)
    print(f"Maximum allowed adjustment: ±{max_adjustment} yards")
    
    assert shot_elevation_adj == -max_adjustment, f"Expected -{max_adjustment}, got {shot_elevation_adj}"
    print("✅ Clamping working correctly!\n")
    return True


def test_confidence_with_uncertainty():
    """
    Test confidence scoring with multiple uncertainty factors.
    
    Scenario: Rough lie, no elevation data, strong wind, default player data
    Expected: Lower confidence with detailed explanation
    """
    print("=== CONFIDENCE WITH UNCERTAINTY TEST ===")
    
    confidence, explanation = calculate_confidence_score(
        match_score=75.0,
        distance_to_target=150,
        adjusted_distance=160,
        dispersion=15,
        has_elevation_data=False,  # No elevation data
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=18,  # Strong wind
        player_lie="rough",  # Rough lie
        lie_quality="thick",
        is_real_player_data=False  # Default player data
    )
    
    print(f"Confidence factors:")
    print(f"  - Distance certainty: {confidence.distance_certainty}")
    print(f"  - Elevation certainty: {confidence.elevation_certainty}")
    print(f"  - Wind certainty: {confidence.wind_certainty}")
    print(f"  - Lie certainty: {confidence.lie_certainty}")
    print(f"  - Player data quality: {confidence.player_data_quality}")
    print(f"Overall confidence: {confidence.overall_confidence:.2f} ({int(confidence.overall_confidence * 100)}%)")
    print(f"Explanation: {explanation}")
    
    assert confidence.overall_confidence < 0.7, f"Expected low confidence, got {confidence.overall_confidence}"
    assert confidence.elevation_certainty == 0.7, "No elevation data should be 0.7"
    assert confidence.lie_certainty == 0.6, "Thick rough should be 0.6"
    assert confidence.player_data_quality == 0.7, "Default data should be 0.7"
    
    print("✅ Uncertainty handling working correctly!\n")
    return True


def run_all_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS: ELEVATION + CONFIDENCE")
    print("="*60)
    
    tests = [
        test_elevation_integration,
        test_confidence_integration,
        test_downhill_clamping,
        test_confidence_with_uncertainty,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__}: {e}\n")
            failed += 1
        except Exception as e:
            print(f"💥 {test_func.__name__}: {type(e).__name__}: {e}\n")
            failed += 1
    
    print("="*60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("="*60)
    return failed == 0


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)
