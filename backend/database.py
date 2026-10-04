import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file path (resolved dynamically relative to project root)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "pyaazsure.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite in FastAPI
)

# Session local factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency to yield database sessions per request.
    Ensures connection is closed cleanly after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
