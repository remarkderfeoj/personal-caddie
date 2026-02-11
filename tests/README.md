# Personal Caddie Tests

## Overview

Comprehensive unit and integration tests for the Personal Caddie backend.

## Structure

- `test_physics.py` - Unit tests for physics calculations (temperature, elevation, wind, etc.)
- `test_round_context.py` - Unit tests for round context and emotional awareness
- `test_api.py` - Integration tests for API endpoints

## Running Tests

### Prerequisites

```bash
cd backend
pip install -r requirements.txt
```

### Run Individual Test Suites

```bash
# Physics tests
python3 tests/test_physics.py

# Round context tests
python3 tests/test_round_context.py

# API integration tests (requires httpx)
pip install httpx pytest
python3 tests/test_api.py
```

### Run All Tests with Pytest

```bash
pip install pytest httpx
pytest tests/
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html
```

## Test Coverage

### Unit Tests

**Physics (`test_physics.py`):**
- ✅ Temperature adjustments (hot, cold, baseline)
- ✅ Elevation effects
- ✅ Wind calculations (headwind, tailwind, crosswind)
- ✅ Rain/wet conditions
- ✅ Lie quality penalties
- ✅ Compass to degrees conversion
- ✅ Wind relative to shot calculation

**Round Context (`test_round_context.py`):**
- ✅ Momentum calculation (hot, steady, cold)
- ✅ Round phase detection (early, middle, closing)
- ✅ Strategy adjustments (conservative after blowup, aggressive when hot)
- ✅ Caddie note generation (context-aware messaging)

### Integration Tests

**API Endpoints (`test_api.py`):**
- ✅ Health check
- ✅ Root endpoint
- ✅ Course listing and search
- ✅ Player baseline CRUD
- ✅ 404 handling for missing resources
- ✅ Input validation (hole numbers, etc.)
- ✅ Rate limiting configuration

## Adding New Tests

1. Create test file: `tests/test_<module>.py`
2. Import module under test
3. Write test functions with descriptive names
4. Use assertions for validation
5. Run tests to verify

Example:

```python
def test_my_feature():
    """Test description"""
    result = my_function(input)
    assert result == expected, "Failure message"
```

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r backend/requirements.txt
    pip install pytest httpx pytest-cov
    pytest tests/ --cov=backend
```

## Future Tests

TODO:
- [ ] Player model tests (dispersion tracking, comfort ratings)
- [ ] Recommendation engine integration tests
- [ ] Security tests (sanitization, rate limiting exhaustion)
- [ ] Database repository tests (when PostgreSQL added)
- [ ] Load tests for recommendation endpoint

## Troubleshooting

**Import errors:**
- Ensure you're running from the project root
- Check sys.path modifications in test files

**Missing dependencies:**
```bash
pip install fastapi uvicorn pydantic httpx pytest
```

**Rate limit errors:**
- Tests may hit rate limits if run repeatedly
- Add delays between test runs or increase limits

## Notes

- Tests use sample data from `examples/` directory
- API tests use FastAPI TestClient (no server startup needed)
- Unit tests are fast (<1s), integration tests may take longer
- Coverage report available after running with `--cov`
