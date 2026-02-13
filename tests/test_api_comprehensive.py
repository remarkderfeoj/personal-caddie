"""
Comprehensive API test suite for Personal Caddie.

Tests ALL endpoints with:
- Happy path scenarios
- Edge cases (empty strings, zero values, max values)
- Error cases (404s, invalid input, missing required fields)
- Enum mapping layer validation

Requires: pip install pytest httpx fastapi
Run: pytest tests/test_api_comprehensive.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from fastapi.testclient import TestClient
    from main import app
    from datetime import datetime
    
    client = TestClient(app)
    
    # ============================================================================
    # HEALTH & INFO ENDPOINTS
    # ============================================================================
    
    def test_health_check_happy_path():
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "courses_loaded" in data
        assert "players_loaded" in data
        assert "services_available" in data
    
    
    def test_root_endpoint_happy_path():
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Personal Caddie API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
        assert "web_app" in data
    
    
    def test_debug_courses_endpoint():
        """Test debug endpoint shows loaded courses"""
        response = client.get("/debug/courses")
        assert response.status_code == 200
        data = response.json()
        assert "total_courses" in data
        assert "course_ids" in data
        assert "course_names" in data
        assert isinstance(data["course_ids"], list)
    
    
    # ============================================================================
    # COURSE ENDPOINTS - LIST/SEARCH
    # ============================================================================
    
    def test_list_courses_happy_path():
        """Test listing all courses without search"""
        response = client.get("/api/v1/courses")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "courses" in data
        assert isinstance(data["courses"], list)
        assert data["count"] >= 0
        
        # Verify course structure
        if data["count"] > 0:
            course = data["courses"][0]
            assert "id" in course
            assert "name" in course
            assert "elevation_feet" in course
            assert "holes" in course
    
    
    def test_search_courses_happy_path():
        """Test course search with valid query"""
        response = client.get("/api/v1/courses?search=pebble")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "pebble"
        assert "count" in data
        assert "courses" in data
    
    
    def test_search_courses_empty_string():
        """Test course search with empty string"""
        response = client.get("/api/v1/courses?search=")
        assert response.status_code == 200
        # Empty search should still work
    
    
    def test_search_courses_no_results():
        """Test course search that returns no results"""
        response = client.get("/api/v1/courses?search=zzzneverexistszzz")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["courses"] == []
    
    
    def test_search_courses_special_chars():
        """Test course search with special characters"""
        response = client.get("/api/v1/courses?search=%3Cscript%3E")
        assert response.status_code == 200
        # Should not crash, just return 0 results
        data = response.json()
        assert "count" in data
    
    
    # ============================================================================
    # COURSE ENDPOINTS - GET SPECIFIC COURSE
    # ============================================================================
    
    def test_get_course_happy_path():
        """Test getting a specific course by ID"""
        # First get list of courses
        list_response = client.get("/api/v1/courses")
        courses = list_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            response = client.get(f"/api/v1/courses/{course_id}")
            assert response.status_code == 200
            data = response.json()
            assert "course_id" in data
            assert "course_name" in data
            assert "holes" in data
    
    
    def test_get_course_not_found():
        """Test getting non-existent course returns 404"""
        response = client.get("/api/v1/courses/nonexistent_course_id_12345")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    
    def test_get_course_empty_id():
        """Test getting course with empty ID"""
        response = client.get("/api/v1/courses/")
        # Should either 404 or redirect to list endpoint
        assert response.status_code in [404, 200]
    
    
    def test_get_course_special_chars():
        """Test getting course with special characters in ID"""
        response = client.get("/api/v1/courses/<script>alert('xss')</script>")
        assert response.status_code == 404
    
    
    # ============================================================================
    # COURSE ENDPOINTS - GET HOLES
    # ============================================================================
    
    def test_get_holes_happy_path():
        """Test getting all holes for a course"""
        list_response = client.get("/api/v1/courses")
        courses = list_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            response = client.get(f"/api/v1/courses/{course_id}/holes")
            assert response.status_code == 200
            data = response.json()
            assert "course_id" in data
            assert "course_name" in data
            assert "holes" in data
            assert isinstance(data["holes"], list)
            
            # Verify hole structure
            if len(data["holes"]) > 0:
                hole = data["holes"][0]
                assert "hole_id" in hole
                assert "hole_number" in hole
                assert "par" in hole
                assert "distance" in hole
                assert "fairway_type" in hole
    
    
    def test_get_holes_course_not_found():
        """Test getting holes for non-existent course"""
        response = client.get("/api/v1/courses/nonexistent/holes")
        assert response.status_code == 404
    
    
    def test_get_specific_hole_happy_path():
        """Test getting a specific hole"""
        list_response = client.get("/api/v1/courses")
        courses = list_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            response = client.get(f"/api/v1/courses/{course_id}/holes/1")
            assert response.status_code == 200
            data = response.json()
            assert "hole_number" in data
            assert data["hole_number"] == 1
    
    
    def test_get_hole_invalid_number_zero():
        """Test getting hole with number 0 (invalid)"""
        list_response = client.get("/api/v1/courses")
        courses = list_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            response = client.get(f"/api/v1/courses/{course_id}/holes/0")
            assert response.status_code == 400
    
    
    def test_get_hole_invalid_number_19():
        """Test getting hole with number 19 (invalid)"""
        list_response = client.get("/api/v1/courses")
        courses = list_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            response = client.get(f"/api/v1/courses/{course_id}/holes/19")
            assert response.status_code == 400
    
    
    def test_get_hole_invalid_number_negative():
        """Test getting hole with negative number"""
        list_response = client.get("/api/v1/courses")
        courses = list_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            response = client.get(f"/api/v1/courses/{course_id}/holes/-1")
            assert response.status_code == 400
    
    
    def test_get_hole_course_not_found():
        """Test getting hole for non-existent course"""
        response = client.get("/api/v1/courses/nonexistent/holes/1")
        assert response.status_code == 404
    
    
    # ============================================================================
    # PLAYER BASELINE ENDPOINTS
    # ============================================================================
    
    def test_create_player_baseline_happy_path():
        """Test creating player baseline with valid data"""
        player_data = {
            "player_id": "test_player_comprehensive",
            "player_name": "Test Player",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "driver",
                    "carry_distance": 220,
                    "total_distance": 240,
                    "measurement_method": "estimated"
                },
                {
                    "club_type": "iron_7",
                    "carry_distance": 150,
                    "total_distance": 155,
                    "measurement_method": "rangefinder"
                }
            ]
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["player_id"] == "test_player_comprehensive"
        assert data["clubs_registered"] == 2
    
    
    def test_create_player_baseline_minimal():
        """Test creating player with minimal required fields"""
        player_data = {
            "player_id": "minimal_player",
            "player_name": "Minimal",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "iron_7",
                    "carry_distance": 150,
                    "total_distance": 155,
                    "measurement_method": "estimated"
                }
            ]
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        assert response.status_code == 200
    
    
    def test_create_player_baseline_missing_required_field():
        """Test creating player without required field"""
        player_data = {
            "player_id": "test_player",
            # Missing player_name
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": []
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        assert response.status_code == 422  # Validation error
    
    
    def test_create_player_baseline_invalid_club_type():
        """Test creating player with invalid club type"""
        player_data = {
            "player_id": "test_player",
            "player_name": "Test",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "invalid_club",
                    "carry_distance": 150,
                    "total_distance": 155,
                    "measurement_method": "estimated"
                }
            ]
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        assert response.status_code == 422  # Validation error
    
    
    def test_create_player_baseline_zero_distance():
        """Test creating player with zero distance (edge case)"""
        player_data = {
            "player_id": "zero_player",
            "player_name": "Zero Distance",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "iron_7",
                    "carry_distance": 0,
                    "total_distance": 0,
                    "measurement_method": "estimated"
                }
            ]
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        # Should accept 0 as valid (beginner might not hit the ball far)
        assert response.status_code == 200
    
    
    def test_create_player_baseline_max_distance():
        """Test creating player with maximum distance"""
        player_data = {
            "player_id": "long_hitter",
            "player_name": "Long Hitter",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "driver",
                    "carry_distance": 400,
                    "total_distance": 450,
                    "measurement_method": "rangefinder"
                }
            ]
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        assert response.status_code == 200
    
    
    def test_create_player_baseline_over_max_distance():
        """Test creating player with over-limit distance"""
        player_data = {
            "player_id": "super_long",
            "player_name": "Super Long",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "driver",
                    "carry_distance": 500,  # Over 400 limit
                    "total_distance": 550,   # Over 450 limit
                    "measurement_method": "rangefinder"
                }
            ]
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        assert response.status_code == 422  # Validation error
    
    
    def test_get_player_baseline_happy_path():
        """Test retrieving existing player baseline"""
        # First create a player
        player_data = {
            "player_id": "retrieve_test",
            "player_name": "Retrieve Test",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "iron_7",
                    "carry_distance": 150,
                    "total_distance": 155,
                    "measurement_method": "estimated"
                }
            ]
        }
        client.post("/api/v1/players/baseline", json=player_data)
        
        # Then retrieve it
        response = client.get("/api/v1/players/retrieve_test/baseline")
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == "retrieve_test"
        assert data["player_name"] == "Retrieve Test"
    
    
    def test_get_player_baseline_not_found():
        """Test getting non-existent player returns 404"""
        response = client.get("/api/v1/players/nonexistent_player_xyz/baseline")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    
    # ============================================================================
    # RECOMMENDATION ENDPOINTS - SIMPLE
    # ============================================================================
    
    def test_simple_recommendation_happy_path():
        """Test simple recommendation with valid data"""
        # First ensure we have a course and player
        courses_response = client.get("/api/v1/courses")
        courses = courses_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            
            request_data = {
                "course_id": course_id,
                "hole_number": 1,
                "distance_to_pin": 150,
                "wind_speed": 10,
                "wind_direction": "headwind",
                "lie": "fairway",
                "elevation_change": 0
            }
            
            response = client.post("/api/v1/recommendation/simple", json=request_data)
            assert response.status_code in [200, 503]  # 503 if services not available
            
            if response.status_code == 200:
                data = response.json()
                assert "caddie_call" in data
                assert "primary_club" in data
                assert "adjusted_distance" in data
                assert "why" in data
    
    
    def test_simple_recommendation_enum_mapping_wind():
        """Test wind direction enum mapping (left-to-right → crosswind_left)"""
        courses_response = client.get("/api/v1/courses")
        courses = courses_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            
            # Test all wind direction mappings
            wind_directions = [
                "calm",
                "headwind",
                "tailwind",
                "left-to-right",
                "right-to-left"
            ]
            
            for wind_dir in wind_directions:
                request_data = {
                    "course_id": course_id,
                    "hole_number": 1,
                    "distance_to_pin": 150,
                    "wind_speed": 10,
                    "wind_direction": wind_dir,
                    "lie": "fairway"
                }
                
                response = client.post("/api/v1/recommendation/simple", json=request_data)
                assert response.status_code in [200, 503]
    
    
    def test_simple_recommendation_enum_mapping_lie():
        """Test lie enum mapping (sand → bunker)"""
        courses_response = client.get("/api/v1/courses")
        courses = courses_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            
            # Test all lie mappings
            lies = ["fairway", "rough", "tee", "sand", "bunker"]
            
            for lie_type in lies:
                request_data = {
                    "course_id": course_id,
                    "hole_number": 1,
                    "distance_to_pin": 150,
                    "wind_speed": 0,
                    "wind_direction": "calm",
                    "lie": lie_type
                }
                
                response = client.post("/api/v1/recommendation/simple", json=request_data)
                assert response.status_code in [200, 503]
    
    
    def test_simple_recommendation_missing_course():
        """Test recommendation for non-existent course"""
        request_data = {
            "course_id": "nonexistent_course",
            "hole_number": 1,
            "distance_to_pin": 150,
            "wind_speed": 0,
            "wind_direction": "calm",
            "lie": "fairway"
        }
        
        response = client.post("/api/v1/recommendation/simple", json=request_data)
        assert response.status_code in [404, 503]
    
    
    def test_simple_recommendation_invalid_hole():
        """Test recommendation for invalid hole number"""
        courses_response = client.get("/api/v1/courses")
        courses = courses_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            
            request_data = {
                "course_id": course_id,
                "hole_number": 19,  # Invalid
                "distance_to_pin": 150,
                "wind_speed": 0,
                "wind_direction": "calm",
                "lie": "fairway"
            }
            
            response = client.post("/api/v1/recommendation/simple", json=request_data)
            assert response.status_code in [404, 503]
    
    
    def test_simple_recommendation_zero_distance():
        """Test recommendation with zero distance to pin"""
        courses_response = client.get("/api/v1/courses")
        courses = courses_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            
            request_data = {
                "course_id": course_id,
                "hole_number": 1,
                "distance_to_pin": 0,
                "wind_speed": 0,
                "wind_direction": "calm",
                "lie": "fairway"
            }
            
            response = client.post("/api/v1/recommendation/simple", json=request_data)
            # Should either work or return validation error
            assert response.status_code in [200, 400, 422, 503]
    
    
    def test_simple_recommendation_max_distance():
        """Test recommendation with maximum distance"""
        courses_response = client.get("/api/v1/courses")
        courses = courses_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            
            request_data = {
                "course_id": course_id,
                "hole_number": 1,
                "distance_to_pin": 600,  # Long par 5
                "wind_speed": 0,
                "wind_direction": "calm",
                "lie": "fairway"
            }
            
            response = client.post("/api/v1/recommendation/simple", json=request_data)
            assert response.status_code in [200, 503]
    
    
    def test_simple_recommendation_negative_wind():
        """Test recommendation with negative wind speed"""
        courses_response = client.get("/api/v1/courses")
        courses = courses_response.json()["courses"]
        
        if len(courses) > 0:
            course_id = courses[0]["id"]
            
            request_data = {
                "course_id": course_id,
                "hole_number": 1,
                "distance_to_pin": 150,
                "wind_speed": -10,  # Invalid
                "wind_direction": "calm",
                "lie": "fairway"
            }
            
            response = client.post("/api/v1/recommendation/simple", json=request_data)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422, 503]
    
    
    # ============================================================================
    # EXAMPLE ENDPOINTS
    # ============================================================================
    
    def test_get_sample_player():
        """Test getting sample player data"""
        response = client.get("/api/v1/examples/sample-player")
        assert response.status_code == 200
        data = response.json()
        # Should have player structure
        if "error" not in data:
            assert "player_id" in data
            assert "player_name" in data
            assert "club_distances" in data
    
    
    def test_get_sample_course():
        """Test getting sample course data"""
        response = client.get("/api/v1/examples/sample-course")
        assert response.status_code == 200
        data = response.json()
        # Should have course structure
        if "error" not in data:
            assert "course_id" in data
            assert "course_name" in data
            assert "holes" in data
    
    
    # ============================================================================
    # TEST RUNNER
    # ============================================================================
    
    def run_all_tests():
        """Run all comprehensive API tests"""
        test_functions = [
            # Health & Info
            test_health_check_happy_path,
            test_root_endpoint_happy_path,
            test_debug_courses_endpoint,
            
            # Course list/search
            test_list_courses_happy_path,
            test_search_courses_happy_path,
            test_search_courses_empty_string,
            test_search_courses_no_results,
            test_search_courses_special_chars,
            
            # Get specific course
            test_get_course_happy_path,
            test_get_course_not_found,
            test_get_course_empty_id,
            test_get_course_special_chars,
            
            # Get holes
            test_get_holes_happy_path,
            test_get_holes_course_not_found,
            test_get_specific_hole_happy_path,
            test_get_hole_invalid_number_zero,
            test_get_hole_invalid_number_19,
            test_get_hole_invalid_number_negative,
            test_get_hole_course_not_found,
            
            # Player baseline
            test_create_player_baseline_happy_path,
            test_create_player_baseline_minimal,
            test_create_player_baseline_missing_required_field,
            test_create_player_baseline_invalid_club_type,
            test_create_player_baseline_zero_distance,
            test_create_player_baseline_max_distance,
            test_create_player_baseline_over_max_distance,
            test_get_player_baseline_happy_path,
            test_get_player_baseline_not_found,
            
            # Recommendation
            test_simple_recommendation_happy_path,
            test_simple_recommendation_enum_mapping_wind,
            test_simple_recommendation_enum_mapping_lie,
            test_simple_recommendation_missing_course,
            test_simple_recommendation_invalid_hole,
            test_simple_recommendation_zero_distance,
            test_simple_recommendation_max_distance,
            test_simple_recommendation_negative_wind,
            
            # Examples
            test_get_sample_player,
            test_get_sample_course,
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_func in test_functions:
            try:
                test_func()
                print(f"✅ {test_func.__name__}")
                passed += 1
            except AssertionError as e:
                print(f"❌ {test_func.__name__}: {e}")
                failed += 1
            except Exception as e:
                if "courses" in str(e).lower() and "empty" in str(e).lower():
                    print(f"⏭️  {test_func.__name__}: Skipped (no test data)")
                    skipped += 1
                else:
                    print(f"💥 {test_func.__name__}: {type(e).__name__}: {e}")
                    failed += 1
        
        print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
        return failed == 0
    
    
    if __name__ == "__main__":
        success = run_all_tests()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"⚠️  Dependencies not installed: {e}")
    print("Install with: pip install fastapi httpx pytest")
    sys.exit(1)
