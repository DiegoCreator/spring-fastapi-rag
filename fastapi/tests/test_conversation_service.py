from uuid import uuid4
from sqlalchemy.orm import Session
from conversation_service import sliding_window, save_message, delete_session, semantic_search
from models import ChatSession, ChatMessage


def test_sliding_window_returns_last_n_messages_in_chronological_order(pg_db: Session, chat_session, make_message):
    try:
        for i in range(10):
            make_message(chat_session.session_id, f"message-{i}")

        result = sliding_window(chat_session.session_id, pg_db, limit=6)

        assert len(result) == 6

        assert [m.content for m in result] == [
            "message-4",
            "message-5",
            "message-6",
            "message-7",
            "message-8",
            "message-9",
        ]

    finally:
        delete_session(chat_session.session_id, pg_db)

def test_sliding_window_filters_other_sessions(pg_db: Session, make_message):
    chat_session = uuid4()
    chat_session2 = uuid4()

    pg_db.add_all([ ChatSession(session_id=chat_session, title="session1"),
        ChatSession(session_id=chat_session2, title="session2"),])
    pg_db.commit()

    try:

        for i in range(2):
            make_message(chat_session, f"session1-{i}")
            make_message(chat_session2, f"session2-{i}")

        result1 = sliding_window(chat_session, pg_db)
        result2 = sliding_window(chat_session2, pg_db)

        assert [m.content for m in result1] == [
            "session1-0",
            "session1-1",
        ]

        assert [m.content for m in result2] == [
            "session2-0",
            "session2-1",
        ]

    finally:
        delete_session(chat_session, pg_db)
        delete_session(chat_session2, pg_db)

def test_save_message_creates_message(pg_db, chat_session):
    try:
        msg = save_message(
            session_id=chat_session.session_id,
            role="user",
            content="hello",
            db=pg_db
        )


        stored = pg_db.get(ChatMessage, msg.message_id)

        assert stored is not None
        assert stored.content == "hello"
        assert stored.role == "user"
        assert stored.session_id == chat_session.session_id

    finally:
        delete_session(chat_session.session_id, pg_db)

def test_semantic_search_returns_closest_embeddings(chat_session, pg_db):
    exact = [1.0] + [0.0] * 383

    close = [0.9, 0.1] + [0.0] * 382

    far = [0.0, 1.0] + [0.0] * 382
    try:

        save_message(
            session_id=chat_session.session_id,
            role="user",
            content="exact",
            embedding=exact,
            db=pg_db,
        )
        save_message(
            session_id=chat_session.session_id,
            role="user",
            content="close",
            embedding=close,
            db=pg_db,
        )
        save_message(
            session_id=chat_session.session_id,
            role="user",
            content="far",
            embedding=far,
            db=pg_db,
        )

        results = semantic_search(
            session_id=chat_session.session_id,
            embedding=exact,
            limit=3,
            db=pg_db,
        )

        assert [m.content for m in results] == [
            "exact",
            "close",
            "far",
        ]

    finally:
        delete_session(chat_session.session_id, pg_db)

def test_delete_session_removes_session(chat_session, pg_db):
    delete_session(chat_session.session_id, pg_db)

    assert pg_db.get(ChatSession, chat_session.session_id) is None


def test_delete_session_nonexistent_session(pg_db):
    delete_session(uuid4(), pg_db)

def test_delete_session_cascades_messages(chat_session, pg_db):
    msg = save_message(
        session_id=chat_session.session_id,
        role="user",
        content="test",
        db=pg_db
    )

    delete_session(chat_session.session_id, pg_db)
    assert pg_db.get(ChatMessage, msg.message_id) is None


