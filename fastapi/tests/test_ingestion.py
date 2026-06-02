import pytest
from services import AIService
from ingestion import chunk_text, load_text_file, process_and_save_chunks
from unittest.mock import patch, MagicMock
from models import DocumentChunk, UploadedDocument
import uuid

ai_service = AIService()

@pytest.mark.parametrize("input_text, expected_output", [
    ("Hello\nWorld", ["Hello", "World"]),
    ("Line 1\n\nLine 2\n \nLine 3", ["Line 1", "Line 2", "Line 3"]),
    ("  trimmed  \n  space  ", ["trimmed", "space"]),
    ("", []),
    ("\n  \n\n", []),
])

def test_chunk_text_logic(input_text, expected_output):
    assert chunk_text(input_text) == expected_output

def test_load_text_file_empty_file():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            load_text_file("any_name.txt")
def test_load_text_file_permission_denied():
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError) as excinfo:
            load_text_file("protected_file.txt")

        assert "Permission denied" in str(excinfo.value)

def test_load_text_file_utf8(tmp_path):
    content = "Héllò World! 🌍"
    file_path = tmp_path / "test_utf8.txt"

    file_path.write_text(content, encoding="utf-8")

    result = load_text_file(str(file_path))
    assert result == content

def test_load_text_file_encoding_mismatch(tmp_path):
    content = "Some text"
    file_path = tmp_path / "test_utf16.txt"

    with open(file_path, "w", encoding="utf-16") as f:
        f.write(content)

    with pytest.raises(UnicodeDecodeError):
        load_text_file(str(file_path))

def test_process_and_save_chunks_workflow():
    mock_db = MagicMock()
    mock_ai = MagicMock()
    mock_ai.get_embedding.return_value = [0.1, 0.2, 0.3]

    with patch("ingestion.load_text_file") as mock_load:
        with patch("ingestion.AIService", return_value=mock_ai):
            mock_load.return_value = "Line 1\nLine 2"

            count = process_and_save_chunks(mock_db, "file_path.txt", DocumentChunk.id, ai_service=ai_service)

            assert count == 2
            assert mock_db.add.call_count == 2
            mock_db.commit.assert_called_once()

def test_process_and_save_chunks_integration(pg_db, tmp_path):
    test_file = tmp_path / "data.txt"
    test_file.write_text("First Chunk\nSecond Chunk")

    uploaded_doc = UploadedDocument(
        id=uuid.uuid4(),
        filename="data.txt",
        path=str(tmp_path)
    )

    pg_db.add(uploaded_doc)
    pg_db.commit()

    with patch("ingestion.AIService") as MockService:
        instance = MockService.return_value

        instance.get_embedding.return_value = [0.1] * 384

        count = process_and_save_chunks(pg_db, str(test_file), uploaded_doc.id, ai_service=ai_service)

        assert count == 2

        saved_docs = pg_db.query(DocumentChunk).all()
        assert len(saved_docs) == 2
        assert saved_docs[0].content == "First Chunk"
        assert saved_docs[1].content == "Second Chunk"
        assert len(saved_docs[0].embedding) == 384

