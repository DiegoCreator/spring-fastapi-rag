import os
import uuid
from fastapi import FastAPI, Request, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from cors_config import setup_cors
from models import UploadedDocument
from services import AIService
from database import get_db, Base, get_engine
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from ingestion import process_and_save_chunks, delete_documents
from sqlalchemy import select
from contextlib import asynccontextmanager
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

setup_cors(app)

class AskRequest(BaseModel):
    question: str

class SourceItem(BaseModel):
    documents_id: str
    chunk_id: str

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem]


def get_ai_service() -> AIService:
    return AIService()

# ====== ENDPOINT ======
@app.post("/ask", response_model=AskResponse)
@limiter.limit("5/minute")
def ask(request: Request, ask_req: AskRequest, db: Session = Depends(get_db), ai_service: AIService = Depends(get_ai_service)):
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

        return {"answer": answer, "sources": [{"documents_id": str(d.document_id), "chunk_id": str(d.id)} for d in results]}

    except Exception as e:
        logger.exception(f"Error in /ask endpoint: {str(e)}", exc_info=True)
        raise

@app.post("/upload")
async def upload_file(file: UploadFile = File(), db: Session = Depends(get_db), ai_service: AIService = Depends(get_ai_service)) -> dict:
    file_id = str(uuid.uuid4())

    safe_name = Path(file.filename).name

    path = f"{UPLOAD_DIR}/{file_id}_{safe_name}"

    with open(path, "wb") as f:
        f.write(file.file.read())

    uploaded_doc = UploadedDocument(id=file_id, filename=file.filename, path=path)

    db.add(uploaded_doc)
    db.commit()

    chunks_count = process_and_save_chunks(db, path, uploaded_doc.id, ai_service=ai_service)

    return  {
        "file_id": file_id,
        "filename": file.filename,
        "path": path,
        "chunks_saved": chunks_count
    }

@app.post("/ingest")
def ingest_api(file_path: str, db: Session = Depends(get_db), ai_service: AIService = Depends(get_ai_service)):
    count = process_and_save_chunks(db, file_path, document_id=None, ai_service=ai_service)

    return {"message": f"Processed {count} chunks."}

@app.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    return delete_documents(db, document_id)

@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    documents = db.scalars(select(UploadedDocument)).all()

    return [
        {"id": doc.id, "filename": doc.filename}
        for doc in documents
    ]