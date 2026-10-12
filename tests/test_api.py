import sys

from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.schemas.chat import ChatResponse, Citation

client = TestClient(app)

def test_openapi_endpoint_returns_request_id():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 36

def test_chat_returns_answer_and_request_id():
    fake_response = ChatResponse(
        answer="You can reset your password from login page",
        confidence=0.92,
        Citations=[],
        tools_used=[],
    )

    with patch(
        "app.api.routes.generate_answer",
        return_value=fake_response,
    ) as mock_generate:
        response = client.post(
            "/api/v1/chat",
            json={"message": "How can I reset my password?"},
        )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "You can reset your password from login page"
    )
    assert "X-Request-ID" in response.headers

    mock_generate.assert_called_once()
    assert (
        mock_generate.call_args.kwargs["question"] == "How can I reset my password?"
    )
    assert mock_generate.call_args.kwargs["request_id"]

def test_chat_returns_fallback_response():
    fake_response = ChatResponse(
        answer="I'm sorry. I don't have enough information to answer that question",
        confidence=0.0,
        citations=[],
        tools_used=[],
    )

    with patch(
        "app.api.routes.generate_answer",
        return_value=fake_response,
    ):
        response = client.post(
            "/api/v1/chat",
            json={"message": "How do I make sushi?"},
        )

    assert response.status_code == 200
    assert response.json()["confidence"] == 0.0
    assert response.json()["citations"] == []
    assert "X-Request-ID" in response.headers


# pytest tests/test_api.py -v