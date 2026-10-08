from app.schemas.request import ChatRequest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fastapi_route():
    request = ChatRequest(
        llm_model="gpt-oss-120b", prompt="Teach me pythagoras theorem with an example"
    )

    response = client.post(
        "/api/v1/chat/completions",
        json=request.model_dump(),  # to generate a dictionary repr of the model
    )
    print(response.status_code, response.json())
    assert response.status_code == 200