from uuid import uuid4

import pytest
import os
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from conversation_service import save_message
from database import Base
from models import ChatSession

load_dotenv()
SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture()
def db():
    """Creates a session using the engine."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool,)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

POSTGRES_URL = os.getenv("DATABASE_TEST_URL")

if POSTGRES_URL and "@db" in POSTGRES_URL:
    POSTGRES_URL = POSTGRES_URL.replace("@db", "@localhost")

@pytest.fixture()
def pg_db():
    engine = create_engine(POSTGRES_URL)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def chat_session(pg_db):
    session = ChatSession(
        session_id=uuid4(),
        title="Test session"
    )
    pg_db.add(session)
    pg_db.commit()
    return session

@pytest.fixture
def make_message(pg_db):
    def _make(session_id, content, role="user"):
        return save_message(
            session_id=session_id,
            role=role,
            content=content,
            db=pg_db
        )
    return _make