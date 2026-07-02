from uuid import uuid4
import pytest
import os
from unittest.mock import patch, MagicMock
from services import AIService, DocumentChunk, update_session_title

def test_missing_api_key():
    with patch('services.load_dotenv'), patch.dict(os.environ, {}, clear=True):

        with pytest.raises(ValueError) as excinfo:
            AIService()

        assert "API key missing" in str(excinfo.value)

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key_for_testing"})
def test_get_embedding_dimensions():
    ai_service = AIService()
    embedding = ai_service.get_embedding("Hello World")

    assert isinstance(embedding, list), "The embedding should be a Python list."
    assert len(embedding) == 384, f"Expected 384 dimensions, but got {len(embedding)}"
    assert isinstance(embedding[0], float), "The embedding elements should be floats"

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key_for_testing"})
def test_cache():
    ai_service = AIService()
    ai_service.llm_model = MagicMock()
    ai_service.generate_answer("", "", [], "")
    ai_service.generate_answer("", "", [], "")
    lenght = len(ai_service.answer_cache)

    assert lenght == 1, f"Expected one, but got {lenght}"

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key_for_testing"})
@patch('services.genai.GenerativeModel')
def test_prompt(mock_model_class):
    ai_service = AIService()
    ai_service.llm_model.generate_content.return_value.text = "I'm sorry, but I don't have enough information to answer this question."
    response = ai_service.generate_answer("When was Microsoft founded?", "Apple was founded in 1976", [], "")

    assert "I'm sorry" in response

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key_for_testing"})
def test_api_error_handling():
    ai_service = AIService()
    ai_service.llm_model = MagicMock()
    ai_service.llm_model.generate_content.side_effect = Exception("Error")
    result = ai_service.generate_answer("question", "context", [], "")

    assert result == "An error occurred while generating the response"

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
def test_similarity_search_logic(db):
    ai_service = AIService()

    cat_vector = [1.0] + [0.0] * 383
    dog_vector = [0.0, 1.0] + [0.0] * 382

    doc1 = DocumentChunk(id=1, content="About cats", embedding=cat_vector)
    doc2 = DocumentChunk(id=2, content="About dogs", embedding=dog_vector)

    mock_query = db.query = MagicMock()
    mock_query.return_value.order_by.return_value.limit.return_value.all.return_value = [doc1, doc2]

    db.add_all([doc1, doc2])
    db.commit()

    query_vec = [0.9, 0.1] + [0.0] * 382
    results = ai_service.similarity_search(query_vec, db, k=1)

    assert results[0].content == "About cats"

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
def test_generate_title_returns_max_4_words():
    ai_service = AIService()
    mock_response = MagicMock()
    mock_response.text = "FastAPI short title"
    ai_service.title_generator_model.generate_content = MagicMock(return_value=mock_response)
    first_question = "What is FastAPI"
    result = ai_service.generate_title(first_question)

    assert len(result.split()) <= 4

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
def test_generate_title_removes_quotes_and_punctuation():
    ai_service = AIService()
    mock_response = MagicMock()
    mock_response.text = "FastAPI short title:."
    ai_service.title_generator_model.generate_content = MagicMock(return_value=mock_response)
    first_question = "What is FastAPI"
    result = ai_service.generate_title(first_question)

    assert result == "FastAPI short title"

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
def test_update_session_title_task_updates_title_successfully():
    mock_ai_service = MagicMock()
    session_id = uuid4()
    first_question = "How do I learn Python?"
    generated_title = "Python Learning Guide"
    mock_ai_service.generate_title.return_value = generated_title
    mock_session = MagicMock()
    mock_db = MagicMock()
    mock_db.scalar.return_value = mock_session

    update_session_title(session_id, first_question, mock_ai_service, mock_db)

    mock_ai_service.generate_title.assert_called_once_with(first_question)
    assert mock_session.title == generated_title
    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_not_called()

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
def test_update_session_title_task_does_nothing_when_session_not_found():
    mock_ai_service = MagicMock()
    mock_db = MagicMock()
    session_id = uuid4()
    mock_ai_service.generate_title.return_value = "Some Title"

    mock_db.scalar.return_value = None

    update_session_title(session_id, "Hello", mock_ai_service, mock_db)

    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_not_called()

def test_update_session_title_task_rolls_back_when_ai_service_fails():
    mock_ai_service = MagicMock()
    mock_db = MagicMock()
    session_id = uuid4()
    mock_ai_service.generate_title.side_effect = Exception("API Timeout")

    with patch("services.logger") as mock_logger:
        update_session_title(session_id, "Hello", mock_ai_service, mock_db)

        mock_db.rollback.assert_called_once()
        mock_db.commit.assert_not_called()
        mock_logger.error.assert_called_once()

def test_update_session_title_task_rolls_back_when_commit_fails():
    mock_ai_service = MagicMock()
    session_id = uuid4()
    mock_ai_service.generate_title.return_value = "Title"
    mock_db = MagicMock()
    mock_session = MagicMock()

    mock_db.scalar.return_value = mock_session
    mock_db.commit.side_effect = Exception("Database disk full")

    with patch("services.logger") as mock_logger:
        update_session_title(session_id, "Hello", mock_ai_service, mock_db)

        mock_db.rollback.assert_called_once()
        mock_logger.error.assert_called_once()
