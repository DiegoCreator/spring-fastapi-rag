from database import Base, EMBEDDING_DIM
from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector

class Document(Base):
    """
    A database model representing a single text fragment
    along with its vector representation.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))