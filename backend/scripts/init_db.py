"""
Create PostGIS extension and all tables. For local dev only.

Run from project root:
  cd backend && python -m scripts.init_db

Or with venv and DATABASE_URL set:
  python backend/scripts/init_db.py
"""
import sys
from pathlib import Path

# Allow running as script or module; ensure app is importable
backend = Path(__file__).resolve().parent.parent
if str(backend) not in sys.path:
    sys.path.insert(0, str(backend))

from sqlalchemy import text
from app.database import engine, Base
from app import models  # noqa: F401 - register models with Base

def main():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("PostGIS extension and tables created successfully.")

if __name__ == "__main__":
    main()
