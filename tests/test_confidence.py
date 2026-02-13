"""
Unit tests for confidence scoring in recommendation engine.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.recommendation import calculate_confidence_score


def test_confidence_perfect_conditions():
    """Test confidence score with perfect conditions"""
    confidence, explanation = calculate_confidence_score(
        match_score=95.0,
        distance_to_target=150,
        adjusted_distance=150,
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=0,
        player_lie="tee",
        lie_quality="clean",
        is_real_player_data=True
    )
    
    assert confidence.distance_certainty == 1.0, "Perfect distance match should be 1.0"
    assert confidence.elevation_certainty == 1.0, "Flat shot should be 1.0"
    assert confidence.wind_certainty == 1.0, "Calm should be 1.0"
    assert confidence.lie_certainty == 1.0, "Tee should be 1.0"
    assert confidence.player_data_quality == 0.95, "Real data should be 0.95"
    assert confidence.overall_confidence >= 0.95, "Overall should be high"
    assert "great" in explanation.lower() or "high confidence" in explanation.lower()


def test_confidence_marginal_distance():
    """Test confidence score with marginal distance match"""
    confidence, explanation = calculate_confidence_score(
        match_score=70.0,
        distance_to_target=150,
        adjusted_distance=165,  # 15 yards off
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=0,
        player_lie="fairway",
        lie_quality="normal",
        is_real_player_data=True
    )
    
    assert confidence.distance_certainty < 0.85, "Distance off by 1.5x dispersion should be lower"
    assert "marginal" in explanation.lower()


def test_confidence_uphill_shot():
    """Test confidence score with significant elevation change"""
    confidence, explanation = calculate_confidence_score(
        match_score=90.0,
        distance_to_target=150,
        adjusted_distance=155,
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=30,  # Significant uphill
        has_wind_data=True,
        wind_speed=5,
        player_lie="fairway",
        lie_quality="normal",
        is_real_player_data=True
    )
    
    assert confidence.elevation_certainty == 0.95, "Significant elevation should be 0.95"
    assert confidence.overall_confidence >= 0.85, "Should still be high confidence"


def test_confidence_no_elevation_data():
    """Test confidence score without elevation data"""
    confidence, explanation = calculate_confidence_score(
        match_score=90.0,
        distance_to_target=150,
        adjusted_distance=150,
        dispersion=10,
        has_elevation_data=False,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=0,
        player_lie="fairway",
        lie_quality="normal",
        is_real_player_data=True
    )
    
    assert confidence.elevation_certainty == 0.7, "No elevation data should be 0.7"
    assert "elevation estimated" in explanation.lower()


def test_confidence_windy_conditions():
    """Test confidence score with strong wind"""
    confidence, explanation = calculate_confidence_score(
        match_score=85.0,
        distance_to_target=150,
        adjusted_distance=150,
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=20,  # Strong wind
        player_lie="fairway",
        lie_quality="normal",
        is_real_player_data=True
    )
    
    assert confidence.wind_certainty == 0.8, "Strong wind should be 0.8"
    assert "wind variable" in explanation.lower()


def test_confidence_rough_lie():
    """Test confidence score from rough"""
    confidence, explanation = calculate_confidence_score(
        match_score=80.0,
        distance_to_target=150,
        adjusted_distance=150,
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=0,
        player_lie="rough",
        lie_quality="thick",
        is_real_player_data=True
    )
    
    assert confidence.lie_certainty == 0.6, "Thick rough should be 0.6"
    assert "challenging lie" in explanation.lower()


def test_confidence_bunker_lie():
    """Test confidence score from bunker"""
    confidence, explanation = calculate_confidence_score(
        match_score=75.0,
        distance_to_target=150,
        adjusted_distance=150,
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=0,
        player_lie="bunker",
        lie_quality=None,
        is_real_player_data=True
    )
    
    assert confidence.lie_certainty == 0.65, "Bunker should be 0.65"


def test_confidence_default_player_data():
    """Test confidence score with default player data"""
    confidence, explanation = calculate_confidence_score(
        match_score=90.0,
        distance_to_target=150,
        adjusted_distance=150,
        dispersion=10,
        has_elevation_data=True,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=0,
        player_lie="fairway",
        lie_quality="normal",
        is_real_player_data=False
    )
    
    assert confidence.player_data_quality == 0.7, "Default data should be 0.7"
    assert "default distances" in explanation.lower()


def test_confidence_multiple_issues():
    """Test confidence score with multiple uncertainty factors"""
    confidence, explanation = calculate_confidence_score(
        match_score=70.0,
        distance_to_target=150,
        adjusted_distance=165,
        dispersion=10,
        has_elevation_data=False,
        elevation_change_feet=0,
        has_wind_data=True,
        wind_speed=15,
        player_lie="rough",
        lie_quality="normal",
        is_real_player_data=False
    )
    
    assert confidence.overall_confidence < 0.7, "Multiple issues should lower confidence"
    # Should mention multiple factors
    assert explanation.count(",") >= 2, "Should list multiple issues"


def run_all_tests():
    """Run all confidence tests"""
    test_functions = [
        test_confidence_perfect_conditions,
        test_confidence_marginal_distance,
        test_confidence_uphill_shot,
        test_confidence_no_elevation_data,
        test_confidence_windy_conditions,
        test_confidence_rough_lie,
        test_confidence_bunker_lie,
        test_confidence_default_player_data,
        test_confidence_multiple_issues,
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
