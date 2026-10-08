import pandas as pd
from app.cache.cache import CacheService,ChatRequest
from app.metrics.evaluation import SemanticCacheEvaluator
from app.config.config import DISTANCE_THRESHOLD,OPENAI_GPT_LUNA_PRO

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
            llm_model="gpt_luna_pro",
            prompt=row["question"]
        )
    )

    evaluator.record(
        actual_hit=row["expected_hit"],
        predicted_hit = response.cache_hit,
        cache_latency=response.cache_latency,
        llm_latency=response.llm_latency
    )

print(f"Model being used : {"gpt_luna_pro"}")
print(f"Evaluation at distance threshold : {DISTANCE_THRESHOLD}")
print(evaluator.report())



