"""
Personal Caddie FastAPI Application

Main entry point for the caddie recommendation engine.
Provides API endpoints for:
- Player baseline management
- Course data
- Shot analysis and recommendations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
import json
import os

from models import (
    PlayerBaseline,
    CourseHoles,
    WeatherConditions,
    ShotAnalysis,
    CaddieRecommendation,
)
from services import generate_recommendation

# Initialize FastAPI app
app = FastAPI(
    title="Personal Caddie",
    description="AI-powered caddie system for golf shot recommendations",
    version="0.1.0",
)

# Add CORS middleware for frontend integration (Phase 2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint - API information"""
    return {
        "name": "Personal Caddie API",
        "version": "0.1.0",
        "description": "AI-powered golf caddie recommendation system",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# PLAYER BASELINE ENDPOINTS
# ============================================================================

@app.post("/api/v1/players/baseline")
def create_player_baseline(baseline: PlayerBaseline):
    """
    Create or update a player's baseline distances.

    The player should measure/estimate their club distances when:
    - Fresh and warmed up
    - On a typical fairway
    - Under standard conditions (calm, 70°F, dry)

    These are used as the baseline for all adjustments.
    """
    # TODO: Persist to database
    return {
        "status": "created",
        "player_id": baseline.player_id,
        "message": f"Baseline created for {baseline.player_name}",
        "clubs_registered": len(baseline.club_distances),
    }


@app.get("/api/v1/players/{player_id}/baseline")
def get_player_baseline(player_id: str):
    """Retrieve a player's baseline distances"""
    # TODO: Fetch from database
    return {
        "player_id": player_id,
        "message": "TODO: Implement database fetch",
    }


# ============================================================================
# COURSE DATA ENDPOINTS
# ============================================================================

@app.post("/api/v1/courses")
def create_course(course: CourseHoles):
    """
    Register a golf course with all 18 holes.

    Required fields:
    - course_name
    - course_elevation_feet
    - 18 holes with distance, par, bearing, hazards
    """
    # TODO: Persist to database
    return {
        "status": "created",
        "course_id": course.course_id,
        "course_name": course.course_name,
        "holes": len(course.holes),
    }


@app.get("/api/v1/courses/{course_id}")
def get_course(course_id: str):
    """Retrieve course data"""
    # TODO: Fetch from database
    return {"course_id": course_id, "message": "TODO: Implement database fetch"}


@app.get("/api/v1/courses/{course_id}/holes/{hole_number}")
def get_hole(course_id: str, hole_number: int):
    """Get data for a specific hole"""
    if hole_number < 1 or hole_number > 18:
        raise HTTPException(status_code=400, detail="Hole number must be 1-18")
    # TODO: Fetch from database
    return {
        "course_id": course_id,
        "hole_number": hole_number,
        "message": "TODO: Implement database fetch",
    }


# ============================================================================
# WEATHER ENDPOINTS
# ============================================================================

@app.post("/api/v1/weather")
def record_weather(weather: WeatherConditions):
    """
    Record current weather conditions.
    Used for calculating distance adjustments.
    """
    # TODO: Persist to database
    return {
        "status": "recorded",
        "condition_id": weather.condition_id,
        "temperature": weather.temperature_fahrenheit,
        "wind_speed": weather.wind_speed_mph,
    }


@app.get("/api/v1/weather/{condition_id}")
def get_weather(condition_id: str):
    """Retrieve recorded weather"""
    # TODO: Fetch from database
    return {"condition_id": condition_id, "message": "TODO: Implement database fetch"}


# ============================================================================
# RECOMMENDATION ENDPOINTS (CORE FUNCTIONALITY)
# ============================================================================

@app.post("/api/v1/recommendations")
def get_recommendation(analysis: ShotAnalysis) -> CaddieRecommendation:
    """
    Get a caddie recommendation for a shot.

    Input:
    - Player ID
    - Course ID and Hole number
    - Current distance to pin
    - Lie (fairway, rough, bunker, etc.)
    - Pin location (front, center, back)
    - Weather conditions
    - Wind relative to shot
    - Player's strategy preference (aggressive, balanced, conservative)

    Output:
    - Primary club recommendation
    - Target area to aim for
    - Expected distances with adjustments
    - Alternative clubs (if strategically different)
    - Hazard analysis
    - Confidence level
    """
    # Load player baseline from example file (MVP)
    player_file = os.path.join(
        os.path.dirname(__file__),
        "../examples/sample_player_baseline.json"
    )
    with open(player_file, "r") as f:
        player_data = json.load(f)
    player_baseline = PlayerBaseline(**player_data)

    # Load course data from example file (MVP)
    course_file = os.path.join(
        os.path.dirname(__file__),
        "../examples/sample_course.json"
    )
    with open(course_file, "r") as f:
        course_data = json.load(f)
    course = CourseHoles(**course_data)

    # Find the hole
    hole = next((h for h in course.holes if h.hole_id == analysis.hole_id), None)
    if not hole:
        raise HTTPException(status_code=404, detail=f"Hole {analysis.hole_id} not found")

    # Create weather conditions
    # TODO: In production, fetch from database using analysis.weather_condition_id
    weather = WeatherConditions(
        condition_id=analysis.weather_condition_id,
        timestamp=datetime.now(),
        temperature_fahrenheit=70.0,
        wind_speed_mph=5.0,
        wind_direction_compass="calm",
        humidity_percent=50,
        rain=False,
        ground_conditions="dry"
    )

    # Generate recommendation using services module
    recommendation = generate_recommendation(
        shot_analysis=analysis,
        player_baseline=player_baseline,
        hole=hole,
        weather=weather,
        course_elevation_feet=course.course_elevation_feet
    )

    return recommendation


# ============================================================================
# EXAMPLE ENDPOINTS FOR TESTING
# ============================================================================

@app.get("/api/v1/examples/sample-player")
def get_sample_player():
    """Returns example player baseline for testing"""
    example_file = os.path.join(
        os.path.dirname(__file__),
        "../examples/sample_player_baseline.json"
    )
    if os.path.exists(example_file):
        with open(example_file, "r") as f:
            return json.load(f)
    return {"error": "Example file not found"}


@app.get("/api/v1/examples/sample-course")
def get_sample_course():
    """Returns example course data for testing"""
    example_file = os.path.join(
        os.path.dirname(__file__),
        "../examples/sample_course.json"
    )
    if os.path.exists(example_file):
        with open(example_file, "r") as f:
            return json.load(f)
    return {"error": "Example file not found"}


# ============================================================================
# ERROR HANDLERS
# ============================================================================

from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid input",
            "detail": str(exc),
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
