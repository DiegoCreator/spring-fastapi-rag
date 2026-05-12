import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

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