"""
Database Migration Script

Migrates data from JSON file storage to PostgreSQL.
Run once when switching from MVP to production.

Usage:
    python migrate.py --create-tables
    python migrate.py --import-data
    python migrate.py --all
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models as db_models

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import PlayerBaseline, CourseHoles
from data_store import data_store


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


def import_players(db: Session):
    """Import players from data_store to PostgreSQL"""
    print("\nImporting players...")
    
    count = 0
    for player_id, player in data_store.players.items():
        # Check if player already exists
        existing = db.query(db_models.PlayerBaseline).filter(
            db_models.PlayerBaseline.player_id == player_id
        ).first()
        
        if existing:
            print(f"  ⚠️  Player {player_id} already exists, skipping")
            continue
        
        # Create player record
        db_player = db_models.PlayerBaseline(
            player_id=player.player_id,
            player_name=player.player_name,
            created_date=player.created_date,
            last_updated=player.last_updated
        )
        db.add(db_player)
        
        # Create club distance records
        for club_dist in player.club_distances:
            club_type = club_dist.club_type.value if hasattr(club_dist.club_type, 'value') else str(club_dist.club_type)
            
            db_club = db_models.ClubDistance(
                player_id=player.player_id,
                club_type=club_type,
                carry_distance=club_dist.carry_distance,
                total_distance=club_dist.total_distance
            )
            db.add(db_club)
        
        count += 1
        print(f"  ✅ Imported player: {player.player_name}")
    
    db.commit()
    print(f"\n✅ Imported {count} players")


def import_courses(db: Session):
    """Import courses from data_store to PostgreSQL"""
    print("\nImporting courses...")
    
    count = 0
    for course_id, course in data_store.courses.items():
        # Check if course already exists
        existing = db.query(db_models.Course).filter(
            db_models.Course.course_id == course_id
        ).first()
        
        if existing:
            print(f"  ⚠️  Course {course_id} already exists, skipping")
            continue
        
        # Create course record
        db_course = db_models.Course(
            course_id=course.course_id,
            course_name=course.course_name,
            course_elevation_feet=course.course_elevation_feet,
            created_date=datetime.now()
        )
        db.add(db_course)
        
        # Create hole records
        for hole in course.holes:
            db_hole = db_models.Hole(
                hole_id=hole.hole_id,
                course_id=course.course_id,
                hole_number=hole.hole_number,
                par=hole.par,
                distance_to_pin_yards=hole.distance_to_pin_yards,
                shot_bearing_degrees=hole.shot_bearing_degrees
            )
            db.add(db_hole)
        
        count += 1
        print(f"  ✅ Imported course: {course.course_name} ({len(course.holes)} holes)")
    
    db.commit()
    print(f"\n✅ Imported {count} courses")


def import_player_profiles():
    """Import player profiles from JSON files"""
    print("\nImporting player profiles...")
    
    profiles_dir = Path(__file__).parent.parent.parent / "data" / "players"
    if not profiles_dir.exists():
        print("  ⚠️  No player profiles directory found")
        return
    
    count = 0
    for profile_file in profiles_dir.glob("*.json"):
        try:
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
            
            # TODO: Import to PlayerProfile table when that model is added to db/models.py
            print(f"  ✅ Found profile: {profile_file.name}")
            count += 1
        except Exception as e:
            print(f"  ❌ Error loading {profile_file.name}: {e}")
    
    print(f"\n✅ Found {count} player profiles (TODO: add PlayerProfile table)")


def verify_migration(db: Session):
    """Verify migration was successful"""
    print("\nVerifying migration...")
    
    player_count = db.query(db_models.PlayerBaseline).count()
    course_count = db.query(db_models.Course).count()
    hole_count = db.query(db_models.Hole).count()
    club_count = db.query(db_models.ClubDistance).count()
    
    print(f"  Players: {player_count}")
    print(f"  Courses: {course_count}")
    print(f"  Holes: {hole_count}")
    print(f"  Club distances: {club_count}")
    
    if player_count > 0 or course_count > 0:
        print("\n✅ Migration verified successfully")
    else:
        print("\n⚠️  No data found - did you run --import-data?")


def main():
    parser = argparse.ArgumentParser(description="Migrate Personal Caddie data to PostgreSQL")
    parser.add_argument("--create-tables", action="store_true", help="Create database tables")
    parser.add_argument("--import-data", action="store_true", help="Import data from JSON storage")
    parser.add_argument("--all", action="store_true", help="Create tables and import data")
    parser.add_argument("--verify", action="store_true", help="Verify migration")
    
    args = parser.parse_args()
    
    if not any([args.create_tables, args.import_data, args.all, args.verify]):
        parser.print_help()
        return
    
    db = SessionLocal()
    
    try:
        if args.all or args.create_tables:
            create_tables()
        
        if args.all or args.import_data:
            import_players(db)
            import_courses(db)
            import_player_profiles()
        
        if args.verify or args.all:
            verify_migration(db)
    
    finally:
        db.close()
    
    print("\n🎉 Migration complete!")


if __name__ == "__main__":
    main()
