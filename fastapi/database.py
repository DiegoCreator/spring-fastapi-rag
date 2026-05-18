import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

EMBEDDING_DIM = 384
Base = declarative_base()

def get_engine():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment variables.")
        raise ValueError("DATABASE_URL is missing from the .env file. Make sure the configuration is correct.")

    logger.info("Initializing SQLAlchemy engine...")
    return create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

def get_db():
    """Creates a session using the engine."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()

    logger.debug("Database session started.")
    try:
        yield db
    finally:
        db.close()