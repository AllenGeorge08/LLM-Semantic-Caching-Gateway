# Semantic Cache Threshold Comparison

Evaluation of the semantic cache across four distance thresholds (0.30, 0.50, 0.75, 0.90) on 105 labeled queries, with `gpt_luna_pro` as the backing LLM.

## Setup

#### How to Reproduce

- Tune the `DISTANCE_THRESHOLD` from `app/config/config.py`

- Run
```python
python -m app.benchmark_evaluation.benchmark
```

| Item | Value |
|---|---|
| Queries | 105 (80 expected hits: paraphrases of cached queries; 25 expected misses: near-miss and unrelated queries) |
| Cache | RedisVL semantic cache, cosine distance |
| Threshold meaning | `distance_threshold`: a cached entry is returned if its cosine distance to the query is within the threshold. **Lower is stricter.** |
| Backing LLM | gpt_luna_pro (via OpenRouter) |
| Positive class | "should be served from cache" |

Definitions:

- **TP**: expected hit, served from cache (correct hit)
- **FP**: expected miss, served from cache (wrong answer returned)
- **FN**: expected hit, sent to the LLM (missed saving)
- **TN**: expected miss, sent to the LLM (correct miss)
- **False-hit rate**: FP / (FP + TN), the share of queries that should miss but are served a cached answer
- **Balanced accuracy**: mean of recall and true-negative rate, which is robust to the 80/25 class imbalance

## Results

| Metric | 0.30 | 0.50 | 0.75 | 0.90 |
|---|---:|---:|---:|---:|
| Queries | 105 | 105 | 105 | 105 |
| Cache hits / misses | 62 / 43 | 105 / 0 | 105 / 0 | 105 / 0 |
| Cache hit ratio | 59.05% | 100.00% | 100.00% | 100.00% |
| Precision | **95.16%** | 76.19% | 76.19% | 76.19% |
| Recall | 73.75% | **100.00%** | **100.00%** | **100.00%** |
| **False-hit rate** | **12.00%** | 100.00% | 100.00% | 100.00% |
| Accuracy | 77.14% | 76.19% | 76.19% | 76.19% |
| Balanced accuracy | **80.88%** | 50.00% | 50.00% | 50.00% |
| F1 score | 83.10% | 86.49% | 86.49% | 86.49% |
| TP | 59 | 80 | 80 | 80 |
| FP | 3 | 25 | 25 | 25 |
| FN | 21 | 0 | 0 | 0 |
| TN | 22 | 0 | 0 | 0 |

## Observations

- **Only 0.30 discriminates.** At 0.50, 0.75 and 0.90 every one of the 105 queries is served from cache, so the results are identical. These thresholds are too loose for this embedding model: all 25 near-miss queries sit within 0.50 distance of a cached entry.
- **At 0.30, 3 of 25 near-miss queries (12%) receive a wrong cached answer**, versus 100% at the looser thresholds. Precision is 95.16%.
- **0.30 gives up recall to get there.** 59 of 80 paraphrases hit (73.75%), and 21 are sent to the LLM unnecessarily. A miss costs an LLM call, while a false hit returns a wrong answer, so this is the safer side of the tradeoff.
- **Accuracy and F1 are not the deciding metrics here.** With 80 positives and 25 negatives, serving everything from cache already scores 76.19% accuracy and 86.49% F1, which is why the loose thresholds look competitive on those two. Balanced accuracy (80.88% vs 50.00%) and false-hit rate show the real difference.
- **There is an ambiguous band between 0.30 and 0.50.** It contains 43 queries: 21 that should hit and 22 that should miss. Raising the threshold within this band recovers paraphrases at roughly the same rate it admits wrong hits, which suggests the distance score alone cannot separate these cases cleanly.

## Latency

Latency figures from this evaluation run are not reported as cache-hit latency. The per-query timings in this harness (about 5-6 s at thresholds of 0.50 and above, and about 144 s on average at 0.30) are far above the lookup latency measured in isolation, and they do not isolate the embedding and vector-search path. The weighted-latency and speedup values this script printed are also omitted, because they combine milliseconds and seconds in one formula.

LLM latency on the miss path at 0.30 (43 misses), which the script printed with an "s" label but whose values are milliseconds:

| Metric | Value |
|---|---:|
| Average LLM latency | 7,094.8 ms |
| P50 LLM latency | 6,574.2 ms |
| P95 LLM latency | 13,638.2 ms |
| P99 LLM latency | 15,945.1 ms |

Cache vs. LLM latency across models is reported separately in the latency benchmark, with lookup timed on its own.

## Conclusion

Of the thresholds tested, **0.30 is the only usable operating point**: 95.16% precision and a 12% false-hit rate, at the cost of 73.75% recall. It is not yet tuned. Thresholds of 0.50 and above should not be used with this embedding model on this query set.

