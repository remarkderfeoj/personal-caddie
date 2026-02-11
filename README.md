# Personal Caddie ⛳

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-latest-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

> An AI-powered caddie system that provides intelligent golf shot recommendations based on physics, course conditions, and strategy.

## 🎯 What It Does

Personal Caddie analyzes real-time conditions and recommends the optimal club for any shot, just like a professional caddie. It combines:

- **Physics-based calculations**: Temperature, elevation, wind, rain adjustments
- **Course management**: Hazard awareness, risk/reward analysis, optimal miss directions
- **Strategic planning**: Aggressive vs. conservative shot selection
- **Real-time analysis**: Instant recommendations with confidence levels

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
git clone https://github.com/remarkderfeoj/personal-caddie.git
cd personal-caddie/backend
pip install -r requirements.txt
```

### Start the Server

```bash
python main.py
```

API will be available at **http://localhost:8000**

Interactive docs at **http://localhost:8000/docs** (Swagger UI)

### Get Your First Recommendation

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

**Response:**
```json
{
  "primary_recommendation": {
    "club": "sand_wedge",
    "target_area": "Aim center, front pin position",
    "expected_carry_yards": 99,
    "expected_total_yards": 101,
    "confidence_percent": 95
  },
  "adjustment_summary": {
    "elevation_adjustment_yards": 19,
    "human_readable_summary": ["+19 yards for elevation"]
  },
  "alternative_clubs": [
    {
      "club": "gap_wedge",
      "confidence_percent": 90,
      "rationale": "More club for confidence"
    }
  ],
  "hazard_analysis": {
    "hazards_in_play": [
      {
        "hazard_type": "bunker",
        "location": "right",
        "risk_level": "medium"
      }
    ],
    "safe_miss_direction": "center"
  }
}
```

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Development Guide](DEVELOPMENT.md)** - Architecture, design decisions, and future plans
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical deep dive into the physics engine
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI (when server is running)

## 🎓 Key Features

### Physics Engine

| Factor | Effect | Example |
|--------|--------|---------|
| **Temperature** | ±2 yards per 10°F from 70°F | 90°F = +4 yards |
| **Elevation** | +0.116% per foot above sea level | 5,000 ft = +6% distance |
| **Wind** | Headwind -4%, Tailwind +4% | 15mph headwind = -6 yards |
| **Rain/Wet** | -3% to -5% reduction | Wet conditions = -4 yards |
| **Lie Quality** | -5% to -35% penalty | Thick rough = -15% |

### Smart Hazard Analysis
- Identifies hazards in play based on shot dispersion
- Recommends safe miss directions
- Risk assessment (high/medium/low)
- Strategic layup suggestions

### Strategic Planning
- **Conservative**: Prioritize safety, avoid hazards
- **Balanced**: Optimal risk/reward trade-off
- **Aggressive**: Attack pins, accept more risk

### Confidence Scoring
Each recommendation includes a confidence percentage based on:
- Distance accuracy (how well the club matches target)
- Hazard proximity
- Lie conditions
- Weather uncertainty

## 🏗️ Project Structure

```
personal-caddie/
├── README.md                          # This file
├── QUICK_START.md                     # Getting started guide
├── DEVELOPMENT.md                     # Developer documentation
├── IMPLEMENTATION_SUMMARY.md          # Technical deep dive
├── contracts/                         # Semantic data contracts (JSON Schema)
│   ├── clubs.json
│   ├── course_holes.json
│   ├── weather_conditions.json
│   ├── player_baseline.json
│   ├── shot_analysis.json
│   └── caddie_recommendation.json
├── backend/                           # FastAPI server
│   ├── main.py                       # API endpoints
│   ├── models.py                     # Pydantic models from contracts
│   ├── services.py                   # ⭐ Recommendation engine (500+ lines)
│   └── requirements.txt
├── frontend/                          # React/TypeScript UI (Phase 2)
└── examples/                          # Test data
    ├── sample_player_baseline.json   # Joe Kramer baseline
    ├── sample_course.json            # Pebble Beach holes
    └── sample_scenarios.json
```

## 🔧 Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Frontend**: React, TypeScript *(Phase 2)*
- **Database**: PostgreSQL *(Phase 2)*
- **Documentation**: Semantic contracts as JSON Schema

## 🗺️ Roadmap

### Phase 1 (MVP) - ✅ Complete
- [x] Semantic contracts for golf domain
- [x] FastAPI backend with recommendation engine
- [x] Physics-based distance adjustments
- [x] Course management & hazard awareness
- [x] Player baseline distance entry
- [x] Wind calculations (compass to shot-relative)
- [x] Strategic planning (aggressive/balanced/conservative)

### Phase 2 (In Progress)
- [ ] React frontend dashboard
- [ ] PostgreSQL integration
- [ ] Player profile tracking & learning
- [ ] Real weather API integration
- [ ] Shot history and analytics

### Phase 3 (Future)
- [ ] Mobile app (iOS/Android)
- [ ] GPS/rangefinder integration
- [ ] Yardage book integration
- [ ] Visualization & course mapping
- [ ] Tournament mode (multi-player)
- [ ] AI learning from actual shot results

## 🧪 Testing

### View Sample Data
```bash
# Sample player baseline
curl http://localhost:8000/api/v1/examples/sample-player

# Sample course data
curl http://localhost:8000/api/v1/examples/sample-course
```

### Test Scenarios

**Scenario 1: Standard Conditions**
```bash
# 110 yards from fairway, front pin, conservative strategy
# Expected: Sand wedge (99 yards carry)
```

**Scenario 2: Rough Lie**
```bash
# Same distance but thick rough
# Expected: Gap wedge to compensate for lie penalty
```

**Scenario 3: Aggressive Play**
```bash
# Aggressive pin placement strategy
# Expected: Longer club, accepting more hazard risk
```

See [QUICK_START.md](QUICK_START.md) for detailed test scenarios.

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python
- Use type hints
- Add docstrings to functions
- Update contracts when changing data models

### Areas for Contribution
- Additional courses and test data
- Frontend development (React/TypeScript)
- Database integration (PostgreSQL)
- Weather API integration
- Mobile app development
- Physics improvements (Magnus effect, spin, etc.)

## 📊 Semantic Contracts

All data structures are defined using semantic contracts in `contracts/`. These contracts document:
- **Structure**: Field names, types, ranges
- **Semantics**: Business meaning, relationships, ownership
- **Physics**: How environmental factors affect values
- **Quality**: Validation rules, constraints

Example contract (`contracts/clubs.json`):
```json
{
  "club_type": "sand_wedge",
  "carry_distance": 80,
  "total_distance": 82,
  "typical_dispersion_yards": 5
}
```

See `contracts/README.md` for detailed contract documentation.

## 🐛 Troubleshooting

**Port already in use:**
```bash
uvicorn main:app --reload --port 8001
```

**Module not found:**
```bash
pip install -r requirements.txt
```

**Server won't start:**
```bash
# Check if process is running
lsof -i :8000

# Kill existing process
pkill -f "python main.py"
```

See [QUICK_START.md](QUICK_START.md#-troubleshooting) for more help.

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Physics formulas based on PGA Tour data and atmospheric physics
- Course management principles from professional caddie experience
- Built with FastAPI and Pydantic for modern Python development

## 📫 Contact

Questions? Open an issue or reach out to the maintainers.

---

**Status**: ✅ Production-ready MVP  
**API**: http://localhost:8000  
**Docs**: http://localhost:8000/docs  
**Next Phase**: Database integration & frontend UI
