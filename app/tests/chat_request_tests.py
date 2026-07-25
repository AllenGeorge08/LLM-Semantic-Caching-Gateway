from app.cache.cache import CacheService
from app.schemas.request import ChatRequest
from app.api.chat import chat_with_llm
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fastapi_route():
    response = client.post(
        "/api/v1/chat/completions",
        json={
            "prompt": "What is a database and why is it used"
        }
    )

    assert response.status_code == 200
   
