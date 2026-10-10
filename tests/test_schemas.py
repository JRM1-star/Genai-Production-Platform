import pytest
from pydantic import ValidationError
from app.domain.schemas import ChatRequest

def test_question_validation():
    assert ChatRequest(question="What is this?").question
    with pytest.raises(ValidationError):
        ChatRequest(question="")

def test_question_limit():
    with pytest.raises(ValidationError):
        ChatRequest(question="x" * 4001)
