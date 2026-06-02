from sqlalchemy.orm import Session
from models import DocumentChunk, UploadedDocument
from services import AIService
from pypdf import PdfReader
from docx import Document
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def chunk_text(text: str,  chunk_size: int = 3, overlap: int = 1) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk_size")

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(lines), step):
        chunk = lines[i:i + chunk_size]
        if chunk:
            chunks.append("\n".join(chunk))

        if i + chunk_size >= len(lines):
            break

    return chunks

def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_pdf(path: str) -> str:
    reader = PdfReader(path)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def load_docx(path: str) -> str:
    doc = Document(path)

    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

LOADERS = {
    ".txt": load_text_file,
    ".md": load_text_file,
    ".pdf": load_pdf,
    ".docx": load_docx,
}

def load_document(path: str) -> str:
    ext = Path(path).suffix.lower()

    try:
        return LOADERS[ext](path)
    except KeyError:
        raise ValueError(f"Unsupported file type: {ext}")

def delete_documents(db: Session, document_id: str) -> None:
    document = db.get(UploadedDocument, document_id)
    if document:
        Path(document.path).unlink(missing_ok=True)
        db.delete(document)
        db.commit()


def process_and_save_chunks(db: Session, path: str, document_id, ai_service: AIService) -> int:
    logger.info(f"Starting processing for file: {path}")

    try:
        text = load_document(path)
        chunks = chunk_text(text)
        logger.info(f"File loaded and split into {len(chunks)} chunks.")

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
                    logger.exception(f"Failed to process chunk {index}")
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