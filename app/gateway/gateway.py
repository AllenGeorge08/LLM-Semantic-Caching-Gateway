from schemas.request import  ChatRequest
from cache.cache import CacheService
from cache.cache import CacheService


def handle(request: ChatRequest):
    cache = CacheService()

    cached = cache.get_or_set(request.prompt)
    return cached 


   