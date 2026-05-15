import pytest
from sqlalchemy import text

def test_database_connection_and_vector_support(pg_db):
    result = pg_db.execute(text("SELECT 1")).scalar()
    assert result == 1

    vector_version = pg_db.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")).scalar()
    assert vector_version is not None

def test_vector_dimension_enforcement(pg_db):
    pg_db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

    pg_db.execute(text("CREATE TABLE IF NOT EXISTS test_vectors (vec vector(384));"))
    pg_db.commit()

    valid_vec = "[" + ",".join(["0"] * 384) + "]"
    pg_db.execute(text("INSERT INTO test_vectors (vec) VALUES (:v)"), {"v": valid_vec})

    invalid_vec = "[0,0,0]"
    with pytest.raises(Exception):
        pg_db.execute(text("INSERT INTO test_vectors (vec) VALUES (:v)"), {"v": invalid_vec})