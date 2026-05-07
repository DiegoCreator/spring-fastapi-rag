import os

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from dotenv import load_dotenv
import google.generativeai as genai

# ====== CONFIG ======
DATABASE_URL = os.getenv("DATABASE_URL")

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
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

model = genai.GenerativeModel("models/gemini-2.5-flash")

def get_embedding(text: str) -> List[float]:
    return embedding_model.encode(text).tolist()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

answer_cache = {}

# ====== ENDPOINT ======
@app.post("/ask", response_model=AskResponse)
@limiter.limit("5/minute")
def ask(request: Request, ask_req: AskRequest):
    db = SessionLocal()
    try:
        query_embedding = get_embedding(ask_req.question)

        results = similarity_search(query_embedding, db)

        if not results:
            return AskResponse(
                answer="No relevant documents found",
                sources=[]
            )

        context = "\n".join([doc.content for doc in results])

        prompt = f"""
        You are a helpful assistant. Answer the user's question below using only the information (context) provided.
        If the provided context doesn't answer, reply:
        "I'm sorry, but I don't have enough information to answer this question."
        
        Context:
        {context}
        
        User Question:
        {ask_req.question}
        """

        if ask_req.question in answer_cache:
            return answer_cache[ask_req.question]

        response = model.generate_content(prompt)

        answer_text = response.text

        answer_cache[ask_req.question] = AskResponse(answer=answer_text, sources=[doc.content[:100] for doc in results])

        return answer_cache[ask_req.question]

    finally:
        db.close()

@app.post("/seed")
def seed():
    db = SessionLocal()

    texts = [
        "Machine learning is a field of AI",
        "FastAPI is a modern Python web framework",
        "Spring Boot is used for Java backend"
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