import pytest
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models import Document
from unittest.mock import patch

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
def test_document_creation(pg_db: Session):
    sample_content = "This is a string"
    sample_embedding = [0.1, 0.2, 0.3] * 128

    new_doc = Document(embedding=sample_embedding, content=sample_content)

    pg_db.add(new_doc)
    pg_db.commit()

    pg_db.expire_all()

    retrieved = pg_db.query(Document).filter_by(id=new_doc.id).first()

    assert retrieved is not None
    assert retrieved.id is not None
    assert retrieved.content == sample_content

    assert list(retrieved.embedding) == sample_embedding

def test_document_content_required(pg_db: Session):
    valid_embedding = [0.1] * 384
    new_doc = Document(embedding=valid_embedding, content=None)

    pg_db.add(new_doc)
    with pytest.raises(IntegrityError):
        pg_db.flush()

    pg_db.rollback()

def test_vector_similarity_search(pg_db: Session):
    vecA = Document(content="Quantum psyhics is complex", embedding=[0.9] * 384)
    vecB = Document(content="Oil painting on canvas", embedding=[0.1] * 384)

    pg_db.add_all([vecA, vecB])
    pg_db.commit()

    vec_query = [0.85] * 384
    results = pg_db.query(Document).order_by(Document.embedding.l2_distance(vec_query)).limit(1).all()

    assert len(results) == 1
    assert "psyhics" in results[0].content
