from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str 
    stream: bool = False
    temperature: float = 0.7

