"""
Unit tests for physics calculations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.physics import (
    calculate_temperature_adjustment,
    calculate_elevation_adjustment,
    calculate_shot_elevation_adjustment,
    calculate_wind_adjustment,
    calculate_rain_adjustment,
    calculate_lie_adjustment,
    compass_to_degrees,
    calculate_wind_relative_to_shot,
)


def test_temperature_adjustment_baseline():
    """Test temperature adjustment at 70°F (no adjustment)"""
    result = calculate_temperature_adjustment(70.0, 150)
    assert result == 0, "70°F should have no adjustment"


def test_temperature_adjustment_hot():
    """Test temperature adjustment on hot day"""
    result = calculate_temperature_adjustment(90.0, 150)
    assert result == 4, "90°F should add 4 yards (20° above baseline)"


def test_temperature_adjustment_cold():
    """Test temperature adjustment on cold day"""
    result = calculate_temperature_adjustment(50.0, 150)
    assert result == -4, "50°F should subtract 4 yards (20° below baseline)"


def test_elevation_adjustment_sea_level():
    """Test elevation adjustment at sea level"""
    result = calculate_elevation_adjustment(0, 150)
    assert result == 0, "Sea level should have no adjustment"


def test_elevation_adjustment_high_altitude():
    """Test elevation adjustment at 5000 feet"""
    result = calculate_elevation_adjustment(5000, 150)
    # 5000 * 0.00002 = 0.1 = 10% increase = 15 yards
    assert result == 15, "5000 feet should add 15 yards"


def test_shot_elevation_adjustment_flat():
    """Test shot elevation adjustment on flat ground"""
    result = calculate_shot_elevation_adjustment(0, 150)
    assert result == 0, "Flat shot should have no adjustment"


def test_shot_elevation_adjustment_uphill():
    """Test shot elevation adjustment uphill"""
    # 30 feet uphill at 150 yards
    result = calculate_shot_elevation_adjustment(30, 150)
    # Base: 30 / 3 = 10 yards, scaling 0.8 for 150y = 8 yards
    assert result == 8, "30 feet uphill at 150y should add 8 yards"


def test_shot_elevation_adjustment_downhill():
    """Test shot elevation adjustment downhill"""
    # 30 feet downhill at 150 yards
    result = calculate_shot_elevation_adjustment(-30, 150)
    # Base: -30 / 3 = -10 yards, scaling 0.8 for 150y = -8 yards
    assert result == -8, "30 feet downhill at 150y should subtract 8 yards"


def test_shot_elevation_adjustment_long_shot():
    """Test shot elevation adjustment for long shot"""
    # 30 feet uphill at 220 yards (long shot, 100% scaling)
    result = calculate_shot_elevation_adjustment(30, 220)
    # Base: 30 / 3 = 10 yards, scaling 1.0 for 220y = 10 yards
    assert result == 10, "30 feet uphill at 220y should add 10 yards"


def test_shot_elevation_adjustment_short_shot():
    """Test shot elevation adjustment for short shot"""
    # 30 feet uphill at 100 yards (short shot, 60% scaling)
    result = calculate_shot_elevation_adjustment(30, 100)
    # Base: 30 / 3 = 10 yards, scaling 0.6 for 100y = 6 yards
    assert result == 6, "30 feet uphill at 100y should add 6 yards"


def test_shot_elevation_adjustment_clamped():
    """Test shot elevation adjustment is clamped to ±15%"""
    # Extreme uphill: 150 feet at 150 yards
    result = calculate_shot_elevation_adjustment(150, 150)
    # Base: 150 / 3 = 50 yards, but clamped to 15% = 22.5 yards, rounds to 23
    max_adjustment = int(150 * 0.15)
    assert result == max_adjustment, f"Extreme uphill should be clamped to {max_adjustment} yards"


def test_wind_adjustment_calm():
    """Test wind adjustment in calm conditions"""
    result = calculate_wind_adjustment("calm", 0, 150)
    assert result == 0, "Calm wind should have no adjustment"


def test_wind_adjustment_headwind():
    """Test wind adjustment with headwind"""
    result = calculate_wind_adjustment("headwind", 15, 150)
    # 15 mph = strength_factor 1.0, -4% = -6 yards
    assert result == -6, "15mph headwind should subtract 6 yards"


def test_wind_adjustment_tailwind():
    """Test wind adjustment with tailwind"""
    result = calculate_wind_adjustment("tailwind", 15, 150)
    # 15 mph = strength_factor 1.0, +4% = +6 yards
    assert result == 6, "15mph tailwind should add 6 yards"


def test_rain_adjustment_dry():
    """Test rain adjustment in dry conditions"""
    result = calculate_rain_adjustment(False, False)
    assert result == 0.0, "Dry conditions should have no adjustment"


def test_rain_adjustment_raining():
    """Test rain adjustment when raining"""
    result = calculate_rain_adjustment(True, False)
    assert result == 0.05, "Rain should give 5% reduction"


def test_rain_adjustment_wet_ground():
    """Test rain adjustment with wet ground"""
    result = calculate_rain_adjustment(False, True)
    assert result == 0.03, "Wet ground should give 3% reduction"


def test_lie_adjustment_tee():
    """Test lie adjustment from tee"""
    result = calculate_lie_adjustment("tee", "clean")
    assert result == 0.0, "Tee should have no penalty"


def test_lie_adjustment_rough():
    """Test lie adjustment from rough"""
    result = calculate_lie_adjustment("rough", "normal")
    assert result == 0.15, "Rough should have 15% penalty"


def test_lie_adjustment_thick_rough():
    """Test lie adjustment from thick rough"""
    result = calculate_lie_adjustment("rough", "thick")
    assert result == 0.25, "Thick rough should have 25% penalty"


def test_lie_adjustment_bunker():
    """Test lie adjustment from bunker"""
    result = calculate_lie_adjustment("bunker", None)
    assert result == 0.20, "Bunker should have 20% penalty"


def test_lie_adjustment_semi_rough():
    """Test lie adjustment from semi rough"""
    result = calculate_lie_adjustment("semi_rough", None)
    assert result == 0.05, "Semi rough should have 5% penalty"


def test_compass_to_degrees():
    """Test compass direction conversion"""
    assert compass_to_degrees("N") == 0
    assert compass_to_degrees("E") == 90
    assert compass_to_degrees("S") == 180
    assert compass_to_degrees("W") == 270
    assert compass_to_degrees("NE") == 45


def test_wind_relative_to_shot_headwind():
    """Test wind relative calculation for headwind"""
    wind_type, _ = calculate_wind_relative_to_shot("N", 0, 15)
    assert wind_type == "headwind", "North wind on north shot should be headwind"


def test_wind_relative_to_shot_tailwind():
    """Test wind relative calculation for tailwind"""
    wind_type, _ = calculate_wind_relative_to_shot("S", 0, 15)
    assert wind_type == "tailwind", "South wind on north shot should be tailwind"


def test_wind_relative_to_shot_crosswind():
    """Test wind relative calculation for crosswind"""
    wind_type, _ = calculate_wind_relative_to_shot("E", 0, 15)
    assert wind_type == "crosswind_left", "East wind on north shot should be crosswind left"


def run_all_tests():
    """Run all physics tests"""
    test_functions = [
        test_temperature_adjustment_baseline,
        test_temperature_adjustment_hot,
        test_temperature_adjustment_cold,
        test_elevation_adjustment_sea_level,
        test_elevation_adjustment_high_altitude,
        test_shot_elevation_adjustment_flat,
        test_shot_elevation_adjustment_uphill,
        test_shot_elevation_adjustment_downhill,
        test_shot_elevation_adjustment_long_shot,
        test_shot_elevation_adjustment_short_shot,
        test_shot_elevation_adjustment_clamped,
        test_wind_adjustment_calm,
        test_wind_adjustment_headwind,
        test_wind_adjustment_tailwind,
        test_rain_adjustment_dry,
        test_rain_adjustment_raining,
        test_rain_adjustment_wet_ground,
        test_lie_adjustment_tee,
        test_lie_adjustment_rough,
        test_lie_adjustment_thick_rough,
        test_lie_adjustment_bunker,
        test_lie_adjustment_semi_rough,
        test_compass_to_degrees,
        test_wind_relative_to_shot_headwind,
        test_wind_relative_to_shot_tailwind,
        test_wind_relative_to_shot_crosswind,
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
