import os
import uuid
from fastapi import FastAPI, Request, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from cors_config import setup_cors
from models import UploadedDocument, DocumentChunk
from services import AIService
from database import get_db, Base, get_engine
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

setup_cors(app)

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

engine = get_engine()

Base.metadata.create_all(bind=engine)

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

@app.post("/upload")
async def upload_file(file: UploadFile = File(), db: Session = Depends(get_db)):
    file_id = str(uuid.uuid4())

    path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"

    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)

    uploaded_doc = UploadedDocument(id=file_id, filename=file.filename, path=path)

    db.add(uploaded_doc)
    db.commit()

    chunks_count = process_and_save_chunks(db, path, uploaded_doc.id)

    return  {
        "file_id": file_id,
        "filename": file.filename,
        "path": path,
        "chunks_saved": chunks_count
    }
@app.post("/ingest")
def ingest_api(file_path: str, db: Session = Depends(get_db)):
    count = process_and_save_chunks(db, file_path, document_id=None)

    return {"message": f"Processed {count} chunks."}