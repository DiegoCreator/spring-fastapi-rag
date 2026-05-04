import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector

# ====== CONFIG ======
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/knowledge_base"
)

EMBEDDING_DIM = 384

# ====== DB SETUP ======
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ====== MODEL ======
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    embedding = Column(Vector(EMBEDDING_DIM))

Base.metadata.create_all(bind=engine)

# ====== EMBEDDING MODEL ======

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> List[float]:
    return model.encode(text).tolist()

app = FastAPI()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]

# ====== UTILS ======
def similarity_search(query_embedding, db, k=3):
    results = db.query(Document).order_by(
        Document.embedding.cosine_distance(query_embedding)
    ).limit(k).all()

    return results

# ====== ENDPOINT ======
@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    db = SessionLocal()
    try:
        query_embedding = get_embedding(request.question)

        results = similarity_search(query_embedding, db)

        if not results:
            return AskResponse(
                answer="No relevant documents found",
                sources=[]
            )

        context = "\n".join([doc.content for doc in results])

        answer_text = f"Based on documents:\n{context[:500]}"

        return AskResponse(
            answer=answer_text,
            sources=[doc.content[:100] for doc in results]
        )

    finally:
        db.close()

@app.post("/seed")
def seed():
    db = SessionLocal()

    texts = [
        "Machine learning is a field of AI",
        "FastAPI is a modern Python web framework",
        "Spring Boot is used for Java backend development"
    ]

    for text in texts:
        try:
            emb = get_embedding(text)
            doc = Document(content=text, embedding=emb)
            db.add(doc)
            db.commit()
        except Exception as e:
            print(f"Error with sentence '{text}': {e}")
            db.rollback()

    db.close()

    return {"status": "seeded"}