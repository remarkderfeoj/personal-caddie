# Personal Caddie - Quick Start Guide

## 🚀 Start the Server

```bash
# Activate conda environment
conda activate personal-caddie

# Go to backend directory
cd /Users/joekramer/personal-caddie/backend

# Start server
python main.py
```

Server runs on: **http://localhost:8000**

## 📚 View API Documentation

Visit: **http://localhost:8000/docs**

Swagger UI provides interactive testing of all endpoints.

## 🏌️ Get a Recommendation

### Via curl:
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "shot_001",
    "player_id": "joe_kramer_001",
    "hole_id": "pebble_7",
    "weather_condition_id": "weather_001",
    "pin_location": "front",
    "current_distance_to_pin_yards": 110,
    "player_lie": "fairway",
    "lie_quality": "clean",
    "pin_placement_strategy": "conservative"
  }'
```

### Via Swagger (Recommended)
1. Go to http://localhost:8000/docs
2. Find "Recommendations" section
3. Click "POST /api/v1/recommendations"
4. Click "Try it out"
5. Fill in the JSON and click "Execute"

## 📊 Understanding the Response

### Primary Recommendation
```json
"primary_recommendation": {
  "club": "sand_wedge",              // Recommended club
  "target_area": "Aim center, front", // Where to aim
  "expected_carry_yards": 99,         // Carry distance adjusted for conditions
  "expected_total_yards": 101,        // Carry + roll
  "confidence_percent": 95            // How confident the system is
}
```

### Adjustment Summary
Shows all physics adjustments:
```json
"adjustment_summary": {
  "temperature_adjustment_yards": 0,
  "elevation_adjustment_yards": 19,   // Based on course elevation
  "wind_adjustment_yards": 0,
  "rain_adjustment_percent": 0.0,
  "lie_adjustment_percent": 0.0,
  "human_readable_summary": [
    "+19 yards for elevation"
  ]
}
```

### Hazard Analysis
Identifies dangers:
```json
"hazard_analysis": {
  "hazards_in_play": [
    {
      "hazard_type": "bunker",
      "location": "right",
      "distance_from_tee": 105,
      "risk_level": "medium"
    }
  ],
  "safe_miss_direction": "center"    // Where to miss if needed
}
```

### Alternatives
Other clubs if strategically different:
```json
"alternative_clubs": [
  {
    "club": "gap_wedge",
    "confidence_percent": 90,
    "rationale": "More club for confidence"
  }
]
```

## 🧮 Physics Adjustments Applied

| Factor | Effect | Example |
|--------|--------|---------|
| **Temperature** | ±2 yards per 10°F | 90°F = +4 yards |
| **Elevation** | +0.116% per foot | 5,000 ft = +6% |
| **Wind** | ±3-5% depending on direction | Headwind = -4% |
| **Rain** | -3-5% reduction | Rain = -5% |
| **Lie** | -5% to -35% penalty | Rough = -15% |

## 📋 Request Fields Explained

| Field | Options | Notes |
|-------|---------|-------|
| `pin_location` | front / center / back | Pin position on green |
| `player_lie` | tee / fairway / rough / bunker / woods / semi_rough | Where ball currently sits |
| `lie_quality` | clean / normal / thick / plugged | Optional, affects distance |
| `pin_placement_strategy` | aggressive / balanced / conservative | How aggressive to play |
| `wind_relative_to_shot` | headwind / tailwind / crosswind_left / crosswind_right / calm | Optional - system calculates if not provided |

## 🧪 Test Scenarios

### Test 1: Standard Conditions
```bash
pin_location: "front"
current_distance_to_pin_yards: 110
player_lie: "fairway"
pin_placement_strategy: "conservative"
```
Expected: Sand wedge or pitching wedge, 90-110 yards

### Test 2: Rough Lie
```bash
player_lie: "rough"
lie_quality: "thick"
```
Expected: Shorter distance recommendation due to lie penalty

### Test 3: Aggressive Strategy
```bash
pin_placement_strategy: "aggressive"
```
Expected: Longer club for distance match, accepts more hazard risk

## 🔧 Modifying Test Data

### Sample Player (`examples/sample_player_baseline.json`)
Edit club distances to customize player:
```json
"club_type": "driver",
"carry_distance": 220,
"total_distance": 235
```

### Sample Course (`examples/sample_course.json`)
Add more holes or modify existing ones:
```json
{
  "hole_id": "pebble_1",
  "hole_number": 1,
  "par": 4,
  "distance_to_pin_yards": 375,
  "shot_bearing_degrees": 45,
  "hazards": [...]
}
```

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -f "python main.py"

# Try different port
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### Conda environment issues
```bash
# List environments
conda env list

# Activate environment
conda activate personal-caddie

# If not found, recreate it
conda create -n personal-caddie python=3.11
conda activate personal-caddie
pip install -r requirements.txt
```

### Module not found errors
```bash
# Ensure you're in the backend directory
cd /Users/joekramer/personal-caddie/backend

# Check that services.py exists
ls -la services.py

# Reinstall dependencies
pip install -r requirements.txt
```

## 📈 Next Steps

### Phase 2: Database Integration
- Store player baselines in PostgreSQL
- Store course/weather data persistently
- Track recommendation history

### Phase 3: Learning
- Compare recommendations vs actual results
- Improve confidence scoring over time
- Detect player improvement

### Phase 4: Frontend
- Build web UI for recommendation requests
- Display recommendations visually
- Track shot history

## 📚 Learn More

- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Development Guide**: See `DEVELOPMENT.md`
- **Data Contracts**: See `contracts/README.md`
- **Plan**: See `.claude/plans/steady-spinning-clover.md`

## 🎯 Key Files

```
personal-caddie/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py            # Pydantic models
│   ├── services.py          # Recommendation engine ✨
│   └── requirements.txt
├── contracts/               # Data model definitions
├── examples/               # Test data
├── QUICK_START.md          # This file
├── IMPLEMENTATION_SUMMARY.md
├── DEVELOPMENT.md
└── README.md
```

## ✅ You're Ready!

The recommendation engine is production-ready. Start the server and visit the API docs to try it out.

**Questions?** Check the documentation files or examine the code - it's well-commented!
