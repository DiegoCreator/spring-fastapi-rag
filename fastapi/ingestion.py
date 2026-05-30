from sqlalchemy.orm import Session
from models import DocumentChunk, UploadedDocument
from services import AIService
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

def delete_documents(db: Session, document_id: str):
    document = db.get(UploadedDocument, document_id)

    if document:
        db.delete(document)
        db.commit()


def process_and_save_chunks(db: Session, path: str, document_id):
    logger.info(f"Starting processing for file: {path}")

    try:
        text = load_text_file(path)
        chunks = chunk_text(text)
        logger.info(f"File loaded and split into {len(chunks)} chunks.")

        ai_service = AIService()

        saved_chunks = 0

        for index, chunk in enumerate(chunks):
            with db.begin_nested():
                try:
                    embedding = ai_service.get_embedding(chunk)
                    doc = DocumentChunk(document_id=document_id, chunk_index=index, content=chunk, embedding=embedding)
                    db.add(doc)
                    db.flush()
                    saved_chunks += 1
                except Exception as e:
                    logger.error(f"Failed to process chunk {index}: {e}")
                    continue

        db.commit()
        logger.info(f"Successfully saved {saved_chunks} chunks to the database.")
        return saved_chunks

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise

    except Exception as e:
        logger.critical(f"Unexpected error processing {path}: {e}")
        raise