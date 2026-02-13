# Personal Caddie Backend Tools

## Overview

This directory contains tools for managing and enriching golf course data.

## Tools

### 1. OSM Hole Mapper (`osm_hole_mapper.py`)

Queries OpenStreetMap (OSM) for golf course features and attempts to infer tee/green positions.

**⚠️ IMPORTANT COVERAGE WARNING:**
OSM golf data is extremely sparse. Most courses only have basic outlines, not individual tee/green positions. This tool is best-effort with typically very low success rates. For famous courses, manual curation is strongly recommended.

**Usage:**
```bash
python osm_hole_mapper.py --name "Course Name" --lat 36.5750 --lng -121.9445
python osm_hole_mapper.py --name "Course Name" --lat 36.5750 --lng -121.9445 --output results.json
```

**Features:**
- Queries Overpass API for golf features (tees, greens, fairways, bunkers, etc.)
- Attempts hole mapping via:
  1. OSM ref tags (hole numbers) if available
  2. Proximity-based chaining (low confidence)
- Outputs confidence scores for each mapping
- Exports results to JSON

**Example:**
```bash
python osm_hole_mapper.py --name "Pebble Beach" --lat 36.5668 --lng -121.9487 --radius 1.5
```

### 2. Hole Validator (`validate_holes.py`)

Validates course JSON files for completeness and correctness.

**Usage:**
```bash
# Validate all courses
python validate_holes.py --all

# Validate specific file(s)
python validate_holes.py ../examples/augusta_national.json

# Summary mode for many courses
python validate_holes.py --all --summary
```

**Checks:**
- All courses have 18 holes (or flags incomplete)
- No duplicate hole numbers
- Hole numbers are 1-18
- Par values are 3-5
- Handicap indices are 1-18
- Distance values are reasonable (50-700 yards)
- Tee/green coordinates are within course bounding box
- GPS-calculated distance matches stated yardage (±20% tolerance)
- All lat/lng values are valid

**Output:**
- ERROR: Must be fixed (malformed data)
- WARNING: Should be reviewed (missing holes, GPS mismatches)
- INFO: Informational notes

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Course Data Coverage (as of 2026-02-13)

### Fully Curated Famous Courses (18 holes + GPS)
- ✅ **Augusta National Golf Club** - 18 holes, 18 with GPS
- ✅ **TPC Sawgrass Stadium Course** - 18 holes, 18 with GPS
- ✅ **St Andrews Old Course** - 18 holes, 18 with GPS
- ✅ **Pebble Beach Golf Links** - 18 holes, 18 with GPS

### Complete Courses (18 holes, no GPS)
- Rocky River Golf Club
- Eagle Chase Golf Club
- Skybrook Golf Club
- Warrior Golf Club
- Sunset Hills Golf Course

### Incomplete Courses (signature holes only)
Most other famous courses in the examples/ directory have 3-9 signature holes documented but need expansion to full 18 holes.

## Future Enhancements

1. **Automated GPS Refinement**: Use Google Maps API or similar to programmatically fetch precise tee/green coordinates
2. **Elevation Data Integration**: Query elevation APIs to populate elevation_change_feet
3. **Hazard Detection**: Use satellite imagery analysis to auto-detect water hazards, bunkers
4. **Hole Geometry**: Calculate shot_bearing_degrees from tee→green vector automatically
5. **Course Database**: Migrate from JSON files to proper database with spatial queries

## Notes

- GPS coordinates are approximate, manually curated from satellite imagery
- Handicap indices sourced from course scorecards where available
- Distance measurements are from championship tees unless noted
- All distances in yards, elevations in feet
