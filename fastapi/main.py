from fastapi import FastAPI, Request
from fastapi.params import Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import logging
from services import AIService
from database import get_db
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from models import Document

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]

ai_service = AIService()

# ====== ENDPOINT ======
@app.post("/ask", response_model=AskResponse)
@limiter.limit("5/minute")
def ask(request: Request, ask_req: AskRequest, db: Session = Depends(get_db)):
    query_embedding = ai_service.get_embedding(ask_req.question)

    results = ai_service.similarity_search(query_embedding, db)

    if not results:
        return AskResponse(
            answer="No relevant documents found",
            sources=[]
        )

    context = "\n".join([doc.content for doc in results])

    answer = ai_service.generate_answer(ask_req.question, context)

    return {"answer": answer, "sources": [d.content[:100] for d in results]}



@app.post("/seed")
def seed(db: Session = Depends(get_db)):

    texts = [
        "Machine learning is a field of AI",
        "FastAPI is a modern Python web framework",
        "Spring Boot is used for Java backend"
    ]

    try:
        for text in texts:
            emb = ai_service.get_embedding(text)
            doc = Document(content=text, embedding=emb)
            db.add(doc)
    except Exception as e:
        logging.error(f"Error with sentence '{text}': {e}")
        db.rollback()
        db.commit()

    return {"status": "seeded"}