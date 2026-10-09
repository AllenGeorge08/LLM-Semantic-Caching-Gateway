import time
import numpy as np
from app.cache.cache import cache_service, semantic_cache, router
from app.schemas.request import ChatRequest
from app.providers.llm_providers import available_models

MODELS = []
for model in available_models:
    MODELS.append(model)


DISTANCE_THRESHOLDS = [0.30, 0.50, 0.75]

QUERY_GROUPS = [
    [
        "Who is Narendra Modi?",
        "Tell me about India's current prime minister.",
        "Give me background on the man leading India's government.",
    ],
    [
        "What causes inflation?",
        "Why do prices rise across an economy over time?",
        "Explain the economic forces that make money lose purchasing power.",
    ],
    [
        "How does photosynthesis work?",
        "Explain how plants convert sunlight into energy.",
        "What's the biological process plants use to make food from light?",
    ],
    [
        "What is the capital of France?",
        "Which city serves as France's seat of government?",
        "Name the largest city and capital in France.",
    ],
    [
        "How do I reverse a linked list in Python?",
        "Write Python code to flip the order of a linked list.",
        "Show me an algorithm to invert a singly linked list, in Python.",
    ],
]


def run_baseline(model: str):
    latencies = []
    for group in QUERY_GROUPS:
        for prompt in group:
            time_start = time.perf_counter()
            _ = router.invoke(model, prompt)
            latencies.append((time.perf_counter() - time_start) * 1000)

    return {
        "model": model,
        "mean_ms": np.mean(latencies),
        "p50_ms": np.median(latencies),
        "p90_ms": np.percentile(latencies, 90),
        "p95_ms": np.percentile(latencies, 95),
    }


def run_cache(model: str):
    cache_latencies = []
    for group in QUERY_GROUPS:
        for prompt in group:
            req = ChatRequest(llm_model=model, prompt=prompt)
            time_start = time.perf_counter()
            _ = cache_service.get_or_set(req)
            cache_latencies.append((time.perf_counter() - time_start) * 1000)
    return {
        "model": model,
        "mean_ms": np.mean(cache_latencies),
        "p50_ms": np.median(cache_latencies),
        "p90_ms": np.percentile(cache_latencies, 90),
        "p95_ms": np.percentile(cache_latencies, 95),
    }


def main():
    print("Running baseline checks..")
    cache_service.delete()
    baseline_responses = {}
    for model in MODELS:
        cache_service.delete()
        res = run_baseline(model)
        baseline_responses[model] = res
        print(
            f"{model:12s} mean_ms: {res['mean_ms']}, p50_ms: {res['p50_ms']}, p90_ms: {res['p90_ms']}, p95_ms: {res['p95_ms']}"
        )

    cache_service.delete()
    cached_responses = {}
    print("Cached latencies...")
    for model in MODELS:
        cache_service.delete()
        res = run_cache(model)
        cached_responses[model] = res
        print(
            f"{model:12s} mean_ms: {res['mean_ms']}, p50_ms: {res['p50_ms']}, p90_ms: {res['p90_ms']}, p95_ms: {res['p95_ms']}"
        )


if __name__ == "__main__":
    main()
