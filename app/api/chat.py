from schemas.request import ChatRequest
from gateway.gateway import handle  
from fastapi import APIRouter , HTTPException,Query,status



chat_router = APIRouter(prefix="api/v1/",tags=["query"])

@chat_router.post("/v1/chat/completions")
def chat_with_llm(request: ChatRequest):
   
    return handle(request)
