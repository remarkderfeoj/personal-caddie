# Personal Caddie

An AI-powered caddie system that provides intelligent golf shot recommendations based on physics, course conditions, and strategy.

## Project Overview

Personal Caddie uses semantic data contracts to define golf course conditions, club specifications, and player baselines. The system analyzes real-time environmental factors and hole characteristics to recommend optimal club selection and shot strategy.

### Key Features

- **Physics-based calculations**: Temperature, elevation, wind, rain adjustments
- **Course management**: Hazard awareness, risk/reward analysis, optimal miss directions
- **Baseline club distances**: Player inputs baseline distances for each club
- **Real-time recommendations**: Suggests primary club + alternatives with rationale

## Project Structure

```
personal-caddie/
├── README.md
├── contracts/                 # Semantic data contracts (JSON Schema)
│   ├── clubs.json
│   ├── course_holes.json
│   ├── weather_conditions.json
│   ├── player_baseline.json
│   ├── shot_analysis.json
│   └── caddie_recommendation.json
├── backend/                   # FastAPI server
│   ├── main.py
│   ├── models.py             # Pydantic models from contracts
│   ├── services.py           # Business logic (recommendations, physics)
│   └── requirements.txt
├── frontend/                  # React/TypeScript UI (Phase 2)
└── examples/                  # Test data & example flows
    ├── augusta_national.json  # Course data
    └── sample_scenarios.json
```

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, TypeScript (Phase 2)
- **Database**: PostgreSQL (Phase 2)
- **Documentation**: Semantic contracts as JSON Schema

## Development Phases

**Phase 1 (MVP)**
- Semantic contracts for golf domain
- FastAPI backend with recommendation engine
- Physics-based distance adjustments
- Course management & hazard awareness
- Player baseline distance entry

**Phase 2 (Future)**
- React frontend dashboard
- PostgreSQL integration
- Player profile tracking & learning
- Yardage book integration
- Visualization & course mapping

## Getting Started

(Instructions coming soon)

## Semantic Contracts

All data structures are defined using semantic contracts in `contracts/`. These contracts document:
- **Structure**: Field names, types, ranges
- **Semantics**: Business meaning, relationships, ownership
- **Physics**: How environmental factors affect values
- **Quality**: Validation rules, constraints

See `contracts/README.md` for detailed contract documentation.
