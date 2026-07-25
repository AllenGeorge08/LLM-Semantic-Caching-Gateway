# Semantic Cache Threshold Comparison

Evaluation run against 105 queries across three similarity thresholds (0.30, 0.50, 0.75).

## Summary Table

| Metric | Threshold 0.30 | Threshold 0.50 | Threshold 0.75 |
|---|---|---|---|
| Queries | 105 | 105 | 105 |
| Cache Hits / Misses | 104 / 1 | 97 / 8 | 105 / 0 |
| Cache Hit Ratio | 99.05% | 92.38% | 100.00% |
| Precision | 76.92% | **82.47%** | 76.19% |
| Recall | 100.00% | 100.00% | 100.00% |
| Accuracy | 77.14% | **83.81%** | 76.19% |
| F1 Score | 86.96% | **90.40%** | 86.49% |
| TP | 80 | 80 | 80 |
| FP | 24 | 17 | 25 |
| FN | 0 | 0 | 0 |
| TN | 1 | 8 | 0 |
| Avg Cache Latency | 6556.55 ms | 85294.48 ms | 6000.55 ms |
| P50 Cache Latency | 6259.38 ms | 84344.14 ms | 5900.74 ms |
| P95 Cache Latency | 8587.22 ms | 105302.73 ms | 6957.06 ms |
| P99 Cache Latency | 11040.03 ms | 133942.52 ms | 10099.08 ms |
| Avg LLM Latency | 25371.532 s | 18796.219 s | 0.000 s |
| Weighted Cache Latency | 248.190 s | 1517.387 s | 6.001 s |
| Speedup | 99.02% | 91.93% | **0.00%** |

## Observations

- **0.50 is the best-performing threshold overall.** It has the highest precision, accuracy, and F1 score, and is the only threshold that produces any true negatives (8), meaning it's the only one actually distinguishing genuinely dissimilar queries.
- **0.30 and 0.75 both over-match.** Recall is 100% at every threshold (no false negatives), but false positive counts of 24 and 25 respectively indicate roughly a quarter of "cache hits" at these thresholds are incorrect matches being served instead of hitting the LLM.
- **0.75's 0.00% speedup is misleading, not a win.** With zero cache misses and zero true negatives, the cache never correctly identified a dissimilar query — every query was served from cache regardless of correctness. This threshold is too loose to be useful for correctness, even though hit ratio looks perfect on paper.
- **The 85s average cache latency at 0.50 is an outlier** relative to 0.30 and 0.75 (roughly 13x higher) and should be investigated — possible causes include a cold cache/embedding model reload, GC pause, or a resource contention issue during that run, rather than an inherent property of the threshold itself.

## Recommendation

Use **threshold = 0.50** as the default operating point — it's the only configuration in this comparison that balances hit ratio with actual correctness (precision/accuracy/F1), rather than trading correctness away for a higher hit rate.