from fastapi import FastAPI, Request
from fastapi.params import Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from services import AIService
from database import get_db
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from ingestion import process_and_save_chunks
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"Received question: {ask_req.question} from {request.client.host}")

    try:

        query_embedding = ai_service.get_embedding(ask_req.question)

        results = ai_service.similarity_search(query_embedding, db)
        logger.info(f"Retrieved {len(results)} chunks from DB")

        if not results:
            logger.warning(f"No context found for query: {ask_req.question}")
            return AskResponse(
                answer="No relevant documents found",
                sources=[]
            )

        context = "\n".join([doc.content for doc in results])
        answer = ai_service.generate_answer(ask_req.question, context)
        logger.info("Answer generated successfully")

        return {"answer": answer, "sources": [d.content[:100] for d in results]}

    except Exception as e:
        logger.error(f"Error in /ask endpoint: {str(e)}", exc_info=True)
        raise

@app.post("/ingest")
def ingest_api(file_path: str, db: Session = Depends(get_db)):
    count = process_and_save_chunks(db, file_path)

    return {"message": f"Processed {count} chunks."}