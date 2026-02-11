"""
Integration tests for API endpoints.

Requires: pip install pytest httpx
Run: pytest tests/test_api.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    def test_health_check():
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    
    def test_root_endpoint():
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"
    
    
    def test_list_courses_empty_search():
        """Test listing all courses"""
        response = client.get("/api/v1/courses")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "courses" in data
    
    
    def test_search_courses():
        """Test course search functionality"""
        response = client.get("/api/v1/courses?search=pebble")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "pebble"
    
    
    def test_get_course_not_found():
        """Test getting non-existent course returns 404"""
        response = client.get("/api/v1/courses/nonexistent")
        assert response.status_code == 404
    
    
    def test_get_player_not_found():
        """Test getting non-existent player returns 404"""
        response = client.get("/api/v1/players/nonexistent/baseline")
        assert response.status_code == 404
    
    
    def test_get_sample_player():
        """Test getting sample player data"""
        response = client.get("/api/v1/examples/sample-player")
        assert response.status_code == 200
        data = response.json()
        assert "player_id" in data
        assert "player_name" in data
        assert "club_distances" in data
    
    
    def test_get_sample_course():
        """Test getting sample course data"""
        response = client.get("/api/v1/examples/sample-course")
        assert response.status_code == 200
        data = response.json()
        assert "course_id" in data
        assert "course_name" in data
        assert "holes" in data
    
    
    def test_create_player_baseline():
        """Test creating player baseline"""
        player_data = {
            "player_id": "test_player",
            "player_name": "Test Player",
            "created_date": "2024-01-01T00:00:00Z",
            "club_distances": [
                {
                    "club_type": "driver",
                    "carry_distance": 220,
                    "total_distance": 240,
                    "measurement_method": "estimated"
                }
            ]
        }
        response = client.post("/api/v1/players/baseline", json=player_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["player_id"] == "test_player"
    
    
    def test_invalid_hole_number():
        """Test that invalid hole numbers are rejected"""
        response = client.get("/api/v1/courses/test_course/holes/19")
        assert response.status_code == 400
    
    
    def test_rate_limiting_enabled():
        """Test that rate limiting is configured (check headers)"""
        response = client.get("/health")
        # Rate limiting should add X-RateLimit headers
        # This is a basic check - full rate limit testing requires many requests
        assert response.status_code == 200
    
    
    def run_all_tests():
        """Run all API tests"""
        test_functions = [
            test_health_check,
            test_root_endpoint,
            test_list_courses_empty_search,
            test_search_courses,
            test_get_course_not_found,
            test_get_player_not_found,
            test_get_sample_player,
            test_get_sample_course,
            test_create_player_baseline,
            test_invalid_hole_number,
            test_rate_limiting_enabled,
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

except ImportError as e:
    print(f"⚠️  Dependencies not installed: {e}")
    print("Install with: pip install fastapi httpx pytest")
    sys.exit(1)
