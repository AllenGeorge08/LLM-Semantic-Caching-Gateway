from app.schemas.request import ChatRequest
from app.gateway.gateway import handle


def test_gateway():
    req = ChatRequest(llm_model="gpt_luna_pro", prompt="What is redis")

    response = handle(request=req)
    assert response.response != " "
