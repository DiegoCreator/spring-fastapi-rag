from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from database import Base, EMBEDDING_DIM
from sqlalchemy import Column, Integer, Text, UUID, ForeignKey, String, DateTime
from pgvector.sqlalchemy import Vector
class DocumentChunk(Base):
    """
    A database model representing a single text fragment
    along with its vector representation.
    """

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id"))
    chunk_index = Column(Integer)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))
    document = relationship("UploadedDocument", back_populates="chunks")

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(UUID(as_uuid=True), primary_key=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete"
    )