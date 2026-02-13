#!/usr/bin/env python3
"""
Golf Course Hole Validation Script

Validates course JSON files for completeness and correctness:
- All courses have 18 holes (or flags incomplete)
- No duplicate hole numbers
- Tee/green coordinates are within course bounding box
- Tee→green distance roughly matches stated yardage (within 20%)
- All lat/lng values are reasonable

Usage:
    python validate_holes.py ../examples/*.json
    python validate_holes.py --all
"""

import json
import argparse
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """A validation issue"""
    severity: str  # ERROR, WARNING, INFO
    course: str
    hole: Optional[int]
    message: str


class HoleValidator:
    """Validate golf course hole data"""
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
    
    def validate_file(self, filepath: Path) -> Dict:
        """Validate a single course file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                course=filepath.name,
                hole=None,
                message=f'Failed to load JSON: {e}'
            ))
            return {}
        
        course_name = data.get('course_name', filepath.name)
        holes = data.get('holes', [])
        
        # Validate course-level data
        self._validate_course_metadata(data, course_name)
        
        # Validate hole count
        self._validate_hole_count(course_name, holes)
        
        # Validate each hole
        for hole in holes:
            self._validate_hole(course_name, hole, data)
        
        # Validate hole numbers are unique and sequential
        self._validate_hole_numbers(course_name, holes)
        
        # Validate GPS bounding box
        if data.get('center_lat') and data.get('center_lng'):
            self._validate_gps_bounding_box(course_name, holes, data)
        
        return {
            'course': course_name,
            'holes': len(holes),
            'holes_with_gps': sum(1 for h in holes if h.get('tee_lat') is not None),
            'issues': len([i for i in self.issues if i.course == course_name])
        }
    
    def _validate_course_metadata(self, data: Dict, course_name: str):
        """Validate course-level metadata"""
        required_fields = ['course_id', 'course_name', 'course_elevation_feet', 'holes']
        
        for field in required_fields:
            if field not in data:
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=None,
                    message=f'Missing required field: {field}'
                ))
        
        # Validate center coordinates if present
        center_lat = data.get('center_lat')
        center_lng = data.get('center_lng')
        
        if center_lat is not None:
            if not (-90 <= center_lat <= 90):
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=None,
                    message=f'Invalid center_lat: {center_lat} (must be -90 to 90)'
                ))
        
        if center_lng is not None:
            if not (-180 <= center_lng <= 180):
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=None,
                    message=f'Invalid center_lng: {center_lng} (must be -180 to 180)'
                ))
    
    def _validate_hole_count(self, course_name: str, holes: List[Dict]):
        """Validate hole count"""
        if len(holes) != 18:
            severity = 'WARNING' if len(holes) > 0 else 'ERROR'
            self.issues.append(ValidationIssue(
                severity=severity,
                course=course_name,
                hole=None,
                message=f'Course has {len(holes)} holes (expected 18)'
            ))
    
    def _validate_hole_numbers(self, course_name: str, holes: List[Dict]):
        """Validate hole numbers are unique and in range"""
        hole_numbers = [h.get('hole_number') for h in holes]
        
        # Check for duplicates
        duplicates = [num for num in hole_numbers if hole_numbers.count(num) > 1]
        if duplicates:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                course=course_name,
                hole=None,
                message=f'Duplicate hole numbers: {set(duplicates)}'
            ))
        
        # Check for out-of-range numbers
        for num in hole_numbers:
            if num is not None and not (1 <= num <= 18):
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=num,
                    message=f'Hole number {num} out of range (1-18)'
                ))
    
    def _validate_hole(self, course_name: str, hole: Dict, course_data: Dict):
        """Validate a single hole"""
        hole_num = hole.get('hole_number', '?')
        
        # Required fields
        required_fields = ['hole_id', 'hole_number', 'par', 'handicap_index', 
                          'distance_to_pin_yards', 'fairway_type']
        
        for field in required_fields:
            if field not in hole:
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=hole_num,
                    message=f'Missing required field: {field}'
                ))
        
        # Validate par
        par = hole.get('par')
        if par is not None and not (3 <= par <= 5):
            self.issues.append(ValidationIssue(
                severity='ERROR',
                course=course_name,
                hole=hole_num,
                message=f'Invalid par: {par} (must be 3-5)'
            ))
        
        # Validate handicap index
        handicap = hole.get('handicap_index')
        if handicap is not None and not (1 <= handicap <= 18):
            self.issues.append(ValidationIssue(
                severity='ERROR',
                course=course_name,
                hole=hole_num,
                message=f'Invalid handicap_index: {handicap} (must be 1-18)'
            ))
        
        # Validate distance
        distance = hole.get('distance_to_pin_yards')
        if distance is not None:
            if not (50 <= distance <= 700):
                self.issues.append(ValidationIssue(
                    severity='WARNING',
                    course=course_name,
                    hole=hole_num,
                    message=f'Unusual distance: {distance} yards'
                ))
        
        # Validate GPS coordinates
        tee_lat = hole.get('tee_lat')
        tee_lng = hole.get('tee_lng')
        green_lat = hole.get('green_lat')
        green_lng = hole.get('green_lng')
        
        # If any GPS field is present, validate it
        if tee_lat is not None:
            if not (-90 <= tee_lat <= 90):
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=hole_num,
                    message=f'Invalid tee_lat: {tee_lat}'
                ))
        
        if tee_lng is not None:
            if not (-180 <= tee_lng <= 180):
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=hole_num,
                    message=f'Invalid tee_lng: {tee_lng}'
                ))
        
        if green_lat is not None:
            if not (-90 <= green_lat <= 90):
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=hole_num,
                    message=f'Invalid green_lat: {green_lat}'
                ))
        
        if green_lng is not None:
            if not (-180 <= green_lng <= 180):
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    course=course_name,
                    hole=hole_num,
                    message=f'Invalid green_lng: {green_lng}'
                ))
        
        # If both tee and green coords exist, validate distance
        if all(x is not None for x in [tee_lat, tee_lng, green_lat, green_lng, distance]):
            gps_distance_yards = self._haversine_distance(
                tee_lat, tee_lng, green_lat, green_lng
            ) * 1093.61  # km to yards
            
            # Allow 20% tolerance
            tolerance = 0.20
            lower_bound = distance * (1 - tolerance)
            upper_bound = distance * (1 + tolerance)
            
            if not (lower_bound <= gps_distance_yards <= upper_bound):
                self.issues.append(ValidationIssue(
                    severity='WARNING',
                    course=course_name,
                    hole=hole_num,
                    message=f'GPS distance ({gps_distance_yards:.0f} yds) differs from stated distance ({distance} yds) by more than 20%'
                ))
    
    def _validate_gps_bounding_box(self, course_name: str, holes: List[Dict], course_data: Dict):
        """Validate that hole GPS coordinates are within reasonable bounds of course center"""
        center_lat = course_data.get('center_lat')
        center_lng = course_data.get('center_lng')
        
        # Typical golf course is 1-2 km across, so we'll use 3 km as outer bound
        MAX_DISTANCE_KM = 3.0
        
        for hole in holes:
            hole_num = hole.get('hole_number', '?')
            tee_lat = hole.get('tee_lat')
            tee_lng = hole.get('tee_lng')
            green_lat = hole.get('green_lat')
            green_lng = hole.get('green_lng')
            
            if tee_lat and tee_lng:
                dist = self._haversine_distance(center_lat, center_lng, tee_lat, tee_lng)
                if dist > MAX_DISTANCE_KM:
                    self.issues.append(ValidationIssue(
                        severity='WARNING',
                        course=course_name,
                        hole=hole_num,
                        message=f'Tee is {dist:.2f} km from course center (expected < {MAX_DISTANCE_KM} km)'
                    ))
            
            if green_lat and green_lng:
                dist = self._haversine_distance(center_lat, center_lng, green_lat, green_lng)
                if dist > MAX_DISTANCE_KM:
                    self.issues.append(ValidationIssue(
                        severity='WARNING',
                        course=course_name,
                        hole=hole_num,
                        message=f'Green is {dist:.2f} km from course center (expected < {MAX_DISTANCE_KM} km)'
                    ))
    
    @staticmethod
    def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in km between two lat/lng points"""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def print_report(self):
        """Print validation report"""
        errors = [i for i in self.issues if i.severity == 'ERROR']
        warnings = [i for i in self.issues if i.severity == 'WARNING']
        infos = [i for i in self.issues if i.severity == 'INFO']
        
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          Golf Course Validation Report                         ║
╚════════════════════════════════════════════════════════════════╝

Total Issues: {len(self.issues)}
  • Errors:   {len(errors)}
  • Warnings: {len(warnings)}
  • Info:     {len(infos)}
""")
        
        if errors:
            print("❌ ERRORS:")
            for issue in errors:
                hole_str = f" (Hole {issue.hole})" if issue.hole else ""
                print(f"  • {issue.course}{hole_str}: {issue.message}")
            print()
        
        if warnings:
            print("⚠️  WARNINGS:")
            for issue in warnings:
                hole_str = f" (Hole {issue.hole})" if issue.hole else ""
                print(f"  • {issue.course}{hole_str}: {issue.message}")
            print()
        
        if not errors and not warnings:
            print("✅ All validations passed!")
        
        return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description='Validate golf course hole data')
    parser.add_argument('files', nargs='*', help='Course JSON files to validate')
    parser.add_argument('--all', action='store_true', help='Validate all courses in examples/')
    parser.add_argument('--summary', action='store_true', help='Show summary only')
    
    args = parser.parse_args()
    
    validator = HoleValidator()
    
    # Determine which files to validate
    if args.all or not args.files:
        # Find examples directory
        script_dir = Path(__file__).parent
        examples_dir = script_dir.parent.parent / 'examples'
        
        if not examples_dir.exists():
            print(f"Error: examples directory not found at {examples_dir}")
            return 1
        
        files = sorted(examples_dir.glob('*.json'))
        files = [f for f in files if 'player' not in f.name.lower()]
    else:
        files = [Path(f) for f in args.files]
    
    print(f"Validating {len(files)} course files...\n")
    
    results = []
    for filepath in files:
        result = validator.validate_file(filepath)
        if result:
            results.append(result)
    
    # Print summary table
    if args.summary or len(files) > 5:
        print("\n" + "="*70)
        print(f"{'Course':<45} | Holes | GPS | Issues")
        print("="*70)
        for r in sorted(results, key=lambda x: x['course']):
            print(f"{r['course']:<45} | {r['holes']:5} | {r['holes_with_gps']:3} | {r['issues']:6}")
        print("="*70)
    
    # Print full report
    validator.print_report()
    
    return 0 if validator.print_report() else 1


if __name__ == '__main__':
    exit(main())
