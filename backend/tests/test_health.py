import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-used-in-this-test")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
client.__enter__()  # trigger startup event (creates tables) for this test session


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
