from sqlalchemy.orm import Session
from models import Document
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


def process_and_save_chunks(db: Session, path: str):
    logger.info(f"Starting processing for file: {path}")

    try:

        text = load_text_file(path)
        chunks = chunk_text(text)
        logger.info(f"File loaded and split into {len(chunks)} chunks.")

        ai_service = AIService()

        for chunk in chunks:
            try:
                embedding = ai_service.get_embedding(chunk)
                doc = Document(content=chunk, embedding=embedding)
                db.add(doc)
            except Exception as e:
                logger.error(f"Failed to process chunk: {e}")
                continue

        db.commit()
        logger.info(f"Successfully saved {len(chunks)} chunks to the database.")
        return len(chunks)

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error processing {path}: {e}")
        db.rollback()
        raise