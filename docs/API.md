# Personal Caddie API Documentation

**Base URL:** `http://localhost:8000` (development)  
**Version:** 0.1.0  
**Interactive Docs:** `/docs` (Swagger UI) or `/redoc` (ReDoc)

---

## Authentication

Currently using stub authentication. Production will use JWT tokens.

```bash
# Future: Include Bearer token
Authorization: Bearer <token>
```

---

## Rate Limits

- **Global:** 100 requests/minute per IP
- **Recommendations:** 20 requests/minute per IP (compute-intensive)

Exceeding limits returns `429 Too Many Requests`.

---

## Core Endpoints

### Health & Info

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### `GET /`
API information.

**Response:**
```json
{
  "name": "Personal Caddie API",
  "version": "0.1.0",
  "description": "AI-powered golf caddie recommendation system",
  "status": "running"
}
```

---

### Courses

#### `GET /api/v1/courses`
List all courses or search by name.

**Query Parameters:**
- `search` (optional): Search string (case-insensitive)

**Example:**
```bash
curl http://localhost:8000/api/v1/courses?search=pebble
```

**Response:**
```json
{
  "count": 1,
  "query": "pebble",
  "courses": [
    {
      "course_id": "augusta_national",
      "course_name": "Augusta National",
      "elevation_feet": 200,
      "holes": 3
    }
  ]
}
```

---

#### `POST /api/v1/courses`
Create a new course.

**Request Body:**
```json
{
  "course_id": "pebble_beach",
  "course_name": "Pebble Beach Golf Links",
  "course_elevation_feet": 50,
  "holes": [
    {
      "hole_id": "pebble_7",
      "hole_number": 7,
      "par": 3,
      "handicap_index": 15,
      "distance_to_pin_yards": 110,
      "shot_bearing_degrees": 315,
      "fairway_type": "fairway",
      "hazards": [
        {
          "hazard_type": "water",
          "location": "left",
          "distance_from_tee_yards": 0,
          "severity": "water",
          "description": "Pacific Ocean"
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "status": "created",
  "course_id": "pebble_beach",
  "course_name": "Pebble Beach Golf Links",
  "holes": 1
}
```

---

#### `GET /api/v1/courses/{course_id}`
Get full course details.

**Example:**
```bash
curl http://localhost:8000/api/v1/courses/augusta_national
```

**Response:** Full `CourseHoles` object with all holes and hazards.

---

#### `GET /api/v1/courses/{course_id}/holes/{hole_number}`
Get specific hole details.

**Parameters:**
- `course_id`: Course identifier
- `hole_number`: 1-18

**Example:**
```bash
curl http://localhost:8000/api/v1/courses/augusta_national/holes/7
```

---

### Players

#### `POST /api/v1/players/baseline`
Create or update player baseline distances.

**Request Body:**
```json
{
  "player_id": "joe_kramer_001",
  "player_name": "Joe Kramer",
  "created_date": "2024-01-01T00:00:00Z",
  "club_distances": [
    {
      "club_type": "driver",
      "carry_distance": 220,
      "total_distance": 235,
      "measurement_method": "rangefinder"
    },
    {
      "club_type": "iron_7",
      "carry_distance": 150,
      "total_distance": 155,
      "measurement_method": "rangefinder"
    }
  ]
}
```

**Response:**
```json
{
  "status": "created",
  "player_id": "joe_kramer_001",
  "message": "Baseline created for Joe Kramer",
  "clubs_registered": 2
}
```

---

#### `GET /api/v1/players/{player_id}/baseline`
Retrieve player baseline distances.

**Example:**
```bash
curl http://localhost:8000/api/v1/players/joe_kramer_001/baseline
```

---

### Recommendations (Core Feature)

#### `POST /api/v1/recommendations`
Get caddie recommendation for a shot.

**Rate Limit:** 20 requests/minute

**Request Body:**
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
  "pin_placement_strategy": "balanced"
}
```

**Request Fields:**
- `analysis_id`: Unique identifier for this analysis
- `player_id`: Player identifier
- `hole_id`: Hole identifier
- `weather_condition_id`: Weather identifier (system-generated)
- `pin_location`: `front` | `center` | `back`
- `current_distance_to_pin_yards`: Distance to pin (1-700)
- `player_lie`: `tee` | `fairway` | `rough` | `bunker` | `woods` | `semi_rough`
- `lie_quality` (optional): `clean` | `normal` | `thick` | `plugged`
- `wind_relative_to_shot` (optional): `headwind` | `tailwind` | `crosswind_left` | `crosswind_right` | `calm`
- `pin_placement_strategy` (optional): `aggressive` | `balanced` | `conservative`

**Response:**
```json
{
  "recommendation_id": "rec_shot_001",
  "shot_analysis_id": "shot_001",
  "timestamp": "2024-01-01T12:00:00Z",
  
  "primary_club": "sand_wedge",
  "primary_target": "Aim center, front pin position",
  "caddie_call": "Sand Wedge, aim center, front pin position. trust it.",
  "caddie_note": "Good par 3. Trust your distance.",
  
  "why": "Sand Wedge plays 101 yards here (+19y elevation).",
  "adjusted_distance": 101,
  "optimal_miss": "Miss center is safe",
  "danger_zone": "Do not miss water left",
  
  "alternatives": [
    {
      "club": "gap_wedge",
      "target": "Take dead aim, 115 yards",
      "scenario": "If you want more club or wind dies"
    }
  ],
  
  "risk_reward": {
    "aggressive_upside": "Close look at birdie",
    "aggressive_downside": "Risk of water",
    "conservative_upside": "Safe par with birdie chance",
    "conservative_downside": "Comfortable two-putt"
  },
  
  "confidence_percent": 95,
  "expected_carry_yards": 99
}
```

---

### Examples (Testing)

#### `GET /api/v1/examples/sample-player`
Get sample player data.

#### `GET /api/v1/examples/sample-course`
Get sample course data.

---

## Data Models

### ClubType Enum
```
driver, wood_3, wood_5, 
iron_2, iron_3, iron_4, iron_5, iron_6, iron_7, iron_8, iron_9,
pitching_wedge, gap_wedge, sand_wedge, lob_wedge
```

### PinLocation Enum
```
front, center, back
```

### PlayerLie Enum
```
tee, fairway, rough, bunker, woods, semi_rough
```

### LieQuality Enum
```
clean, normal, thick, plugged
```

### PinPlacementStrategy Enum
```
aggressive, balanced, conservative
```

---

## Error Responses

### 400 Bad Request
Invalid input validation.

```json
{
  "detail": "Hole number must be 1-18"
}
```

### 404 Not Found
Resource not found.

```json
{
  "detail": "Course augusta_national not found"
}
```

### 429 Too Many Requests
Rate limit exceeded.

```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
Server error (details not exposed).

```json
{
  "detail": "Internal server error"
}
```

---

## Interactive Documentation

Visit these URLs when server is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Example Workflows

### Complete Recommendation Flow

```bash
# 1. List available courses
curl http://localhost:8000/api/v1/courses

# 2. Get course details
curl http://localhost:8000/api/v1/courses/augusta_national

# 3. Get player baseline
curl http://localhost:8000/api/v1/players/joe_kramer_001/baseline

# 4. Get recommendation
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "shot_001",
    "player_id": "joe_kramer_001",
    "hole_id": "pebble_7",
    "weather_condition_id": "weather_001",
    "pin_location": "front",
    "current_distance_to_pin_yards": 110,
    "player_lie": "fairway",
    "pin_placement_strategy": "balanced"
  }'
```

---

## SDKs & Libraries

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

def get_recommendation(analysis):
    response = requests.post(
        f"{BASE_URL}/api/v1/recommendations",
        json=analysis
    )
    return response.json()

# Usage
recommendation = get_recommendation({
    "analysis_id": "shot_001",
    "player_id": "joe_kramer_001",
    "hole_id": "pebble_7",
    "weather_condition_id": "weather_001",
    "pin_location": "front",
    "current_distance_to_pin_yards": 110,
    "player_lie": "fairway",
    "pin_placement_strategy": "balanced"
})

print(recommendation["caddie_call"])
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000";

async function getRecommendation(analysis: ShotAnalysis) {
  const response = await fetch(`${BASE_URL}/api/v1/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(analysis),
  });
  return response.json();
}

// Usage
const recommendation = await getRecommendation({
  analysis_id: "shot_001",
  player_id: "joe_kramer_001",
  hole_id: "pebble_7",
  weather_condition_id: "weather_001",
  pin_location: "front",
  current_distance_to_pin_yards: 110,
  player_lie: "fairway",
  pin_placement_strategy: "balanced",
});

console.log(recommendation.caddie_call);
```

---

## Changelog

### 0.1.0 (2024-01-01)
- Initial release
- Course management
- Player baselines
- Recommendation engine with conviction-first format
- Rate limiting
- Search functionality
