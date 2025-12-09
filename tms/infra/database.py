"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from tms.config import config

# Create SQLAlchemy engine
# Create SQLAlchemy engine
connect_args = {}
if "sqlite" in config.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    config.DATABASE_URL,
    connect_args=connect_args,
    echo=config.DEBUG,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Yields a database session and ensures it's closed after use
    """
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(f"❌ Database session error: {e}")
        # Check if we are accidentally using SQLite on Vercel
        if "sqlite" in config.DATABASE_URL and config.UPLOAD_DIR.startswith("/tmp"):
             print("⚠️ CRITICAL: Using SQLite on Vercel (Read-only filesystem). DATABASE_URL environment variable is likely missing!")
        raise e
    finally:
        if db:
            db.close()

def init_db() -> None:
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)

def drop_db() -> None:
    """
    Drop all database tables - use with caution!
    """
    Base.metadata.drop_all(bind=engine)
