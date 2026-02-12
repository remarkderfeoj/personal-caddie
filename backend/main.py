"""
Personal Caddie FastAPI Application

Main entry point for the caddie recommendation engine.
Provides API endpoints for:
- Player baseline management
- Course data
- Shot analysis and recommendations

SECURITY: Rate limited, CORS configured, input validated.
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import List, Optional
from datetime import datetime
import json
import os
import logging

from models import (
    PlayerBaseline,
    CourseHoles,
    WeatherConditions,
    ShotAnalysis,
    CaddieRecommendation,
)
from auth import get_current_user, get_optional_user, User
from data_store import data_store

# Import recommendation service
try:
    from services import generate_recommendation
    SERVICES_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not import services: {e}")
    SERVICES_AVAILABLE = False
    generate_recommendation = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Caddie",
    description="AI-powered caddie system for golf shot recommendations",
    version="0.1.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS (allow all for mobile access in development)
# In production, set ALLOWED_ORIGINS env var to restrict
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in ALLOWED_ORIGINS else ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# ============================================================================
# GLOBAL ERROR HANDLER
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler - never leaks stack traces to clients.
    
    Logs full error internally, returns safe generic message.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/app")
async def serve_app():
    """Serve the mobile web app"""
    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "frontend/index.html"
    )
    return FileResponse(frontend_path)


@app.get("/")
@limiter.limit("100/minute")
def read_root(request: Request):
    """Root endpoint - API information"""
    return {
        "name": "Personal Caddie API",
        "version": "0.1.0",
        "description": "AI-powered golf caddie recommendation system",
        "status": "running",
        "web_app": "/app",
    }


@app.get("/health")
@limiter.limit("100/minute")
def health_check(request: Request):
    """Health check endpoint"""
    courses_loaded = len(data_store.courses)
    players_loaded = len(data_store.players)
    ready = courses_loaded > 0 and players_loaded > 0 and SERVICES_AVAILABLE
    return {
        "status": "healthy" if ready else "degraded",
        "courses_loaded": courses_loaded,
        "players_loaded": players_loaded,
        "services_available": SERVICES_AVAILABLE,
        "ready": ready
    }


@app.get("/debug/courses")
@limiter.limit("100/minute")
def debug_courses(request: Request):
    """Debug endpoint to see what courses are loaded"""
    return {
        "total_courses": len(data_store.courses),
        "course_ids": list(data_store.courses.keys()),
        "course_names": [c.course_name for c in data_store.courses.values()]
    }


# ============================================================================
# PLAYER BASELINE ENDPOINTS
# ============================================================================

@app.post("/api/v1/players/baseline")
@limiter.limit("100/minute")
def create_player_baseline(request: Request, baseline: PlayerBaseline):
    """
    Create or update a player's baseline distances.

    The player should measure/estimate their club distances when:
    - Fresh and warmed up
    - On a typical fairway
    - Under standard conditions (calm, 70°F, dry)

    These are used as the baseline for all adjustments.
    """
    data_store.add_player(baseline)
    return {
        "status": "created",
        "player_id": baseline.player_id,
        "message": f"Baseline created for {baseline.player_name}",
        "clubs_registered": len(baseline.club_distances),
    }


@app.get("/api/v1/players/{player_id}/baseline")
@limiter.limit("100/minute")
def get_player_baseline(request: Request, player_id: str) -> PlayerBaseline:
    """Retrieve a player's baseline distances"""
    player = data_store.get_player_by_id(player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    return player


# ============================================================================
# COURSE DATA ENDPOINTS
# ============================================================================

@app.get("/api/v1/courses")
@limiter.limit("100/minute")
def list_courses(request: Request, search: Optional[str] = None):
    """
    List all courses or search by name.
    
    Query params:
        search: Optional search string (searches course name and ID)
    
    Returns:
        List of matching courses
    """
    def course_summary(c):
        return {
            "id": c.course_id,
            "name": c.course_name,
            "elevation_feet": c.course_elevation_feet,
            "holes": len(c.holes),
            "center_lat": getattr(c, 'center_lat', None),
            "center_lng": getattr(c, 'center_lng', None),
        }
    
    if search:
        courses = data_store.search_courses(search)
        return {"count": len(courses), "query": search, "courses": [course_summary(c) for c in courses]}
    else:
        courses = data_store.list_all_courses()
        return {"count": len(courses), "courses": [course_summary(c) for c in courses]}


@app.post("/api/v1/courses")
@limiter.limit("100/minute")
def create_course(request: Request, course: CourseHoles):
    """
    Register a golf course with all 18 holes.

    Required fields:
    - course_name
    - course_elevation_feet
    - holes (list of hole data)
    """
    data_store.add_course(course)
    return {
        "status": "created",
        "course_id": course.course_id,
        "course_name": course.course_name,
        "holes": len(course.holes),
    }


@app.get("/api/v1/courses/{course_id}")
@limiter.limit("100/minute")
def get_course(request: Request, course_id: str) -> CourseHoles:
    """
    Retrieve full course data by ID.
    
    Returns complete course with all holes, hazards, etc.
    """
    course = data_store.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
    return course


@app.get("/api/v1/courses/{course_id}/holes")
@limiter.limit("100/minute")
def get_holes(request: Request, course_id: str):
    """Get all holes for a course"""
    course = data_store.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
    
    holes = []
    for h in sorted(course.holes, key=lambda x: x.hole_number):
        hole_data = {
            "hole_id": h.hole_id,
            "hole_number": h.hole_number,
            "par": h.par,
            "handicap_index": h.handicap_index,
            "distance": h.distance_to_pin_yards,
            "elevation_change": h.elevation_change_feet or 0,
            "fairway_type": h.fairway_type.value if hasattr(h.fairway_type, 'value') else h.fairway_type,
            "green_shape": h.green_shape.value if h.green_shape and hasattr(h.green_shape, 'value') else (h.green_shape or "medium"),
            "hazards": [
                {
                    "type": hz.hazard_type.value if hasattr(hz.hazard_type, 'value') else hz.hazard_type,
                    "location": hz.location.value if hasattr(hz.location, 'value') else hz.location,
                    "distance": hz.distance_from_tee_yards,
                    "description": hz.description or ""
                }
                for hz in (h.hazards or [])
            ],
            "notes": h.notes or "",
        }
        # Add GPS coords if available
        if h.tee_lat is not None:
            hole_data["tee_lat"] = h.tee_lat
            hole_data["tee_lng"] = h.tee_lng
            hole_data["green_lat"] = h.green_lat
            hole_data["green_lng"] = h.green_lng
        holes.append(hole_data)
    
    return {
        "course_id": course_id,
        "course_name": course.course_name,
        "elevation": course.course_elevation_feet,
        "center_lat": getattr(course, 'center_lat', None),
        "center_lng": getattr(course, 'center_lng', None),
        "holes": holes
    }


@app.get("/api/v1/courses/{course_id}/holes/{hole_number}")
@limiter.limit("100/minute")
def get_hole(request: Request, course_id: str, hole_number: int):
    """Get data for a specific hole"""
    if hole_number < 1 or hole_number > 18:
        raise HTTPException(status_code=400, detail="Hole number must be 1-18")
    
    course = data_store.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
    
    hole = next((h for h in course.holes if h.hole_number == hole_number), None)
    if not hole:
        raise HTTPException(status_code=404, detail=f"Hole {hole_number} not found on course {course_id}")
    
    return hole


# ============================================================================
# WEATHER ENDPOINTS
# ============================================================================

@app.post("/api/v1/weather")
@limiter.limit("100/minute")
def record_weather(request: Request, weather: WeatherConditions):
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
@limiter.limit("100/minute")
def get_weather(request: Request, condition_id: str):
    """Retrieve recorded weather"""
    # TODO: Fetch from database
    return {"condition_id": condition_id, "message": "TODO: Implement database fetch"}


# ============================================================================
# RECOMMENDATION ENDPOINTS (CORE FUNCTIONALITY)
# ============================================================================

@app.post("/api/v1/recommendation/simple")
@limiter.limit("20/minute")
async def get_simple_recommendation(request: Request):
    """
    Simplified recommendation endpoint for web app.
    Accepts basic shot parameters and returns recommendation.
    """
    if not SERVICES_AVAILABLE or generate_recommendation is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation service unavailable - check server logs for import errors"
        )
    
    try:
        data = await request.json()
        
        # Extract parameters
        course_id = data.get("course_id")
        hole_number = data.get("hole_number", 1)
        distance_to_pin = data.get("distance_to_pin", 150)
        wind_speed = data.get("wind_speed", 0)
        wind_direction = data.get("wind_direction", "calm")
        lie = data.get("lie", "fairway")
        elevation_change = data.get("elevation_change", 0)
        
        logger.info(f"Recommendation request: course={course_id}, hole={hole_number}, distance={distance_to_pin}")
        
        # Get course and hole
        course = data_store.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
        
        hole = next((h for h in course.holes if h.hole_number == hole_number), None)
        if not hole:
            raise HTTPException(status_code=404, detail=f"Hole {hole_number} not found")
        
        # Use specific player if provided, else default
        player_id = data.get("player_id")
        if player_id:
            player_baseline = data_store.get_player_by_id(player_id)
            if not player_baseline:
                # Fall back to default
                players = data_store.list_all_players()
                if not players:
                    raise HTTPException(status_code=404, detail="No players configured")
                player_baseline = players[0]
        else:
            players = data_store.list_all_players()
            if not players:
                raise HTTPException(status_code=404, detail="No players configured")
            player_baseline = players[0]
        
        # Map frontend wind direction to WindRelativeToShot enum values
        wind_map = {
            "calm": "calm",
            "headwind": "headwind",
            "tailwind": "tailwind",
            "left-to-right": "crosswind_left",
            "right-to-left": "crosswind_right",
        }
        mapped_wind = wind_map.get(wind_direction, "calm")
        
        # Map frontend lie to PlayerLie enum values
        lie_map = {
            "fairway": "fairway",
            "rough": "rough",
            "tee": "tee",
            "sand": "bunker",
            "bunker": "bunker",
        }
        mapped_lie = lie_map.get(lie, "fairway")
        
        # Create weather with compass direction (use calm/N since we use relative wind)
        weather = WeatherConditions(
            condition_id="current",
            timestamp=datetime.now(),
            temperature_fahrenheit=70.0,
            wind_speed_mph=float(wind_speed),
            wind_direction_compass="calm",
            humidity_percent=50,
            rain=False,
            ground_conditions="dry"
        )
        
        # Create shot analysis with correct field names
        import time
        analysis = ShotAnalysis(
            analysis_id=f"shot-{int(time.time())}",
            player_id=player_baseline.player_id,
            hole_id=hole.hole_id,
            weather_condition_id="current",
            pin_location="center",
            current_distance_to_pin_yards=int(distance_to_pin),
            player_lie=mapped_lie,
            wind_relative_to_shot=mapped_wind if mapped_wind != "calm" else None,
            pin_placement_strategy="balanced",
            timestamp=datetime.now()
        )
        
        # Generate recommendation
        logger.info("Generating recommendation...")
        recommendation = generate_recommendation(
            shot_analysis=analysis,
            player_baseline=player_baseline,
            hole=hole,
            weather=weather,
            course_elevation_feet=course.course_elevation_feet + elevation_change,
            round_context=None
        )
        
        # Map ClubType enum to display name
        club_val = recommendation.primary_club.value if hasattr(recommendation.primary_club, 'value') else str(recommendation.primary_club)
        club_display = club_val.replace("_", " ").title()
        
        logger.info(f"Recommendation generated: {club_display}")
        
        return {
            "caddie_call": recommendation.caddie_call,
            "primary_club": club_display,
            "primary_target": recommendation.primary_target,
            "adjusted_distance": recommendation.adjusted_distance,
            "why": recommendation.why,
            "optimal_miss": recommendation.optimal_miss,
            "danger_zone": recommendation.danger_zone,
            "caddie_note": recommendation.caddie_note,
            "confidence": recommendation.confidence_percent or 75,
            "risk_reward": {
                "aggressive_upside": recommendation.risk_reward.aggressive_upside,
                "aggressive_downside": recommendation.risk_reward.aggressive_downside,
                "conservative_upside": recommendation.risk_reward.conservative_upside,
                "conservative_downside": recommendation.risk_reward.conservative_downside,
            },
            "alternatives": [
                {
                    "club": alt.club.value.replace("_", " ").title() if hasattr(alt.club, 'value') else str(alt.club),
                    "target": alt.target,
                    "scenario": alt.scenario,
                }
                for alt in (recommendation.alternatives or [])
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in simple recommendation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/api/v1/recommendation")
@limiter.limit("20/minute")
def get_recommendation(
    request: Request,
    analysis: ShotAnalysis,
    current_user: Optional[User] = Depends(get_optional_user)
) -> CaddieRecommendation:
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
    # Load player baseline from data store
    player_baseline = data_store.get_player_by_id(analysis.player_id)
    if not player_baseline:
        raise HTTPException(status_code=404, detail=f"Player {analysis.player_id} not found")

    # Extract course ID from hole ID (format: "course_hole")
    # For now, we need to search through courses to find the hole
    course = None
    hole = None
    
    for c in data_store.list_all_courses():
        for h in c.holes:
            if h.hole_id == analysis.hole_id:
                course = c
                hole = h
                break
        if course:
            break
    
    if not course or not hole:
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

    # Build round context if available in request
    # TODO: Accept RoundContext as part of request body in future
    round_ctx = None
    # For now, round_context is optional - can be added to API later
    
    # Generate recommendation using services module
    recommendation = generate_recommendation(
        shot_analysis=analysis,
        player_baseline=player_baseline,
        hole=hole,
        weather=weather,
        course_elevation_feet=course.course_elevation_feet,
        round_context=round_ctx
    )

    return recommendation


# ============================================================================
# EXAMPLE ENDPOINTS FOR TESTING
# ============================================================================

@app.get("/api/v1/examples/sample-player")
@limiter.limit("100/minute")
def get_sample_player(request: Request):
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
@limiter.limit("100/minute")
def get_sample_course(request: Request):
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
