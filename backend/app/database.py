"""
Database connection and session management for City Break Planner.

Uses SQLAlchemy 2.0 style with a synchronous engine. GeoAlchemy2 works
with the same engine (postgresql+psycopg2); no extra config required.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Default URL matches docker-compose (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://citybreak:citybreak@localhost:5432/citybreak",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    echo=False,  # Set True for SQL logging during development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency that yields a DB session. Use with FastAPI's Depends().
    Ensures the session is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
