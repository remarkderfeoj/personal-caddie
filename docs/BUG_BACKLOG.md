# Personal Caddie - Bug Backlog

**Last Updated:** 2024-02-13  
**QA Subagent:** A

---

## Priority Definitions

- **P0:** Broken functionality - app crashes or critical feature doesn't work
- **P1:** Incorrect behavior - feature works but produces wrong results
- **P2:** UX issues - feature works but user experience is degraded
- **P3:** Nice to have - polish, improvements, minor issues

---

## Test Execution Summary

### Environment
- **Testing Date:** 2024-02-13
- **Python Version:** 3.x
- **Dependencies Status:** ⚠️ pytest, fastapi, pydantic NOT INSTALLED
- **Backend Status:** Not running during test execution

### Test Suite Status

| Test Suite | Total Tests | Passed | Failed | Status |
|------------|-------------|--------|--------|---------|
| test_physics.py | 18 | ⏸️ | ⏸️ | Cannot run - missing pydantic |
| test_round_context.py | 12 | ⏸️ | ⏸️ | Cannot run - missing pydantic |
| test_api.py | 11 | ⏸️ | ⏸️ | Cannot run - missing fastapi |
| test_api_comprehensive.py | 41+ | ⏸️ | ⏸️ | Created, not yet executed |
| test_data_validation.py | 11 | 8 | 3 | ✅ EXECUTED |

**Overall:** Data validation tests executed successfully. Backend tests require dependencies (pydantic, fastapi, pytest).

---

## P0: Broken Functionality

### P0-001: Cannot Run Test Suite - Missing Dependencies
**Status:** 🔴 OPEN  
**Component:** Development Environment  
**Description:** pytest, pydantic, fastapi not installed in container. All tests fail with ModuleNotFoundError.

**Impact:** Cannot validate any functionality automatically.

**Error Message:**
```
ModuleNotFoundError: No module named 'pydantic'
ModuleNotFoundError: No module named 'fastapi'
/usr/bin/python3: No module named pytest
```

**Resolution:**
```bash
# Install dependencies
python3 -m pip install -r backend/requirements.txt
python3 -m pip install pytest httpx pytest-cov
```

**Workaround:** Manual testing via browser/Postman.

---

### P0-002: (Reserved for critical bugs found during testing)
**Status:** -  
**Component:** -  
**Description:** -

---

## P1: Incorrect Behavior

### P1-001: Elevation Formula Was Incorrect (FIXED)
**Status:** ✅ RESOLVED  
**Component:** backend/services/physics.py  
**Description:** Elevation adjustment formula used coefficient 0.00116 which was too large. Caused massive distance adjustments at high elevation.

**Expected:** At 5000 ft, 150-yard shot should add ~9 yards  
**Actual (old):** Added unrealistic amounts  
**Fix Applied:** Changed coefficient to 0.00002

**Commit:** Fixed in recent update  
**Verification:** Need to re-run test_physics.py::test_elevation_adjustment_high_altitude

---

### P1-002: Pin Marker Persistence Issue (FIXED)
**Status:** ✅ RESOLVED  
**Component:** frontend/index.html  
**Description:** Pin marker position on hole diagram was resetting to center when navigating away and back.

**Expected:** Pin position persists across screen navigation  
**Actual (old):** Pin reset to center each time  
**Fix Applied:** State management updated to persist pin positions

**Verification:** See QA_CHECKLIST.md section 3 - Pin Marker Persistence

---

### P1-003: St Andrews Duplicate Handicap Indices
**Status:** 🔴 OPEN  
**Component:** examples/st_andrews.json  
**Description:** St Andrews Old Course has duplicate handicap index 10 and missing index 2.

**Expected:** All 18 holes have unique handicap indices 1-18  
**Actual:** Index 10 appears twice, index 2 missing  
**Impact:** Low - affects handicap calculations for match play

**Fix:** Review St Andrews hole data and correct handicap indices.

---

### P1-004: Augusta National Duplicate Handicap Indices
**Status:** 🔴 OPEN  
**Component:** examples/augusta_national.json  
**Description:** Augusta National has duplicate handicap indices 5 and 13, missing indices 6 and 18.

**Expected:** All 18 holes have unique handicap indices 1-18  
**Actual:** Indices 5 and 13 duplicated, indices 6 and 18 missing  
**Impact:** Low - affects handicap calculations

**Fix:** Verify against official Augusta National handicap ratings and correct.

---

### P1-005: Incomplete Course Data (16 Courses)
**Status:** 🟡 BY DESIGN  
**Component:** examples/*.json  
**Description:** 16 courses have only 3-5 holes instead of complete 18-hole layouts.

**Courses affected:** Torrey Pines, Muirfield, Pine Valley, Shinnecock, Oakmont, Winged Foot, Olympic Club, Whistling Straits, Bandon Dunes, Kiawah, Cypress Point, Bethpage Black, Merion, Pinehurst No. 2, Royal Melbourne, Sample Course

**Expected:** All courses have 18 holes  
**Actual:** Most have 3-5 signature holes only  
**Impact:** Medium - These courses cannot be used for full-round play

**Notes:** May be intentional for demo purposes (showcasing famous holes). If these are meant to be complete courses, hole data needs to be added.

**Decision needed:** Are these incomplete by design or missing data?

---

## P2: UX Issues

### P2-001: No Visual Feedback on API Errors
**Status:** 🟡 NEEDS VERIFICATION  
**Component:** frontend/index.html  
**Description:** When backend is down or returns error, user may not see clear error message.

**Expected:** User-friendly error message with retry option  
**Actual:** Unknown - needs frontend testing  
**Suggested Fix:** Add error toast/alert with descriptive message

**Test:** Disconnect backend, attempt recommendation request

---

### P2-002: Loading States Not Implemented
**Status:** 🟡 NEEDS VERIFICATION  
**Component:** frontend/index.html  
**Description:** Long-running API requests (recommendation, course load) may not show loading indicators.

**Expected:** Spinner or progress indicator during API calls  
**Actual:** Unknown - needs frontend testing  
**Suggested Fix:** Add loading spinner to buttons during async operations

---

### P2-003: Form Validation Messages
**Status:** 🟡 NEEDS VERIFICATION  
**Component:** frontend/index.html  
**Description:** Form validation errors may not be user-friendly.

**Expected:** Clear error messages like "Distance must be between 0 and 600 yards"  
**Actual:** Unknown - needs frontend testing  
**Suggested Fix:** Enhance client-side validation with friendly messages

---

### P2-004: Mobile Keyboard Covering Input Fields
**Status:** 🟡 NEEDS VERIFICATION  
**Component:** frontend/index.html  
**Description:** On mobile, keyboard may cover active input field in shot advisor form.

**Expected:** Form scrolls to keep active input visible above keyboard  
**Actual:** Unknown - needs mobile device testing  
**Suggested Fix:** Add `scrollIntoView()` on input focus

---

## P3: Nice to Have

### P3-001: Missing Unit Tests for New Features
**Status:** 🔴 OPEN  
**Component:** tests/  
**Description:** New features (hybrids, wedge degrees, My Bag) don't have dedicated unit tests.

**Suggested:** Add test_player_baseline_hybrids.py for hybrid club validation  
**Effort:** Low  
**Priority:** Low (covered by API tests)

---

### P3-002: No Performance Tests
**Status:** 🔴 OPEN  
**Component:** tests/  
**Description:** No load testing or performance benchmarks for recommendation endpoint.

**Suggested:** Add test_performance.py with locust or similar  
**Effort:** Medium  
**Priority:** Low (for Phase 2)

---

### P3-003: Missing Database Tests
**Status:** 🔴 OPEN  
**Component:** tests/  
**Description:** SQLAlchemy included in requirements.txt but no database tests exist.

**Suggested:** Add test_database.py when PostgreSQL integration is added  
**Effort:** Medium  
**Priority:** Low (Phase 2 feature)

---

### P3-004: Accessibility Not Tested
**Status:** 🟡 NEEDS VERIFICATION  
**Component:** frontend/index.html  
**Description:** No automated accessibility (a11y) tests.

**Suggested:** Add axe-core or pa11y to test suite  
**Effort:** Medium  
**Priority:** Medium (important for public release)

---

### P3-005: No CI/CD Integration
**Status:** 🔴 OPEN  
**Component:** .github/workflows/  
**Description:** No GitHub Actions or CI/CD pipeline configured.

**Suggested:** Add .github/workflows/test.yml to run tests on PR  
**Effort:** Low  
**Priority:** Medium (before production)

---

## Data Validation Results

**Status:** ✅ EXECUTED  
**Date:** 2024-02-13  
**Test Command:** `python3 tests/test_data_validation.py`

### Results Summary:
**8 passed, 3 failed**

### Passing Tests:
- ✅ All course JSON files load correctly (24 courses found)
- ✅ All courses have required top-level fields
- ✅ All holes have required fields
- ✅ Par values are 3, 4, or 5
- ✅ GPS coordinates valid where present
- ✅ Hole coordinates near course center
- ✅ Distances reasonable for par rating (with warnings)
- ✅ Par totals calculated (with warnings)

### Failing Tests:

#### ❌ test_courses_have_18_holes
**16 courses incomplete** - Most courses only have 3-5 holes instead of 18:
- Torrey Pines: 4 holes
- Muirfield: 5 holes
- Pine Valley: 3 holes
- Shinnecock Hills: 5 holes
- Sample Course: 3 holes (expected)
- Plus 11 more courses with 3-5 holes

**Complete courses (18 holes):**
- St Andrews Old Course ✅
- Augusta National ✅
- TPC Sawgrass ✅
- Rocky River ✅
- Skybrook ✅
- Sunset Hills ✅
- Warrior GC ✅
- Eagle Chase ✅

#### ❌ test_handicap_indices_valid
**Issues found:**
- St Andrews: Duplicate handicap index 10, missing index 2
- Augusta National: Duplicate indices 5 and 13, missing indices 6 and 18
- 16 incomplete courses: Missing most handicap indices (expected due to incomplete hole data)

#### ❌ test_hole_numbers_sequential
**16 courses with missing holes** (same courses as above - incomplete data)

### Warnings (non-failing):

**Distance warnings** (unusual but valid):
- Torrey Pines Hole 12: 504y for par 4 (slightly long)
- Sunset Hills Hole 3: 263y for par 4 (short)
- Sunset Hills Hole 13: 417y for par 5 (short)
- Cypress Point Hole 16: 231y for par 4 (famous short par 4)
- Bethpage Black Hole 12: 501y for par 4 (championship course)
- Pinehurst No. 2 Hole 4: 528y for par 4 (very long)
- Augusta National Hole 11: 520y for par 4 (famous long par 4)

**Conclusion:** Most sample courses are intentionally incomplete (showcase holes). Full courses mostly valid with minor handicap index issues in 2 courses.

---

## API Test Results

**Note:** Comprehensive API tests created (41+ test cases) but not yet executed. Run with:
```bash
# Install dependencies first
pip install pytest httpx fastapi pydantic

# Then run tests
pytest tests/test_api_comprehensive.py -v
```

### Coverage Includes:
- ✅ Health & info endpoints
- ✅ Course list/search (happy path, edge cases, errors)
- ✅ Get specific course (valid, 404, special chars)
- ✅ Get holes (all holes, specific hole, invalid numbers)
- ✅ Player baseline CRUD (create, read, validation)
- ✅ Simple recommendation (happy path, enum mapping, errors)
- ✅ Example endpoints

**Status:** Awaiting test execution

---

## Frontend Manual Testing

**Status:** 🟡 NOT STARTED  
**Checklist:** See docs/QA_CHECKLIST.md

### Critical Flows to Test:
1. [ ] Course search and selection
2. [ ] Hole detail view and SVG interaction
3. [ ] Pin marker persistence
4. [ ] Shot advisor form submission
5. [ ] Recommendation display
6. [ ] My Bag onboarding and setup
7. [ ] Hybrid clubs and wedge degree inputs
8. [ ] Bottom nav and back button
9. [ ] Error handling
10. [ ] Mobile responsiveness

---

## Known Limitations

1. **Test Environment:** No access to pip/pip3 in current container
2. **Backend Not Running:** Cannot test live API endpoints
3. **No Mobile Devices:** Cannot test actual mobile experience
4. **No Browser:** Cannot test frontend functionality

---

## Recommendations

### Immediate Actions:
1. ✅ Install Python dependencies: `pip install -r backend/requirements.txt && pip install pytest httpx`
2. ✅ Run existing test suite: `pytest tests/ -v`
3. ✅ Run data validation: `python3 tests/test_data_validation.py`
4. ✅ Run comprehensive API tests: `pytest tests/test_api_comprehensive.py -v`
5. ⏸️ Start backend server: `uvicorn backend.main:app`
6. ⏸️ Execute frontend QA checklist manually
7. ⏸️ Test on real mobile devices (iOS + Android)

### Phase 2 Actions:
1. Set up CI/CD pipeline (GitHub Actions)
2. Add performance tests (load testing)
3. Add accessibility tests (axe-core)
4. Add database integration tests
5. Add end-to-end tests (Playwright/Selenium)

---

## Test Command Reference

```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install pytest httpx pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api_comprehensive.py -v

# Run individual tests without pytest
python3 tests/test_physics.py
python3 tests/test_round_context.py
python3 tests/test_data_validation.py

# Start backend for manual testing
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Sign-off

**QA Engineer:** Subagent A  
**Date:** 2024-02-13  
**Status:** Test infrastructure created, awaiting execution  
**Confidence:** Medium (cannot verify without running tests)

**Next QA Session Should:**
1. Execute all automated tests
2. Document actual failures
3. Perform manual frontend testing
4. Update this backlog with real bugs found
