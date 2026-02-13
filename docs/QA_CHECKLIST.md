# Personal Caddie - Frontend QA Checklist

## Purpose
Manual testing checklist for the Personal Caddie web app frontend. Use this to ensure all user-facing features work correctly before release.

## Environment Setup
- [ ] App loads at `/app` endpoint
- [ ] No console errors on initial load
- [ ] Mobile viewport (375x667 minimum) displays correctly
- [ ] Backend API is running and accessible

---

## 1. Course Search & Filtering

### Course List View
- [ ] App starts on "Courses" tab (bottom nav)
- [ ] Search box is visible at top
- [ ] At least one course is displayed
- [ ] Each course card shows: name, elevation, hole count
- [ ] Course cards are tappable/clickable

### Search Functionality
- [ ] Type "pebble" → filters to Pebble Beach-related courses
- [ ] Type "augusta" → filters to Augusta National
- [ ] Type gibberish → shows "No courses found"
- [ ] Clear search → shows all courses again
- [ ] Search is case-insensitive
- [ ] Search works on both course name and location

### Edge Cases
- [ ] Empty search string shows all courses
- [ ] Special characters in search don't crash app
- [ ] Very long search string is handled gracefully

---

## 2. Course Detail View

### Navigation
- [ ] Tap any course card → navigates to course detail
- [ ] Course name displays at top
- [ ] Back button appears and works
- [ ] Elevation info is visible

### Hole Display
- [ ] All 18 holes are listed
- [ ] Holes show: number, par, distance, handicap
- [ ] Holes are in order 1-18
- [ ] Front 9 (1-9) and Back 9 (10-18) are distinguishable
- [ ] Hole cards are tappable

### Hole Details
- [ ] Tap hole 1 → shows hole detail view
- [ ] Hole number and par are correct
- [ ] Distance to pin is shown
- [ ] Fairway type is displayed
- [ ] Hazards are listed (if any)
- [ ] Notes/description appears (if available)

### Edge Cases
- [ ] Course with missing optional fields displays correctly
- [ ] Very long course names don't break layout
- [ ] Courses with unusual pars (e.g., all par 3s) display properly

---

## 3. Hole Selection & SVG Diagram

### Hole Detail View
- [ ] SVG diagram renders (green, fairway, tee box visible)
- [ ] Pin marker appears (red flag icon)
- [ ] Hazards are drawn (water = blue, bunkers = tan)
- [ ] Distance markers are shown
- [ ] Diagram is appropriately sized for viewport

### Tap-to-Set Position
- [ ] Tap fairway → updates "Your Position" indicator
- [ ] Tap anywhere on diagram → sets your current position
- [ ] Distance to pin updates after tap
- [ ] Pin position can be moved by tapping green
- [ ] Visual feedback when tapping (highlight, ripple, etc.)

### Pin Marker Persistence
- [ ] Set pin position on hole 1
- [ ] Navigate back to course detail
- [ ] Navigate to hole 2
- [ ] Navigate back to hole 1
- [ ] **Pin position is STILL SET (not reset to center)**
- [ ] Distance calculation reflects saved pin position

### Edge Cases
- [ ] Tap outside valid areas is handled gracefully
- [ ] Very fast taps don't cause errors
- [ ] Zoom/pan on SVG (if implemented) works smoothly

---

## 4. Shot Advisor Form

### Form Display
- [ ] "Get Recommendation" button is visible
- [ ] Form opens when button is tapped
- [ ] All input fields are present:
  - Distance to pin (numeric)
  - Lie selector (dropdown/buttons)
  - Wind speed (numeric)
  - Wind direction (selector)
  - Elevation change (numeric)

### Input Validation
- [ ] Distance accepts numbers only
- [ ] Distance rejects negative values
- [ ] Wind speed accepts 0-50 mph range
- [ ] Elevation accepts positive and negative values

### Lie Selection
- [ ] Lie options: Tee, Fairway, Rough, Sand/Bunker
- [ ] All options are selectable
- [ ] Selected option is visually highlighted
- [ ] Default selection is "Fairway"

### Wind Direction Selector
- [ ] Wind options visible: Calm, Headwind, Tailwind, Left-to-Right, Right-to-Left
- [ ] All directions are selectable
- [ ] Visual indicator shows selection
- [ ] Default is "Calm"
- [ ] Wind speed input is disabled when "Calm" is selected

### Form Submission
- [ ] "Get Advice" button submits form
- [ ] Loading indicator appears during request
- [ ] Button is disabled during request (prevent double-submit)
- [ ] Success: recommendation displays
- [ ] Error: shows user-friendly error message

---

## 5. Recommendation Display

### Recommendation Content
- [ ] Primary club displays clearly (e.g., "7 Iron")
- [ ] Target area/strategy is shown
- [ ] Adjusted distance appears (accounting for conditions)
- [ ] "Why" explanation is readable and makes sense
- [ ] Optimal miss direction is indicated
- [ ] Danger zones are highlighted
- [ ] Caddie note/tip is personal and contextual

### Confidence & Risk/Reward
- [ ] Confidence percentage displays (e.g., "85% confident")
- [ ] Risk/reward breakdown shows:
  - Aggressive upside
  - Aggressive downside
  - Conservative upside
  - Conservative downside

### Alternative Clubs
- [ ] Alternative club options are listed (if any)
- [ ] Each alternative shows: club, target, scenario
- [ ] Alternatives are selectable/expandable

### Edge Cases
- [ ] Very long text in recommendations wraps properly
- [ ] Recommendations for extreme conditions display correctly
- [ ] Handling when no suitable club is found

---

## 6. My Bag Onboarding Flow

### Access
- [ ] "My Bag" tab in bottom nav is accessible
- [ ] First time: shows onboarding/setup screen
- [ ] Returning users: shows saved clubs

### Preset Options
- [ ] Preset buttons: Beginner, Average, Advanced
- [ ] Tap "Average" → loads average distances
- [ ] Tap "Beginner" → loads shorter distances
- [ ] Tap "Advanced" → loads longer distances
- [ ] Preview of distances appears after selection

### Custom Club Entry
- [ ] "Custom" option is available
- [ ] List of all club types appears:
  - Driver, Woods (3, 5, 7)
  - Hybrids (2, 3, 4, 5, 6)
  - Irons (2-9)
  - Wedges (PW, GW, SW, LW)
- [ ] Each club has distance input fields:
  - Carry distance
  - Total distance (carry + roll)
- [ ] Inputs accept numbers only
- [ ] Validation rejects distances > 400 yards

### Hybrid Clubs
- [ ] Hybrid 2, 3, 4, 5, 6 are all available
- [ ] Distance inputs work for all hybrids
- [ ] Hybrids can replace irons (e.g., Hybrid 4 instead of 4 Iron)

### Wedge Degree Inputs
- [ ] Wedges show degree input (e.g., "52°" for Gap Wedge)
- [ ] Degree inputs accept 44-64° range
- [ ] Default degrees: PW=46°, GW=52°, SW=56°, LW=60°
- [ ] Custom degrees can be entered

### Save & Load
- [ ] "Save Bag" button saves to browser localStorage
- [ ] After save: success message appears
- [ ] Reload page → bag data persists
- [ ] "Clear Bag" button resets to onboarding

### Baseline Player Creation
- [ ] Saving bag creates player baseline in backend
- [ ] Player ID is generated/stored
- [ ] Recommendations use the player's actual distances
- [ ] Editing bag updates player baseline

---

## 7. Bottom Nav & Screen Switching

### Navigation Bar
- [ ] Bottom nav is visible on all screens
- [ ] Three tabs: Courses, Shot Advisor, My Bag
- [ ] Active tab is highlighted
- [ ] Icons are clear and intuitive

### Tab Switching
- [ ] Tap "Courses" → shows course list
- [ ] Tap "Shot Advisor" → shows shot form (if context available)
- [ ] Tap "My Bag" → shows bag setup/editor
- [ ] Switching tabs doesn't lose state
- [ ] Switching tabs doesn't cause flicker/reload

### State Persistence
- [ ] Course search query persists when switching tabs
- [ ] Shot advisor form data persists
- [ ] My Bag edits are saved before switching

---

## 8. Back Button Navigation

### Browser Back
- [ ] Course detail → Back → Course list
- [ ] Hole detail → Back → Course detail
- [ ] Shot advisor → Back → Previous screen
- [ ] Back button never causes app crash
- [ ] Back button doesn't skip screens

### In-App Back
- [ ] Back button in header works on all screens
- [ ] Back button navigates to logical previous screen
- [ ] No orphaned screens (can always get back to home)

---

## 9. Error Handling

### Network Errors
- [ ] Disconnect network → attempt search → shows error message
- [ ] Error message is user-friendly (not technical)
- [ ] Retry mechanism is available
- [ ] App doesn't crash on network failure

### API Errors
- [ ] Backend down → shows "Service unavailable"
- [ ] Invalid course ID → shows "Course not found"
- [ ] Invalid player data → shows validation error
- [ ] 500 error → shows generic error message

### Input Validation Errors
- [ ] Submit empty form → shows "Required field" messages
- [ ] Enter invalid distance → shows range error
- [ ] Enter letters in number field → rejected or sanitized

### Edge Cases
- [ ] Very slow network → shows loading indicator
- [ ] Timeout → shows timeout message
- [ ] Rapid button clicking → prevents duplicate requests

---

## 10. Mobile Responsiveness

### Screen Sizes
- [ ] iPhone SE (375x667) → all content visible
- [ ] iPhone 12/13 (390x844) → proper layout
- [ ] iPhone 14 Pro Max (430x932) → no wasted space
- [ ] Android small (360x640) → all features accessible
- [ ] Tablet/iPad (768x1024) → responsive layout

### Touch Targets
- [ ] All buttons are minimum 44x44px (finger-sized)
- [ ] Course cards are easy to tap
- [ ] Form inputs are large enough to tap accurately
- [ ] No accidental taps on nearby elements

### Keyboard Behavior
- [ ] Tap text input → keyboard appears
- [ ] Keyboard doesn't cover input field
- [ ] "Done" on keyboard dismisses it
- [ ] Form scrolls to keep active input visible

### Orientation
- [ ] Portrait mode works perfectly
- [ ] Landscape mode (if supported) displays correctly
- [ ] Orientation change doesn't lose data

### Scrolling
- [ ] Long course lists scroll smoothly
- [ ] Hole detail content scrolls without jank
- [ ] Scroll position is maintained when navigating back
- [ ] No rubber-banding issues

---

## 11. Performance

### Load Times
- [ ] Initial app load < 3 seconds
- [ ] Course list loads instantly (or with spinner)
- [ ] Course detail loads in < 1 second
- [ ] Recommendation request completes < 2 seconds

### Animations
- [ ] Page transitions are smooth
- [ ] Tab switches are instant
- [ ] No stuttering during scrolling
- [ ] SVG rendering is performant

### Memory
- [ ] App doesn't slow down after extended use
- [ ] No memory leaks (check dev tools)
- [ ] Multiple course views don't degrade performance

---

## 12. Accessibility

### Screen Reader
- [ ] Course cards have descriptive labels
- [ ] Form inputs have labels
- [ ] Buttons announce their purpose
- [ ] Tab order is logical

### Contrast & Readability
- [ ] Text is readable against backgrounds
- [ ] Form labels are clear
- [ ] Error messages are visible
- [ ] Color isn't the only differentiator

### Font Sizes
- [ ] Minimum text size is 14px
- [ ] Headings are appropriately sized
- [ ] Small text (e.g., handicap) is still readable

---

## 13. Known Issues to Test

### Elevation Formula Fix
- [ ] Recommendations at 5000+ ft elevation are accurate
- [ ] Distance adjustments match physics test expectations
- [ ] Elevation formula uses 0.00002 coefficient (not old 0.00116)

### Pin Marker Persistence
- [ ] Pin markers persist across navigation (verified above)
- [ ] Pin positions save to state/storage
- [ ] Pin reset button works (if implemented)

### Hybrid & Wedge Support
- [ ] All 5 hybrid options work
- [ ] Wedge degree inputs work
- [ ] Recommendations correctly use hybrid/wedge distances

---

## Test Results Summary

**Date Tested:** ___________  
**Tester:** ___________  
**Device/Browser:** ___________  

**Total Checks:** _____ / _____  
**Passed:** _____  
**Failed:** _____  

**Critical Issues Found:**
1. 
2. 
3. 

**Minor Issues Found:**
1. 
2. 
3. 

**Notes:**


---

## Sign-off

- [ ] All critical features work
- [ ] No P0 bugs remaining
- [ ] User experience is smooth
- [ ] Ready for production

**QA Lead:** _________________  
**Date:** _________________
