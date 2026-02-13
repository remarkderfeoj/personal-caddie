"""
Data validation tests for Personal Caddie course JSON files.

Validates:
- All course JSON files load correctly
- All courses have valid holes with required fields
- Par values are 3, 4, or 5
- Handicap indices are 1-18 with no duplicates
- Distances are reasonable for par rating
- GPS coordinates are valid where present

Run: pytest tests/test_data_validation.py -v
"""

import sys
import json
import glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

# Valid ranges for hole distances by par
DISTANCE_RANGES = {
    3: (100, 250),   # Par 3: 100-250 yards
    4: (280, 500),   # Par 4: 280-500 yards
    5: (450, 650),   # Par 5: 450-650 yards (some can be longer)
}


def load_all_course_files():
    """Load all course JSON files from examples directory"""
    course_files = glob.glob(str(EXAMPLES_DIR / "*.json"))
    # Filter out non-course files
    course_files = [f for f in course_files if not any(x in f for x in [
        "sample_player", "baseline", "weather", "shot", "caddie"
    ])]
    return course_files


def test_all_courses_load():
    """Test that all course JSON files can be loaded"""
    course_files = load_all_course_files()
    assert len(course_files) > 0, "No course files found"
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                assert isinstance(data, dict), f"{course_file}: Not a JSON object"
        except Exception as e:
            failed.append((course_file, str(e)))
    
    if failed:
        error_msg = "\n".join([f"{f}: {e}" for f, e in failed])
        assert False, f"Failed to load courses:\n{error_msg}"


def test_courses_have_required_fields():
    """Test that all courses have required top-level fields"""
    course_files = load_all_course_files()
    
    required_fields = ["course_id", "course_name", "course_elevation_feet", "holes"]
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                for field in required_fields:
                    if field not in data:
                        failed.append(f"{Path(course_file).name}: Missing {field}")
        except Exception as e:
            failed.append(f"{Path(course_file).name}: {e}")
    
    if failed:
        assert False, f"Course validation errors:\n" + "\n".join(failed)


def test_courses_have_18_holes():
    """Test that all courses have exactly 18 holes"""
    course_files = load_all_course_files()
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                holes = data.get("holes", [])
                if len(holes) != 18:
                    failed.append(f"{Path(course_file).name}: Has {len(holes)} holes, expected 18")
        except Exception as e:
            failed.append(f"{Path(course_file).name}: {e}")
    
    if failed:
        assert False, f"Hole count errors:\n" + "\n".join(failed)


def test_holes_have_required_fields():
    """Test that all holes have required fields"""
    course_files = load_all_course_files()
    
    required_fields = ["hole_id", "hole_number", "par", "handicap_index", "distance_to_pin_yards"]
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                holes = data.get("holes", [])
                
                for hole in holes:
                    hole_num = hole.get("hole_number", "?")
                    for field in required_fields:
                        if field not in hole:
                            failed.append(f"{course_name} Hole {hole_num}: Missing {field}")
        except Exception as e:
            failed.append(f"{Path(course_file).name}: {e}")
    
    if failed:
        assert False, f"Hole field validation errors:\n" + "\n".join(failed)


def test_par_values_are_valid():
    """Test that all par values are 3, 4, or 5"""
    course_files = load_all_course_files()
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                holes = data.get("holes", [])
                
                for hole in holes:
                    hole_num = hole.get("hole_number", "?")
                    par = hole.get("par")
                    if par not in [3, 4, 5]:
                        failed.append(f"{course_name} Hole {hole_num}: Invalid par {par} (must be 3, 4, or 5)")
        except Exception as e:
            failed.append(f"{Path(course_file).name}: {e}")
    
    if failed:
        assert False, f"Par validation errors:\n" + "\n".join(failed)


def test_handicap_indices_valid():
    """Test that handicap indices are 1-18 with no duplicates per course"""
    course_files = load_all_course_files()
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                holes = data.get("holes", [])
                
                handicap_indices = []
                for hole in holes:
                    hole_num = hole.get("hole_number", "?")
                    handicap_idx = hole.get("handicap_index")
                    
                    # Check range
                    if handicap_idx is not None:
                        if not (1 <= handicap_idx <= 18):
                            failed.append(f"{course_name} Hole {hole_num}: Invalid handicap index {handicap_idx} (must be 1-18)")
                        handicap_indices.append(handicap_idx)
                
                # Check for duplicates
                if len(handicap_indices) != len(set(handicap_indices)):
                    duplicates = [idx for idx in handicap_indices if handicap_indices.count(idx) > 1]
                    failed.append(f"{course_name}: Duplicate handicap indices: {set(duplicates)}")
                
                # Check that all 1-18 are present (if course has all handicaps set)
                if None not in [h.get("handicap_index") for h in holes]:
                    if set(handicap_indices) != set(range(1, 19)):
                        missing = set(range(1, 19)) - set(handicap_indices)
                        failed.append(f"{course_name}: Missing handicap indices: {missing}")
        except Exception as e:
            failed.append(f"{Path(course_file).name}: {e}")
    
    if failed:
        assert False, f"Handicap index validation errors:\n" + "\n".join(failed)


def test_distances_are_reasonable():
    """Test that hole distances are reasonable for their par rating"""
    course_files = load_all_course_files()
    
    warnings = []
    errors = []
    
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                holes = data.get("holes", [])
                
                for hole in holes:
                    hole_num = hole.get("hole_number", "?")
                    par = hole.get("par")
                    distance = hole.get("distance_to_pin_yards")
                    
                    if par in DISTANCE_RANGES and distance is not None:
                        min_dist, max_dist = DISTANCE_RANGES[par]
                        
                        # Allow some flexibility - warn if slightly outside, error if way outside
                        if distance < min_dist * 0.8 or distance > max_dist * 1.3:
                            errors.append(f"{course_name} Hole {hole_num}: Distance {distance}y seems wrong for par {par} (expected {min_dist}-{max_dist})")
                        elif distance < min_dist or distance > max_dist:
                            warnings.append(f"{course_name} Hole {hole_num}: Distance {distance}y unusual for par {par} (typical {min_dist}-{max_dist})")
        except Exception as e:
            errors.append(f"{Path(course_file).name}: {e}")
    
    # Print warnings but don't fail
    if warnings:
        print("\n⚠️  Distance warnings:")
        for w in warnings:
            print(f"  {w}")
    
    if errors:
        assert False, f"Distance validation errors:\n" + "\n".join(errors)


def test_gps_coordinates_valid():
    """Test that GPS coordinates are valid where present"""
    course_files = load_all_course_files()
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                
                # Check course-level coordinates
                center_lat = data.get("center_lat")
                center_lng = data.get("center_lng")
                
                if center_lat is not None:
                    if not (-90 <= center_lat <= 90):
                        failed.append(f"{course_name}: Invalid center_lat {center_lat} (must be -90 to 90)")
                
                if center_lng is not None:
                    if not (-180 <= center_lng <= 180):
                        failed.append(f"{course_name}: Invalid center_lng {center_lng} (must be -180 to 180)")
                
                # Check hole-level coordinates
                holes = data.get("holes", [])
                for hole in holes:
                    hole_num = hole.get("hole_number", "?")
                    
                    tee_lat = hole.get("tee_lat")
                    tee_lng = hole.get("tee_lng")
                    green_lat = hole.get("green_lat")
                    green_lng = hole.get("green_lng")
                    
                    if tee_lat is not None and not (-90 <= tee_lat <= 90):
                        failed.append(f"{course_name} Hole {hole_num}: Invalid tee_lat {tee_lat}")
                    
                    if tee_lng is not None and not (-180 <= tee_lng <= 180):
                        failed.append(f"{course_name} Hole {hole_num}: Invalid tee_lng {tee_lng}")
                    
                    if green_lat is not None and not (-90 <= green_lat <= 90):
                        failed.append(f"{course_name} Hole {hole_num}: Invalid green_lat {green_lat}")
                    
                    if green_lng is not None and not (-180 <= green_lng <= 180):
                        failed.append(f"{course_name} Hole {hole_num}: Invalid green_lng {green_lng}")
                    
                    # If hole has coordinates, both tee and green should be present
                    has_tee = tee_lat is not None and tee_lng is not None
                    has_green = green_lat is not None and green_lng is not None
                    
                    if has_tee != has_green:
                        failed.append(f"{course_name} Hole {hole_num}: Incomplete coordinates (need both tee and green)")
        
        except Exception as e:
            failed.append(f"{Path(course_file).name}: {e}")
    
    if failed:
        assert False, f"GPS coordinate validation errors:\n" + "\n".join(failed)


def test_hole_coordinates_near_course_center():
    """Test that hole coordinates are within reasonable distance of course center"""
    course_files = load_all_course_files()
    
    warnings = []
    
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                
                center_lat = data.get("center_lat")
                center_lng = data.get("center_lng")
                
                if center_lat is None or center_lng is None:
                    continue  # Skip courses without center coordinates
                
                holes = data.get("holes", [])
                for hole in holes:
                    hole_num = hole.get("hole_number", "?")
                    
                    tee_lat = hole.get("tee_lat")
                    tee_lng = hole.get("tee_lng")
                    green_lat = hole.get("green_lat")
                    green_lng = hole.get("green_lng")
                    
                    if tee_lat is None or tee_lng is None:
                        continue  # Skip holes without coordinates
                    
                    # Rough distance check (1 degree ≈ 69 miles at equator)
                    # Most golf courses are < 1 mile radius (≈ 0.015 degrees)
                    tee_dist = ((tee_lat - center_lat)**2 + (tee_lng - center_lng)**2)**0.5
                    
                    if tee_dist > 0.05:  # ~3.5 miles - definitely wrong
                        warnings.append(f"{course_name} Hole {hole_num}: Tee is {tee_dist:.3f}° from course center (suspicious)")
                    
                    if green_lat is not None and green_lng is not None:
                        green_dist = ((green_lat - center_lat)**2 + (green_lng - center_lng)**2)**0.5
                        if green_dist > 0.05:
                            warnings.append(f"{course_name} Hole {hole_num}: Green is {green_dist:.3f}° from course center (suspicious)")
        
        except Exception as e:
            warnings.append(f"{Path(course_file).name}: {e}")
    
    # Print warnings but don't fail (some courses might legitimately span large areas)
    if warnings:
        print("\n⚠️  GPS distance warnings:")
        for w in warnings:
            print(f"  {w}")


def test_hole_numbers_sequential():
    """Test that hole numbers are 1-18 and sequential"""
    course_files = load_all_course_files()
    
    failed = []
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                holes = data.get("holes", [])
                
                hole_numbers = [h.get("hole_number") for h in holes]
                
                # Check for None values
                if None in hole_numbers:
                    failed.append(f"{course_name}: Some holes missing hole_number")
                    continue
                
                # Check range
                for num in hole_numbers:
                    if not (1 <= num <= 18):
                        failed.append(f"{course_name}: Invalid hole number {num}")
                
                # Check uniqueness
                if len(set(hole_numbers)) != len(hole_numbers):
                    duplicates = [n for n in hole_numbers if hole_numbers.count(n) > 1]
                    failed.append(f"{course_name}: Duplicate hole numbers: {set(duplicates)}")
                
                # Check completeness
                if set(hole_numbers) != set(range(1, 19)):
                    missing = set(range(1, 19)) - set(hole_numbers)
                    failed.append(f"{course_name}: Missing hole numbers: {missing}")
        
        except Exception as e:
            failed.append(f"{Path(course_file).name}: {e}")
    
    if failed:
        assert False, f"Hole number validation errors:\n" + "\n".join(failed)


def test_course_par_totals():
    """Test that course par totals are reasonable (typically 70-72)"""
    course_files = load_all_course_files()
    
    warnings = []
    
    for course_file in course_files:
        try:
            with open(course_file, 'r') as f:
                data = json.load(f)
                course_name = data.get("course_name", Path(course_file).name)
                holes = data.get("holes", [])
                
                total_par = sum(h.get("par", 0) for h in holes)
                
                # Most courses are 70-72, but some are different
                if total_par < 68 or total_par > 74:
                    warnings.append(f"{course_name}: Total par {total_par} is unusual (typical 70-72)")
        
        except Exception as e:
            warnings.append(f"{Path(course_file).name}: {e}")
    
    if warnings:
        print("\n⚠️  Par total warnings:")
        for w in warnings:
            print(f"  {w}")


def run_all_tests():
    """Run all data validation tests"""
    test_functions = [
        test_all_courses_load,
        test_courses_have_required_fields,
        test_courses_have_18_holes,
        test_holes_have_required_fields,
        test_par_values_are_valid,
        test_handicap_indices_valid,
        test_distances_are_reasonable,
        test_gps_coordinates_valid,
        test_hole_coordinates_near_course_center,
        test_hole_numbers_sequential,
        test_course_par_totals,
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
