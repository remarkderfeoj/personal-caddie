#!/usr/bin/env python3
"""
OpenStreetMap Golf Course Hole Mapper

Uses Overpass API to query golf course features and attempt to infer
tee/green positions for individual holes.

COVERAGE WARNING: OSM golf data is extremely spotty. Most courses have
only basic course boundaries, not individual tees/greens. This tool is
best-effort and will have low success rates for most courses.

Usage:
    python osm_hole_mapper.py --name "Pebble Beach" --lat 36.5668 --lng -121.9487
    python osm_hole_mapper.py --name "Augusta National" --lat 33.5027 --lng -82.0199
"""

import requests
import json
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class GolfFeature:
    """A golf feature from OSM"""
    osm_id: int
    feature_type: str  # tee, green, hole, fairway, bunker, water_hazard
    lat: float
    lng: float
    name: Optional[str] = None
    ref: Optional[str] = None  # hole number reference
    tags: Dict = None


@dataclass
class HoleMapping:
    """Inferred hole mapping"""
    hole_number: int
    tee_lat: Optional[float]
    tee_lng: Optional[float]
    green_lat: Optional[float]
    green_lng: Optional[float]
    confidence: float  # 0.0 to 1.0
    notes: str


class OSMHoleMapper:
    """Query OSM and attempt to map golf holes"""
    
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self, course_name: str, center_lat: float, center_lng: float, radius_km: float = 1.0):
        self.course_name = course_name
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.radius_km = radius_km
        self.radius_m = radius_km * 1000
    
    def query_osm(self) -> List[GolfFeature]:
        """
        Query Overpass API for golf features.
        
        Returns:
            List of GolfFeature objects
        """
        # Overpass QL query for golf features
        # Search for: golf=tee, golf=green, golf=hole, golf=fairway, 
        #             golf=bunker, golf=water_hazard, leisure=golf_course
        query = f"""
        [out:json][timeout:25];
        (
          node["golf"="tee"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          node["golf"="green"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          node["golf"="hole"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          way["golf"="tee"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          way["golf"="green"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          way["golf"="fairway"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          way["golf"="bunker"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          way["golf"="water_hazard"](around:{self.radius_m},{self.center_lat},{self.center_lng});
          relation["leisure"="golf_course"](around:{self.radius_m},{self.center_lat},{self.center_lng});
        );
        out center;
        """
        
        try:
            print(f"Querying Overpass API for golf features near {self.course_name}...")
            response = requests.post(self.OVERPASS_URL, data={'data': query}, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            print(f"Got {len(data.get('elements', []))} OSM elements")
            
            features = []
            for element in data.get('elements', []):
                feature = self._parse_element(element)
                if feature:
                    features.append(feature)
            
            return features
        
        except Exception as e:
            print(f"Error querying Overpass API: {e}")
            return []
    
    def _parse_element(self, element: Dict) -> Optional[GolfFeature]:
        """Parse an OSM element into a GolfFeature"""
        osm_id = element.get('id')
        tags = element.get('tags', {})
        
        # Get golf feature type
        golf_type = tags.get('golf')
        if not golf_type and tags.get('leisure') == 'golf_course':
            golf_type = 'course'
        
        if not golf_type:
            return None
        
        # Get coordinates
        if element['type'] == 'node':
            lat = element.get('lat')
            lng = element.get('lon')
        elif element['type'] == 'way' and 'center' in element:
            lat = element['center'].get('lat')
            lng = element['center'].get('lon')
        else:
            return None
        
        if lat is None or lng is None:
            return None
        
        return GolfFeature(
            osm_id=osm_id,
            feature_type=golf_type,
            lat=lat,
            lng=lng,
            name=tags.get('name'),
            ref=tags.get('ref'),
            tags=tags
        )
    
    def map_holes(self, features: List[GolfFeature], num_holes: int = 18) -> List[HoleMapping]:
        """
        Attempt to map tees and greens to specific holes.
        
        Strategy:
        1. Filter for tees and greens only
        2. If features have 'ref' tags (hole numbers), use those
        3. Otherwise, attempt proximity-based ordering (tee1→green1→tee2→green2...)
        
        Args:
            features: List of GolfFeature objects
            num_holes: Expected number of holes (default 18)
        
        Returns:
            List of HoleMapping objects
        """
        tees = [f for f in features if f.feature_type == 'tee']
        greens = [f for f in features if f.feature_type == 'green']
        
        print(f"\nFound {len(tees)} tees and {len(greens)} greens in OSM")
        
        if not tees and not greens:
            print("⚠️  No tees or greens found in OSM data")
            return []
        
        # Strategy 1: Use ref tags if available
        holes_by_ref = self._map_by_ref(tees, greens)
        
        if holes_by_ref:
            print(f"✓ Mapped {len(holes_by_ref)} holes using OSM ref tags")
            return holes_by_ref
        
        # Strategy 2: Proximity-based chaining
        print("No ref tags found, attempting proximity-based mapping...")
        holes_by_proximity = self._map_by_proximity(tees, greens, num_holes)
        
        return holes_by_proximity
    
    def _map_by_ref(self, tees: List[GolfFeature], greens: List[GolfFeature]) -> List[HoleMapping]:
        """Map holes using OSM ref tags (hole numbers)"""
        holes = {}
        
        for tee in tees:
            if tee.ref and tee.ref.isdigit():
                hole_num = int(tee.ref)
                if hole_num not in holes:
                    holes[hole_num] = HoleMapping(
                        hole_number=hole_num,
                        tee_lat=tee.lat,
                        tee_lng=tee.lng,
                        green_lat=None,
                        green_lng=None,
                        confidence=0.7,
                        notes="Mapped from OSM ref tag"
                    )
                else:
                    holes[hole_num].tee_lat = tee.lat
                    holes[hole_num].tee_lng = tee.lng
        
        for green in greens:
            if green.ref and green.ref.isdigit():
                hole_num = int(green.ref)
                if hole_num not in holes:
                    holes[hole_num] = HoleMapping(
                        hole_number=hole_num,
                        tee_lat=None,
                        tee_lng=None,
                        green_lat=green.lat,
                        green_lng=green.lng,
                        confidence=0.7,
                        notes="Mapped from OSM ref tag"
                    )
                else:
                    holes[hole_num].green_lat = green.lat
                    holes[hole_num].green_lng = green.lng
        
        # Update confidence for complete holes
        for hole in holes.values():
            if hole.tee_lat and hole.green_lat:
                hole.confidence = 0.9
        
        return sorted(holes.values(), key=lambda h: h.hole_number)
    
    def _map_by_proximity(self, tees: List[GolfFeature], greens: List[GolfFeature], 
                          num_holes: int) -> List[HoleMapping]:
        """
        Map holes by proximity chaining.
        
        Algorithm:
        1. Find the "starting" tee (closest to course center or arbitrary)
        2. Find nearest green to that tee
        3. Find next tee (nearest to previous green, but not already used)
        4. Repeat until all holes mapped
        
        This is highly speculative and will have low confidence.
        """
        if not tees or not greens:
            return []
        
        holes = []
        used_tees = set()
        used_greens = set()
        
        # Start with tee closest to course center
        current_lat, current_lng = self.center_lat, self.center_lng
        
        for hole_num in range(1, num_holes + 1):
            # Find nearest unused tee
            nearest_tee = None
            min_dist = float('inf')
            for tee in tees:
                if id(tee) in used_tees:
                    continue
                dist = self._haversine_distance(current_lat, current_lng, tee.lat, tee.lng)
                if dist < min_dist:
                    min_dist = dist
                    nearest_tee = tee
            
            if not nearest_tee:
                break
            
            used_tees.add(id(nearest_tee))
            
            # Find nearest unused green to this tee
            nearest_green = None
            min_dist = float('inf')
            for green in greens:
                if id(green) in used_greens:
                    continue
                dist = self._haversine_distance(nearest_tee.lat, nearest_tee.lng, 
                                                green.lat, green.lng)
                if dist < min_dist:
                    min_dist = dist
                    nearest_green = green
            
            if nearest_green:
                used_greens.add(id(nearest_green))
                current_lat, current_lng = nearest_green.lat, nearest_green.lng
                
                holes.append(HoleMapping(
                    hole_number=hole_num,
                    tee_lat=nearest_tee.lat,
                    tee_lng=nearest_tee.lng,
                    green_lat=nearest_green.lat,
                    green_lng=nearest_green.lng,
                    confidence=0.3,  # Low confidence for proximity-based mapping
                    notes="Proximity-based inference (low confidence)"
                ))
            else:
                # Tee only, no green found
                holes.append(HoleMapping(
                    hole_number=hole_num,
                    tee_lat=nearest_tee.lat,
                    tee_lng=nearest_tee.lng,
                    green_lat=None,
                    green_lng=None,
                    confidence=0.2,
                    notes="Tee only (no green found)"
                ))
        
        print(f"✓ Mapped {len(holes)} holes using proximity chaining (low confidence)")
        return holes
    
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
    
    def export_results(self, holes: List[HoleMapping], output_file: Optional[str] = None):
        """Export hole mappings to JSON"""
        results = {
            'course_name': self.course_name,
            'center_lat': self.center_lat,
            'center_lng': self.center_lng,
            'holes_mapped': len(holes),
            'holes': [
                {
                    'hole_number': h.hole_number,
                    'tee_lat': h.tee_lat,
                    'tee_lng': h.tee_lng,
                    'green_lat': h.green_lat,
                    'green_lng': h.green_lng,
                    'confidence': h.confidence,
                    'notes': h.notes
                }
                for h in holes
            ]
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✓ Results written to {output_file}")
        
        return results


def main():
    parser = argparse.ArgumentParser(description='Map golf holes using OpenStreetMap data')
    parser.add_argument('--name', required=True, help='Course name')
    parser.add_argument('--lat', type=float, required=True, help='Course center latitude')
    parser.add_argument('--lng', type=float, required=True, help='Course center longitude')
    parser.add_argument('--radius', type=float, default=1.0, help='Search radius in km (default: 1.0)')
    parser.add_argument('--holes', type=int, default=18, help='Number of holes (default: 18)')
    parser.add_argument('--output', help='Output JSON file (optional)')
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║          OSM Golf Course Hole Mapper                           ║
╚════════════════════════════════════════════════════════════════╝

Course: {args.name}
Center: {args.lat}, {args.lng}
Radius: {args.radius} km

⚠️  COVERAGE WARNING:
OpenStreetMap golf data is extremely sparse. Most courses only have
basic outlines, not individual tee/green positions. This tool is
best-effort and success rates are typically very low.

For famous courses, manual curation is recommended.
""")
    
    mapper = OSMHoleMapper(args.name, args.lat, args.lng, args.radius)
    features = mapper.query_osm()
    
    if not features:
        print("\n❌ No golf features found in OSM")
        print("   Consider manual curation for this course.")
        return
    
    # Print feature summary
    feature_counts = {}
    for f in features:
        feature_counts[f.feature_type] = feature_counts.get(f.feature_type, 0) + 1
    
    print("\nOSM Feature Summary:")
    for ftype, count in sorted(feature_counts.items()):
        print(f"  {ftype:20} {count:3}")
    
    holes = mapper.map_holes(features, args.holes)
    
    if holes:
        print(f"\n✓ Successfully mapped {len(holes)} holes\n")
        print("Hole | Tee Coords        | Green Coords      | Confidence")
        print("-----|-------------------|-------------------|------------")
        for h in holes:
            tee_str = f"{h.tee_lat:.5f},{h.tee_lng:.5f}" if h.tee_lat else "None"
            green_str = f"{h.green_lat:.5f},{h.green_lng:.5f}" if h.green_lat else "None"
            print(f"  {h.hole_number:2} | {tee_str:17} | {green_str:17} | {h.confidence:.1%}")
        
        results = mapper.export_results(holes, args.output)
        
        if not args.output:
            print("\n" + json.dumps(results, indent=2))
    else:
        print("\n❌ Could not map any holes")
        print("   OSM data insufficient for this course.")


if __name__ == '__main__':
    main()
