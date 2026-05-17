from sqlalchemy.orm import Session
from models import Document
from services import AIService

def chunk_text(text: str):
    chunks = [
        chunk.strip()
        for chunk in text.split("\n")
        if chunk.strip()
    ]

    return chunks

def load_text_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def process_and_save_chunks(db: Session, path: str):
    text = load_text_file(path)
    chunks = chunk_text(text)
    ai_service = AIService()

    for chunk in chunks:
        embedding = ai_service.get_embedding(chunk)
        doc = Document(content=chunk, embedding=embedding)
        db.add(doc)

    db.commit()
    return len(chunks)