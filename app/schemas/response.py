from pydantic import BaseModel 

class ChatResponse:
    response: str 
    cache_hit: bool 
    similarity_score: float | None = None 
    latency_ms: float | None 