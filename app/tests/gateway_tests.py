from app.cache.cache import CacheService
from app.api.chat import chat_with_llm
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.providers.deepseek_ollama import get_llm_response
from app.gateway.gateway import handle


def test_gateway():
    req = ChatRequest(
        prompt="What is redis"
    )

    response = handle(request=req)
    assert response.response != " "