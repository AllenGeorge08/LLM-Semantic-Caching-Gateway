import os 
import redis
import time 
import numpy as np
import pandas as pd 

from sentence_transformers import SentenceTransformer 
from redisvl.utils.vectorize import HFTextVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache 
from redisvl.extensions.cache.llm import SemanticCache
from schemas.request import  ChatRequest
from schemas.response import ChatResponse
from providers.deepseek_ollama import get_llm_response

encoder = SentenceTransformer("all-mpnet-base-v2")

#Docker.yaml
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379"
)

r = redis.Redis.from_url(REDIS_URL)
r.ping()
print("Redis connected")


vectorizer = HFTextVectorizer(
    model="redis/langcache-embed-v1",
    cache=EmbeddingsCache(
        redis_client=r,
        ttl=3600
    )
)

cache = SemanticCache(
      name="LLM-Gateway-Cache",
      vectorizer=vectorizer,
      redis_client=r,
      distance_threshold=0.5
)


class CacheService:

    def get_or_set(self, query: ChatRequest):
        start = time.perf_counter()
        cached = self.check(query)

        latency = (time.perf_counter() - start)*1000

        if cached:
            return ChatResponse(
                response=cached[0]["response"],
                cache_hit=True,
                similarity_score=None,
                latency_ms=latency
            )

        resp = get_llm_response(query.prompt)
        self.store(query.prompt, resp)

        return ChatResponse(
            response=resp,
            cache_hit=False,
            similarity_score=None,
            latency_ms=None
        )

    def check(self, query: ChatRequest):
        return cache.check(query.prompt)

    def store(self, prompt, response):
        return cache.store(
            prompt=prompt,
            response=response
        )