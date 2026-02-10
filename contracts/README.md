# Semantic Data Contracts

This directory contains the semantic contracts that define the Personal Caddie system's data model. Each contract is a JSON Schema that documents not just the structure of data, but also the business meaning, relationships, physics, and validation rules.

## Contract Files

### 1. **clubs.json**
Golf club specifications and baseline performance characteristics.
- **What**: Defines 15 club types (driver through lob wedge)
- **Baseline**: Sea level, 70°F, calm wind, dry fairway, amateur golfer (~90mph driver swing speed)
- **Fields**: Club type, loft angle, carry distance, total distance, accuracy margin
- **Ownership**: System
- **Update frequency**: As new club technology emerges

### 2. **player_baseline.json**
Player's personal club distances and characteristics.
- **What**: Customizes generic club specs to individual player abilities
- **Why**: Each player hits clubs different distances based on swing speed and technique
- **Fields**: Club distances (carry + total), measurement method, miss patterns
- **Ownership**: Player
- **Update frequency**: Every few months as player improves

### 3. **course_holes.json**
Hole-specific layout and characteristics for each hole on a golf course.
- **What**: Static course information for all 18 holes
- **Fields**: Distance, par, handicap index, shot bearing, hazards, green shape
- **Ownership**: Course Management
- **Note**: Shot bearing (compass direction) is critical - caddie uses this to calculate wind relative to shot
- **Future**: Per-hole elevation change requires golf simulator database integration

### 4. **weather_conditions.json**
Real-time environmental conditions that modify distance and trajectory.
- **What**: Snapshot of weather at time of shot
- **Physics applied**:
  - Temperature: ~2 yards per 10°F from baseline 70°F
  - Wind: Calculated relative to shot bearing (headwind reduces, tailwind increases)
  - Elevation: +0.116% distance per foot above sea level
  - Rain/wet: 3-5% distance reduction
  - Humidity: Negligible impact (<1 yard)
- **Ownership**: Weather Data Provider
- **Update frequency**: Real-time

### 5. **shot_analysis.json**
Input data for caddie recommendation engine.
- **What**: Real-time information about current shot situation
- **Provided by**: Player/GPS device
- **Fields**: Distance to pin, lie, pin location, wind relative to shot, strategy preference
- **Critical field**: `wind_relative_to_shot` - caddie calculates this from weather + hole bearing

### 6. **caddie_recommendation.json**
Output of recommendation engine - suggested club, target area, and strategy.
- **What**: The caddie's recommendation
- **Primary output**: Club + target area (not just "aim at flag")
- **Supporting data**:
  - Confidence level
  - Expected distances with adjustments
  - Adjustment breakdown (temp, wind, elevation, etc.)
  - Alternative clubs with rationale
  - Hazard analysis
  - Safe miss direction
- **Philosophy**: Provide WHY, not just WHAT

## Design Principles

### 1. **Structure + Semantics**
Each field has:
- Type and validation rules (structure)
- Business meaning and physics (semantics)
- Ownership and update frequency
- Examples where helpful

### 2. **Physics-Driven**
Adjustments are documented with the physics behind them:
- Temperature: Affects ball and club performance
- Wind: Calculated relative to shot, not compass
- Elevation: Affects air density
- Rain: Affects ball contact and fairway roll

### 3. **Real-World Pragmatism**
- Player baseline distances measured/estimated by player
- Course data captures what's practically available
- Weather data from standard sources
- Recommendations include confidence level (accounts for uncertainty)

### 4. **Course Management > Yardage**
The caddie doesn't just say "hit a 6-iron". It says:
- Which club
- Where to aim
- Why (hazards, pin position, risk/reward)
- What to avoid
- Confidence level

## Usage in Backend

The backend will:
1. Load these contracts as Pydantic models
2. Validate incoming data against contracts
3. Use contract semantics to calculate adjustments
4. Generate recommendations per caddie_recommendation contract

## Future Enhancements

- **Pin placement rotation**: Map pin positions (1, 2, 3) to dates for visualization
- **Hole-by-hole elevation**: Integrate golf simulator data for undulation
- **Player profile evolution**: Track performance over time
- **Psychological state**: Add player confidence/momentum tracking
- **Yardage book integration**: Connect to course maps and visualizations

## Philosophy

These contracts are the "API" between the golf domain and the software system. They encode expert knowledge about:
- How golf works (physics)
- What matters for decision-making (course management)
- What the caddie needs to know (player, course, weather)
- What the caddie should communicate (clear, decisive recommendations)
