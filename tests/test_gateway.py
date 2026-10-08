from app.cache.cache import CacheService
from app.api.chat import chat_with_llm
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.gateway.gateway import handle


def test_gateway():
    req = ChatRequest(
        llm_model="gpt_luna_pro",
        prompt="What is redis"
    )

    response = handle(request=req)
    assert response.response != " "