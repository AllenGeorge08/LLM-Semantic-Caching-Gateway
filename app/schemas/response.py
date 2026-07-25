from pydantic import BaseModel 

class ChatResponse(BaseModel):
    response: str 
    cache_hit: bool 
    similarity_score: float | None = None 
    cache_latency: float 
    llm_latency: float 