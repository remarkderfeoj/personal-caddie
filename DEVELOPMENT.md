# Development Guide

## Project Status

**Phase 1 (MVP)**: Semantic contracts + Physics engine
- ✅ Contracts defined (6 core contracts)
- ✅ Pydantic models for data validation
- ✅ FastAPI app skeleton with endpoints
- ✅ Example data (player baseline, sample course)
- ⏳ Recommendation engine (next)

## Getting Started

### 1. Setup Environment

```bash
cd personal-caddie/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the API

```bash
python main.py
# OR
uvicorn main:app --reload
```

Server will start at `http://localhost:8000`

**API Documentation**: http://localhost:8000/docs (interactive Swagger UI)

### 3. Test with Example Data

#### Load Sample Player Baseline
```bash
curl http://localhost:8000/api/v1/examples/sample-player
```

#### Load Sample Course
```bash
curl http://localhost:8000/api/v1/examples/sample-course
```

#### Create Player Baseline (POST)
```bash
curl -X POST http://localhost:8000/api/v1/players/baseline \
  -H "Content-Type: application/json" \
  -d @examples/sample_player_baseline.json
```

#### Create Course (POST)
```bash
curl -X POST http://localhost:8000/api/v1/courses \
  -H "Content-Type: application/json" \
  -d @examples/sample_course.json
```

## Next Steps: Implement Recommendation Engine

The core work now is building `services.py` with the physics calculations and course management logic.

### Key Components to Build

#### 1. **Physics Calculator** (`services.py`)
Adjusts player baseline distances based on conditions.

**Input**: Player baseline, club type, weather, elevation
**Output**: Adjusted carry and total distances

```python
def calculate_adjusted_distance(
    baseline_carry: int,
    temperature: float,
    elevation: int,
    wind_relative: str,
    wind_speed: float,
    rain: bool
) -> dict:
    """
    Calculate adjusted distance for given conditions.

    Physics:
    - Temperature: ±2 yards per 10°F from 70°F
    - Elevation: +0.116% distance per foot
    - Wind: headwind -3-5%, tailwind +3-5%
    - Rain: -3-5% reduction
    """
```

#### 2. **Course Management Logic**
Select optimal club based on:
- Distance to pin
- Player baseline distances
- Hazards and their penalties
- Pin placement (aggressive vs conservative)
- Wind relative to shot

```python
def recommend_club(
    distance_to_pin: int,
    player_baseline: PlayerBaseline,
    hole: Hole,
    weather: WeatherConditions,
    strategy: PinPlacementStrategy
) -> CaddieRecommendation:
    """
    Main recommendation logic.

    Algorithm:
    1. Get adjusted distance for each club
    2. Find clubs that reach pin distance
    3. Apply course management rules:
       - Avoid hazards where possible
       - Conservative: lay up short
       - Aggressive: attack pin
    4. Calculate confidence based on:
       - Distance accuracy (dispersion)
       - Hazard avoidance
       - Lie quality
    5. Generate alternative clubs with rationale
    """
```

#### 3. **Wind Calculations**
This is tricky—convert compass wind direction + shot bearing into headwind/tailwind.

```python
def calculate_wind_effect(
    wind_direction_compass: str,  # "NE", "SW", etc.
    shot_bearing_degrees: int,    # 0-359
    wind_speed_mph: float
) -> dict:
    """
    Convert compass wind to shot-relative wind.

    Logic:
    - Convert wind direction compass to degrees
    - Calculate angle between wind and shot
    - Headwind (0-90°): reduces distance
    - Tailwind (180-270°): increases distance
    - Crosswind: affects accuracy, minor distance effect
    """
```

### Test Data Structure

Example shot analysis request:
```json
{
  "analysis_id": "shot_001",
  "player_id": "joe_kramer_001",
  "hole_id": "pebble_7",
  "weather_condition_id": "weather_001",
  "pin_location": "front",
  "current_distance_to_pin_yards": 110,
  "player_lie": "fairway",
  "lie_quality": "clean",
  "wind_relative_to_shot": "calm",
  "pin_placement_strategy": "conservative"
}
```

Expected response:
```json
{
  "recommendation_id": "rec_001",
  "shot_analysis_id": "shot_001",
  "primary_recommendation": {
    "club": "sand_wedge",
    "target_area": "center of green, water left is only danger",
    "expected_carry_yards": 78,
    "expected_total_yards": 80,
    "confidence_percent": 92
  },
  "adjustment_summary": {
    "temperature_adjustment_yards": -1,
    "elevation_adjustment_yards": 0,
    "wind_adjustment_yards": 0,
    "rain_adjustment_percent": 0,
    "lie_adjustment_percent": 0,
    "human_readable_summary": [
      "-1 yard for cool temperature (68°F)"
    ]
  },
  "alternative_clubs": [],
  "hazard_analysis": {
    "hazards_in_play": [
      {
        "hazard_type": "water",
        "location": "left",
        "distance_from_tee": 0,
        "risk_level": "high"
      }
    ],
    "safe_miss_direction": "right"
  },
  "strategy_notes": "Conservative play: sand wedge gets you near pin with water completely out of play. No reason to be aggressive on this par 3."
}
```

## Architecture Decisions

### Why Semantic Contracts?
- Documents **what** the data means, not just structure
- Makes physics and business rules explicit
- Enables AI agents to understand the domain
- Contracts are the "API" between golf domain and software

### Why FastAPI?
- Modern, fast, with automatic API docs
- Pydantic integration for validation
- Easy to extend for database/async

### Why Separate Contracts?
- Each contract is independently documented
- Clear ownership (System, Course Management, Player, Weather)
- Update frequency varies (static vs real-time)
- Supports future multi-service architecture

## Future Phases

**Phase 2: Persistence & Frontend**
- PostgreSQL database
- React dashboard
- Shot history tracking

**Phase 3: Learning**
- Track player performance over time
- Detect improving distances
- Confidence adjustments based on actual results

**Phase 4: Visualization**
- Course maps with pin placements
- Yardage book integration
- Real-time shot tracking

## Key Files to Know

- `contracts/` - Source of truth for data model
- `backend/models.py` - Pydantic models (auto-generated from contracts)
- `backend/services.py` - Business logic (TBD: recommendation engine)
- `examples/` - Test data
- `README.md` - Project overview

## Questions & Decisions

### Wind Calculation Complexity
We noted that wind calculation could "do more harm than good" in reality. Consider:
- Should we provide headwind/tailwind estimates?
- Should we only provide confidence adjustments?
- Should player input wind relative to shot directly?

### Pin Placement Rotation
Future: Map pin positions (1, 2, 3) to date ranges for course visualization. For now, just use front/center/back.

### Hole-by-Hole Elevation
Future: Golf simulator databases have full undulation data. For MVP, use only course elevation above sea level.

### Player Profile Learning
Phase 1: Manual baseline entry
Phase 2: Track actual shot distances over time and refine baseline

## Quick Reference: Physics Formulas

```
Temperature adjustment:
  Per 10°F change from 70°F baseline
  ~2 yards per 10°F (cold=shorter, hot=longer)

Elevation adjustment:
  +0.116% distance per foot above sea level
  5000 ft elevation ≈ 5-6% distance increase

Wind (relative to shot):
  Headwind: -3-5% distance
  Tailwind: +3-5% distance
  Crosswind: Minor distance effect, accuracy impact

Rain/Wet fairway:
  -3-5% total distance reduction

Humidity:
  <1 yard impact, negligible for MVP
```

## Contact & Feedback

Built with Claude Code. Questions? See `/help` in Claude Code.
