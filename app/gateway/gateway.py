from schemas.request import  ChatRequest
from cache.cache import CacheService
from cache.cache import CacheService


cache = CacheService()

def handle(request: ChatRequest):
    cached = cache.get_or_set(request.prompt)
    return cached 


   