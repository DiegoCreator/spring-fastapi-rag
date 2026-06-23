import uuid
from pathlib import Path
from database import get_db
import os
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app, get_ai_service, AskResponse
from unittest.mock import patch

from models import UploadedDocument

client = TestClient(app)

def test_ask_endpoint_returns_answer_and_sources():
    mock_ai_service = MagicMock()
    mock_db = MagicMock()
    mock_ai_service.get_embedding.return_value = [0.1, 0.2, 0.3]

    mock_chunk = MagicMock()
    mock_chunk.document_id = 1
    mock_chunk.id = 2
    mock_chunk.content = "FastAPI is a modern Python web framework"

    mock_ai_service.similarity_search.return_value = [mock_chunk]

    mock_ai_service.generate_answer.return_value = "FastAPI is a modern Python web framework"

    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "question": "What is FastAPI?",
        "session_id": str(uuid.uuid4())
    }

    expected_sources = [
        {
            "documents_id": "1",
            "chunk_id": "2",
        }
    ]

    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "FastAPI is a modern Python web framework"
    assert data["sources"] == expected_sources

    app.dependency_overrides.clear()


def test_ask_endpoint_no_context():
    mock_ai_service = MagicMock()
    mock_db = MagicMock()
    mock_ai_service.get_embedding.return_value = [0.1, 0.2, 0.3]
    mock_ai_service.similarity_search.return_value = []

    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "question": "What is FastAPI?",
        "session_id": str(uuid.uuid4())
    }

    response = client.post("/ask", json=payload)

    data = response.json()
    assert data["answer"] == "No relevant documents found"
    assert data["sources"] == []

    app.dependency_overrides.clear()

def test_ask_endpoint_response_matches_ask_response_schema():
    mock_ai_service = MagicMock()
    mock_db = MagicMock()
    mock_ai_service.get_embedding.return_value = [0.1, 0.2, 0.3]
    mock_ai_service.similarity_search.return_value = []

    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/ask",
        json={
            "question": "FastAPI?",
            "session_id": str(uuid.uuid4())
        }
    )

    data = response.json()
    AskResponse.model_validate(data)

    app.dependency_overrides.clear()

def test_upload_file_success(db, tmp_path):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with patch("main.UPLOAD_DIR", str(tmp_path)):
        with patch("main.process_and_save_chunks") as mock_process:
            mock_process.return_value = 3

            file_content = b"test"
            file_name = "test_document.txt"

            response = client.post("/upload", files={"file": (file_name, file_content, "text/plain")})

            assert response.status_code == 200
            data = response.json()

            assert data["filename"] == file_name
            assert data["chunks_saved"] == 3
            assert "file_id" in data

            mock_process.assert_called_once()

            assert os.path.exists(data["path"])

    app.dependency_overrides.clear()

def test_upload_file_creates_document_record(db, tmp_path):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with patch("main.UPLOAD_DIR", str(tmp_path)):
        with patch("main.process_and_save_chunks") as mock_process:
            mock_process.return_value = 3

            file_content = b"test"
            file_name = "test_document.txt"

            response = client.post("/upload", files={"file": (file_name, file_content, "text/plain")})

            data = response.json()

            try:
                document = (db.query(UploadedDocument).filter(UploadedDocument.id == uuid.UUID(data["file_id"])).first())

                assert document is not None
                assert document.filename == file_name
            finally:
                db.close()

    app.dependency_overrides.clear()

def  test_upload_cannot_escape_upload_directory(db, tmp_path):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with patch("main.UPLOAD_DIR", str(tmp_path)):
        with patch("main.process_and_save_chunks") as mock_process:
            mock_process.return_value = 3

            malicious_name = "../../../etc/passwd"
            file_content = b"test"

            response = client.post("/upload", files={"file": (malicious_name, file_content, "text/plain")})

            data = response.json()

            saved_path = Path(data["path"]).resolve()
            assert saved_path.parent == tmp_path.resolve()

    app.dependency_overrides.clear()

def test_upload_file_accepts_unusual_filenames(db, tmp_path):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with patch("main.UPLOAD_DIR", str(tmp_path)):
        with patch("main.process_and_save_chunks") as mock_process:
            mock_process.return_value = 3

            file_content = b"test"
            file_name = "‽§¶#.txt"

            response = client.post("/upload", files={"file": (file_name, file_content, "text/plain")})

            data = response.json()
            saved_path = Path(data["path"])


            assert data["filename"] == file_name
            assert saved_path.exists()

    app.dependency_overrides.clear()

