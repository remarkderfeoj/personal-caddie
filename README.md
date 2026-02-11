# ⛳️ Personal Caddie

**Your AI golf caddie in your pocket.**

Smart club selection and shot strategy based on:
- Real physics (wind, elevation, lie conditions)
- Player learning (your actual distances and tendencies)
- Course intelligence (hazards, optimal lines)
- Round momentum (confidence, fatigue, scoring position)

---

## 🚀 Quick Start

### Use the Web App (Easiest)

1. **Deploy to Railway** (5 minutes - see [DEPLOY.md](DEPLOY.md))
2. **Open on your phone**: `https://your-app.railway.app/app`
3. **Save to home screen** for app-like experience
4. **Play golf!** 🏌️

### Run Locally

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start server
cd backend
python3 main.py

# Open in browser
# http://localhost:8000/app
```

---

## 📱 Features

### Current (v0.1)
- **Conviction-first recommendations** - One decisive club call, not a menu
- **Physics-based adjustments** - Wind, elevation, lie, temperature
- **Mobile-optimized web UI** - Works great on phone browsers
- **Famous courses pre-loaded** - Augusta, St Andrews, Pine Valley, Cypress Point

### Coming Soon
- **Player learning** - Adapts to YOUR game over time
- **Shot tracking** - Learn from every round
- **Round awareness** - Adjusts for momentum and fatigue
- **Custom courses** - Add any course you play
- **Strokes gained analytics** - See where to improve

---

## 🏗️ Architecture

**Backend:**
- FastAPI (Python)
- Pydantic models + JSON Schema contracts
- In-memory data (PostgreSQL migration ready)
- Rate limiting + input validation

**Frontend:**
- Single-page HTML app
- Mobile-first design
- No dependencies, just vanilla JS

**Data:**
- Courses: JSON files in `backend/data/`
- Players: JSON files (or PostgreSQL)
- Physics models: Deterministic calculations

---

## 📚 Documentation

- [DEPLOY.md](DEPLOY.md) - Deployment guide
- [docs/API.md](docs/API.md) - Full API documentation
- [docs/POSTGRES_MIGRATION.md](docs/POSTGRES_MIGRATION.md) - Database setup

---

## 🛠️ Development

```bash
# Run tests
pytest tests/

# Or individual test files
python3 tests/test_physics.py
python3 tests/test_round_context.py
python3 tests/test_api.py
```

**Key modules:**
- `backend/services/physics.py` - Wind/elevation calculations
- `backend/services/recommendation.py` - Caddie logic
- `backend/services/player_model.py` - Learning system
- `backend/services/round_context.py` - Momentum/fatigue

---

## 🎯 Design Philosophy

Based on research of legendary caddies (Steve Williams, Bones Mackay):

1. **Memory** - Learn the player, not just the course
2. **Conviction** - One decisive call, not multiple options
3. **Feel** - Read the situation (pressure, momentum, fatigue)

---

## 📝 License

MIT License - Build whatever you want with this!

---

## 🤝 Contributing

Pull requests welcome! Especially:
- New course data
- Physics improvements
- Player learning algorithms
- Frontend enhancements

---

Built with ☕ by [Joe Kramer](https://github.com/remarkderfeoj)
