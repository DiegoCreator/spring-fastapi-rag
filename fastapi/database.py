import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

EMBEDDING_DIM = 384
Base = declarative_base()

def get_engine():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing from the .env file. Make sure the configuration is correct.")
    return create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

def get_db():
    """Creates a session using the engine."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()