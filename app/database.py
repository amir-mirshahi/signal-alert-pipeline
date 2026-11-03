"""
Sets up the SQLAlchemy database connection and session.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

# check_same_thread=False is required for SQLite to work with FastAPI's background tasks
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is what we will use to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for our database models
Base = declarative_base()