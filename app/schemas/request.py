from pydantic import BaseModel


class ChatRequest(BaseModel):
    llm_model: str
    prompt: str
    stream: bool = False
    temperature: float = 0.7
