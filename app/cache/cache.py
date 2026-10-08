import os
import redis
import time

from sentence_transformers import SentenceTransformer
from redisvl.utils.vectorize import HFTextVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from redisvl.extensions.cache.llm import SemanticCache
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.metrics.evaluation import SemanticCacheEvaluator
from app.config.config import EMBEDDING_MODEL, TTL, DISTANCE_THRESHOLD
from app.providers.llm_providers import Router
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

router = Router()

encoder = SentenceTransformer("all-mpnet-base-v2")

# Docker.yaml
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

r = redis.Redis.from_url(REDIS_URL)

try:
    r.ping()
    print("Redis connected")
except redis.exceptions.ConnectionError as e:
    raise RuntimeError(f"Cannot reach Redis at {REDIS_URL}: {e}") from e
except redis.exceptions.RedisError as e:
    raise RuntimeError(f"Redis error: {e}") from e

vectorizer = HFTextVectorizer(
    model=EMBEDDING_MODEL, cache=EmbeddingsCache(redis_client=r, ttl=3600)
)

dist_threshold = DISTANCE_THRESHOLD


def set_distance_threshold(threshold: float):
    dist_threshold = threshold
    print(f"Distance threshold changed to {dist_threshold}")


semantic_cache = SemanticCache(
    name="LLM-Gateway-Cache",
    vectorizer=vectorizer,
    redis_client=r,
    distance_threshold=dist_threshold,
    ttl=TTL,
)

supported_models = router.supported_models()
evaluator = SemanticCacheEvaluator()


class CacheService:
    def get_or_set(self, query: ChatRequest):

        model = query.llm_model
        if model not in supported_models:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "unsupported_model",
                    "model": query.llm_model,
                    "supported": supported_models,
                },
            )

        # Retrieving the cache..
        cache_start = time.perf_counter()
        cached = self.check(query)
        cache_latency = (time.perf_counter() - cache_start) * 1000

        if cached:
            distance = float(cached[0]["vector_distance"])
            similarity = 1 - distance

            return ChatResponse(
                response=cached[0]["response"],
                cache_hit=True,
                similarity_score=similarity,
                cache_latency=cache_latency,
                llm_latency=0.0,
            )

        llm_latency_start = time.perf_counter()

        try:
            resp = router.invoke(query.llm_model, query.prompt)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM call failed: {e}") from e

        llm_latency_final = (time.perf_counter() - llm_latency_start) * 1000
        self.store(query.prompt, resp)

        return ChatResponse(
            response=resp,
            cache_hit=False,
            similarity_score=None,
            cache_latency=cache_latency,
            llm_latency=llm_latency_final,
        )

    def check(self, query: ChatRequest):
        return semantic_cache.check(
            query.prompt, return_fields=["response", "vector_distance"]
        )

    def store(self, prompt, response):
        return semantic_cache.store(prompt=prompt, response=response)

    def delete(self):
        return semantic_cache.clear()


cache_service = CacheService()
