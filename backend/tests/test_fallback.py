import os
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("GEMINI_API_KEY", "test-key-not-used-in-this-test")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
client.__enter__()


def test_out_of_corpus_fallback():
    with patch("app.routers.chat.complete") as mock_complete:
        mock_complete.return_value = "This is a general knowledge answer about dal recipes."

        response = client.post("/chat", json={"message": "xyzqwert12345 recipe for dal", "language": "English"})
        assert response.status_code == 200
        data = response.json()

        messages = data.get("messages", [])
        assert len(messages) >= 2
        assistant_msg = messages[-1]
        assert assistant_msg["role"] == "assistant"
        assert assistant_msg["content"] == "This is a general knowledge answer about dal recipes."
        assert assistant_msg["sources"] == [{"fallback": True, "provider": "gemini"}]

        mock_complete.assert_called_once()


def test_in_corpus_rag_path():
    with patch("app.routers.chat.complete") as mock_complete:
        mock_complete.return_value = "Aadhaar is a 12-digit biometric ID under Aadhaar Act, 2016."

        response = client.post("/chat", json={"message": "aadhaar", "language": "English"})
        assert response.status_code == 200
        data = response.json()

        messages = data.get("messages", [])
        assert len(messages) >= 2
        assistant_msg = messages[-1]
        assert assistant_msg["role"] == "assistant"
        assert assistant_msg["content"] == "Aadhaar is a 12-digit biometric ID under Aadhaar Act, 2016."
        assert len(assistant_msg["sources"]) > 0
        assert "act_name" in assistant_msg["sources"][0]
        assert "section" in assistant_msg["sources"][0]

        mock_complete.assert_called_once()
