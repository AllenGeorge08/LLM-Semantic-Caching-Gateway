from app.cache.cache import CacheService
from app.schemas.request import ChatRequest


cache = CacheService()

def test_cache_hit():
    cache.store(
        "What is redis",
        "Redis is an in memory database"
    )

    request = ChatRequest(
        prompt = "What is redis"
    )

    result = cache.check(request)
    print(f"Result: {result}")
    assert result is not None


def test_cache_miss():
    request = ChatRequest(
        prompt="What is an school and what do we do there"
    )

    result = cache.check(request)
    assert result == []



def test_score_and_check():
    cache.store(
            "What is redis",
            "Redis is an in memory database"
        )
    
    request = ChatRequest(
            prompt = "What's redis"
        )
    
    result = cache.check(request)
    print(f"Result: {result}")
    assert result is not None
    