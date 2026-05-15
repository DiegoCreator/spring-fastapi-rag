import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database import Base

load_dotenv()
SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture()
def db():
    """Creates a session using the engine."""
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

POSTGRES_URL = os.getenv("DATABASE_URL")

if POSTGRES_URL and "@db" in POSTGRES_URL:
    POSTGRES_URL = POSTGRES_URL.replace("@db", "@localhost")

@pytest.fixture()
def pg_db():
    engine = create_engine(POSTGRES_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()