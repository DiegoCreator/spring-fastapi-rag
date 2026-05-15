import pytest
import os
from unittest.mock import patch, MagicMock
from services import AIService, Document

def test_missing_api_key():
    with patch.dict(os.environ, {}, clear=True):
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
    ai_service.generate_answer("", "")
    ai_service.generate_answer("", "")
    lenght = len(ai_service.answer_cache)

    assert lenght == 1, f"Expected one, but got {lenght}"

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key_for_testing"})
@patch('services.genai.GenerativeModel')
def test_prompt(mock_model_class):
    ai_service = AIService()
    ai_service.llm_model.generate_content.return_value.text = "I'm sorry, but I don't have enough information to answer this question."
    response = ai_service.generate_answer("When was Microsoft founded?", "Apple was founded in 1976")

    assert "I'm sorry" in response

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key_for_testing"})
def test_api_error_handling():
    ai_service = AIService()
    ai_service.llm_model = MagicMock()
    ai_service.llm_model.generate_content.side_effect = Exception("Error")
    result = ai_service.generate_answer("question", "context")

    assert result == "An error occurred while generating the response"

@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
def test_similarity_search_logic(db):
    ai_service = AIService()

    cat_vector = [1.0] + [0.0] * 383
    dog_vector = [0.0, 1.0] + [0.0] * 382

    doc1 = Document(id=1, content="About cats", embedding=cat_vector)
    doc2 = Document(id=2, content="About dogs", embedding=dog_vector)

    mock_query = db.query = MagicMock()
    mock_query.return_value.order_by.return_value.limit.return_value.all.return_value = [doc1, doc2]

    db.add_all([doc1, doc2])
    db.commit()

    query_vec = [0.9, 0.1] + [0.0] * 382
    results = ai_service.similarity_search(query_vec, db, k=1)

    assert results[0].content == "About cats"

