"""
Simple in-memory data store for MVP.

Loads example data and provides search functionality.
Will be replaced with database in Phase 2.
"""

import json
import os
from typing import Optional, List, Dict
from pathlib import Path
from models import CourseHoles, PlayerBaseline

class DataStore:
    """In-memory data store"""
    
    def __init__(self):
        self.courses: Dict[str, CourseHoles] = {}
        self.players: Dict[str, PlayerBaseline] = {}
        self._load_examples()
    
    def _load_examples(self):
        """Load example data from files"""
        examples_dir = Path(__file__).parent.parent / "examples"
        
        # Load all course JSON files
        for course_file in examples_dir.glob("*.json"):
            # Skip player files
            if "player" in course_file.name.lower():
                continue
            
            try:
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
                course = CourseHoles(**course_data)
                self.courses[course.course_id] = course
                print(f"Loaded course: {course.course_name} ({len(course.holes)} holes)")
            except Exception as e:
                print(f"Error loading {course_file.name}: {e}")
        
        # Load sample player
        player_file = examples_dir / "sample_player_baseline.json"
        if player_file.exists():
            try:
                with open(player_file, 'r') as f:
                    player_data = json.load(f)
                player = PlayerBaseline(**player_data)
                self.players[player.player_id] = player
                print(f"Loaded player: {player.player_name}")
            except Exception as e:
                print(f"Error loading player: {e}")
    
    def get_course_by_id(self, course_id: str) -> Optional[CourseHoles]:
        """Get course by exact ID"""
        return self.courses.get(course_id)
    
    def search_courses(self, query: str) -> List[CourseHoles]:
        """
        Search courses by name (case-insensitive).
        
        Args:
            query: Search string
        
        Returns:
            List of matching courses
        """
        query_lower = query.lower()
        matches = []
        
        for course in self.courses.values():
            if query_lower in course.course_name.lower():
                matches.append(course)
            elif query_lower in course.course_id.lower():
                matches.append(course)
        
        return matches
    
    def list_all_courses(self) -> List[CourseHoles]:
        """Get all courses"""
        return list(self.courses.values())
    
    def add_course(self, course: CourseHoles) -> None:
        """Add or update a course"""
        self.courses[course.course_id] = course
    
    def get_player_by_id(self, player_id: str) -> Optional[PlayerBaseline]:
        """Get player by exact ID"""
        return self.players.get(player_id)
    
    def add_player(self, player: PlayerBaseline) -> None:
        """Add or update a player"""
        self.players[player.player_id] = player


# Global data store instance
data_store = DataStore()
