from uuid import UUID
from models import ChatMessage, ChatSession
from sqlalchemy.orm import Session
from sqlalchemy import select

def sliding_window(session_id: UUID, db: Session, limit = 6):

    query = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.desc()).limit(limit)
    result = db.execute(query)
    messages = list(result.scalars().all())
    return messages[::-1]

def save_message(session_id: UUID, role: str, content: str, db: Session, embedding: list[float] | None = None):
    new_message = ChatMessage(session_id=session_id, role=role, content=content, embedding=embedding)

    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def semantic_search(session_id: UUID, embedding: list[float], limit: int, db: Session):
    query = select(ChatMessage).where(ChatMessage.session_id == session_id).where(ChatMessage.role == "user").where(ChatMessage.embedding.is_not(None)).order_by(
        ChatMessage.embedding.cosine_distance(embedding)).limit(limit)

    result = db.execute(query)
    return list(result.scalars().all())

def delete_session(session_id: UUID, db: Session) -> None:
    chat_session = db.get(ChatSession, session_id)
    if chat_session:
        db.delete(chat_session)
        db.commit()