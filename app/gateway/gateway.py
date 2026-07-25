from app.schemas.request import  ChatRequest
from app.cache.cache import CacheService


cache = CacheService()

def handle(request: ChatRequest):
    cached = cache.get_or_set(request)
    return cached 


   