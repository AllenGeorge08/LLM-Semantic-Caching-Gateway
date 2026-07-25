import pandas as pd
from app.cache.cache import CacheService,ChatRequest
from app.metrics.evaluation import SemanticCacheEvaluator

faq_df = pd.read_csv("app/benchmark_evaluation/faq_dataset.csv")

cache = CacheService()

#Populating redis db
for _,row in faq_df.iterrows():
    cache.store(
        prompt=row["question"],
        response=row["answer"]
    )


test_df = pd.read_csv("app/benchmark_evaluation/evaluation_dataset.csv")

evaluator = SemanticCacheEvaluator()

for _,row in test_df.iterrows():
    response = cache.get_or_set(
        ChatRequest(
            prompt=row["question"]
        )
    )

    evaluator.record(
        actual_hit=row["expected_hit"],
        predicted_hit = response.cache_hit,
        cache_latency=response.cache_latency,
        llm_latency=response.llm_latency
    )


print(evaluator.report())



