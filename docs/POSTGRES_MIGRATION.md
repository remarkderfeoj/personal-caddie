# PostgreSQL Migration Guide

## Overview

Personal Caddie MVP uses JSON file storage. This guide walks you through migrating to PostgreSQL for production.

## Prerequisites

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt install postgresql postgresql-contrib

# macOS:
brew install postgresql
brew services start postgresql

# Verify installation
psql --version
```

## Step 1: Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE personal_caddie;
CREATE USER caddie_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE personal_caddie TO caddie_user;
\q
```

## Step 2: Configure Environment

Create `.env` file in `backend/` directory:

```bash
# backend/.env
DATABASE_URL=postgresql://caddie_user:your_secure_password_here@localhost:5432/personal_caddie
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Step 3: Install Dependencies

```bash
cd backend
pip install sqlalchemy psycopg2-binary alembic
```

Update `requirements.txt`:

```txt
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.1
```

## Step 4: Run Migration

```bash
cd backend/db

# Create tables
python migrate.py --create-tables

# Import existing data
python migrate.py --import-data

# Or do both at once
python migrate.py --all

# Verify migration
python migrate.py --verify
```

Expected output:

```
Creating database tables...
✅ Tables created successfully

Importing players...
  ✅ Imported player: Joe Kramer
✅ Imported 1 players

Importing courses...
  ✅ Imported course: Augusta National (3 holes)
✅ Imported 1 courses

Verifying migration...
  Players: 1
  Courses: 1
  Holes: 3
  Club distances: 14
✅ Migration verified successfully

🎉 Migration complete!
```

## Step 5: Update Application

Modify `backend/main.py` to use database instead of data_store:

```python
from db import get_db, repository
from sqlalchemy.orm import Session

@app.get("/api/v1/courses/{course_id}")
def get_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    repo = repository.CourseRepository(db)
    course = repo.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
```

## Step 6: Database Backups

### Automated Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/personal_caddie"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump personal_caddie > $BACKUP_DIR/caddie_$DATE.sql
# Keep last 7 days
find $BACKUP_DIR -name "caddie_*.sql" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /path/to/backup.sh
```

### Manual Backup/Restore

```bash
# Backup
pg_dump personal_caddie > backup.sql

# Restore
psql personal_caddie < backup.sql
```

## Step 7: Performance Optimization

### Indexes

```sql
-- Add indexes for common queries
CREATE INDEX idx_player_id ON player_baselines(player_id);
CREATE INDEX idx_course_id ON courses(course_id);
CREATE INDEX idx_hole_course ON holes(course_id);
CREATE INDEX idx_hole_number ON holes(hole_number);
CREATE INDEX idx_club_player ON club_distances(player_id);
```

### Connection Pooling

Update `backend/db/database.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Troubleshooting

### Connection Refused

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check port is correct
sudo netstat -tulpn | grep 5432
```

### Authentication Failed

```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Change peer to md5 for local connections
local   all   all   md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Migration Errors

```bash
# Drop and recreate database
sudo -u postgres psql
DROP DATABASE personal_caddie;
CREATE DATABASE personal_caddie;
\q

# Re-run migration
python migrate.py --all
```

## Rollback Plan

If you need to rollback to JSON storage:

```bash
# Export data from PostgreSQL
python export_to_json.py  # TODO: Create this script

# Update main.py to use data_store again
git checkout main.py

# Restart application
```

## Next Steps

After migration:

1. ✅ Test all API endpoints
2. ✅ Monitor query performance
3. ✅ Set up automated backups
4. ✅ Configure monitoring (pg_stat_statements)
5. ✅ Plan for scaling (read replicas, connection pooling)

## Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
