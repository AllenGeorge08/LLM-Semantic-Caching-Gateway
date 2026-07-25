import os 
import redis
import time 


from sentence_transformers import SentenceTransformer 
from redisvl.utils.vectorize import HFTextVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache 
from redisvl.extensions.cache.llm import SemanticCache
from app.schemas.request import  ChatRequest
from app.schemas.response import ChatResponse
from app.providers.deepseek_ollama import get_llm_response
from app.metrics.evaluation import SemanticCacheEvaluator
from app.config.config import EMBEDDING_MODEL,TTL,DISTANCE_THRESHOLD

encoder = SentenceTransformer("all-mpnet-base-v2")

#Docker.yaml
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379"
)

r = redis.Redis.from_url(REDIS_URL)

try:
    r.ping()
    print("Redis connected")
except redis.exceptions.ConnectionError as e:
    raise RuntimeError(f"Cannot reach Redis at {REDIS_URL}: {e}") from e
except redis.exceptions.RedisError as e:
    raise RuntimeError(f"Redis error: {e}") from e

vectorizer = HFTextVectorizer(
    model=EMBEDDING_MODEL,
    cache=EmbeddingsCache(
        redis_client=r,
        ttl=3600
    )
)

cache = SemanticCache(
      name="LLM-Gateway-Cache",
      vectorizer=vectorizer,
      redis_client=r,
      distance_threshold=DISTANCE_THRESHOLD,
      ttl=TTL
)


evaluator = SemanticCacheEvaluator()

class CacheService:

    def get_or_set(self, query: ChatRequest):

        #Retrieving the cache..
        cache_start = time.perf_counter()
        cached = self.check(query)
        cache_latency = (time.perf_counter() - cache_start)*1000

        if cached:
            return ChatResponse(
                response=cached[0]["response"],
                cache_hit=True,
                similarity_score=None,
                cache_latency=cache_latency,
                llm_latency=0.0
            )

        llm_latency_start = time.perf_counter()
        resp = get_llm_response(query.prompt)
        llm_latency_final = (time.perf_counter() - llm_latency_start)*1000
        self.store(query.prompt, resp)

        return ChatResponse(
            response=resp,
            cache_hit=False,
            similarity_score=None,
            cache_latency=cache_latency,
            llm_latency=llm_latency_final
        )

    def check(self, query: ChatRequest):
        return cache.check(query.prompt)

    def store(self, prompt, response):
        return cache.store(
            prompt=prompt,
            response=response
        )