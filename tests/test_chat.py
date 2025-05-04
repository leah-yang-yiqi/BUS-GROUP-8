# Conduct positive and negative cases for AI section
import pytest

def test_chat_positive(client):
    from app import get_AIModel
    tokenizer, model = get_AIModel()

    input_text = "Hello, could you give me steps on how students enroll in courses at the University of Birmingham?"
    history = []
    response, updated_history = model.chat(tokenizer, input_text, history)

    print("AI Response:", response)

    assert isinstance(response, str)
    assert "enroll" in response.lower() or "course" in response.lower() or len(response) > 20


def test_chat_negative(client):
    from app import get_AIModel
    tokenizer, model = get_AIModel()

    input_text = ""
    history = []

    try:
        response, updated_history = model.chat(tokenizer, input_text, history)
        print("AI Response (Empty Input):", response)
        assert isinstance(response, str)
        assert len(response.strip()) > 0
    except Exception as e:
        pytest.fail(f"Model failed on empty input: {e}")



