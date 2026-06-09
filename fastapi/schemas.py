from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class ChatMessageOut(BaseModel):
    message_id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True