from sqlalchemy.orm import Session
from models import DocumentChunk, UploadedDocument
from services import AIService
from pypdf import PdfReader
from docx import Document
from pathlib import Path
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

def load_pdf(path: str):
    reader = PdfReader(path)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def load_docx(path: str):
    doc = Document(path)

    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def load_document(path: str):
    ext = Path(path).suffix.lower()

    if ext == ".txt":
        return load_text_file(path)
    elif ext == ".md":
        return load_text_file(path)
    elif ext == ".pdf":
        return load_pdf(path)
    elif ext == ".docx":
        return load_docx(path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")

def delete_documents(db: Session, document_id: str):
    document = db.get(UploadedDocument, document_id)

    if document:
        db.delete(document)
        db.commit()


def process_and_save_chunks(db: Session, path: str, document_id):
    logger.info(f"Starting processing for file: {path}")

    try:
        text = load_document(path)
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