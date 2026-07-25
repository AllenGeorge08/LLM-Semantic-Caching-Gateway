import numpy as np

class SemanticCacheEvaluator:

    def __init__(self):
        self.tp = 0
        self.fp = 0
        self.tn = 0
        self.fn = 0

        self.total_queries = 0
        self.cache_hits = 0
        self.cache_misses  = 0

        self.cache_latencies = []
        self.llm_latencies = []


    def record(self,actual_hit: bool ,predicted_hit :bool ,cache_latency: float,llm_latency: float =0.0):
        self.total_queries += 1
        self.cache_latencies.append(cache_latency)

        if llm_latency>0:
            self.llm_latencies.append(llm_latency)

        if predicted_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1


        #Confusion matrix
        if predicted_hit and actual_hit:
            self.tp += 1
        elif predicted_hit and not actual_hit:
            self.fp += 1
        elif not predicted_hit and actual_hit:
            self.fn+=1
        else:
            self.tn += 1


    @property
    def cache_hit_ratio(self):
        return self.cache_hits/self.total_queries  if self.total_queries else 0


    @property
    def cache_miss_ratio(self):
        return self.cache_misses /self.total_queries if self.total_queries else 0

    @property
    def precision(self):
        denominator = self.tp + self.fp 
        return self.tp/denominator if denominator else 0

    @property
    def accuracy(self):
        return (self.tp + self.tn)/self.total_queries if self.total_queries else 0

    @property
    def recall(self):
        denom = self.tp + self.fn 
        return self.tp/denom if denom else 0

    @property
    def f1_score(self):
        p = self.precision
        r = self.recall 

        if p+r==0:
            return 0

        return 2*p*r/(p+r)

    @property
    def average_cache_latency(self):
        if not self.cache_latencies: return 0
        return np.mean(self.cache_latencies)


    @property
    def average_llm_latency(self):
        if not self.llm_latencies: return 0
        return np.mean(self.llm_latencies)

    @property
    def weighted_cache_latency(self):
        ACL = self.average_cache_latency
        ALL = self.average_llm_latency
        CHR = self.cache_hit_ratio
        return ACL*CHR + (ALL+ACL)*(1-CHR)

    @property
    def speedup(self):
        ALL = self.average_llm_latency

        if ALL == 0:
            return 0

        WCL = self.weighted_cache_latency
        return (ALL-WCL)/ALL


    def __percentile__(self,values,p):
        """Computing percentile"""
        if not values:
            return 0.0
        return np.percentile(values,p)


    @property
    def p50_cache_latency(self):
        return self.__percentile__(self.cache_latencies,50)

    
    @property
    def p95_cache_latency(self):
            return self.__percentile__(self.cache_latencies, 95)

    @property
    def p99_cache_latency(self):
        return self.__percentile__(self.cache_latencies,99)

    @property
    def p50_llm_latency(self):
        return self.__percentile__(self.llm_latencies,50)

    @property
    def p95_llm_latency(self):
        return self.__percentile__(self.llm_latencies,95)

    @property
    def p99_llm_latency(self):
        return self.__percentile__(self.llm_latencies,99)


    def report(self):

        print("\n" + "=" * 50)
        print("Semantic Cache Evaluation")
        print("=" * 50)

        print(f"Queries              : {self.total_queries}")
        print(f"Cache Hits           : {self.cache_hits}")
        print(f"Cache Misses         : {self.cache_misses}")
        print()

        print(f"Cache Hit Ratio      : {self.cache_hit_ratio:.2%}")
        print(f"Precision            : {self.precision:.2%}")
        print(f"Recall               : {self.recall:.2%}")
        print(f"Accuracy             : {self.accuracy:.2%}")
        print(f"F1 Score             : {self.f1_score:.2%}")

        print()

        print(
            f"Average Cache Latency : {self.average_cache_latency*1000:.2f} ms"
        )

        print(
            f"Average LLM Latency   : {self.average_llm_latency:.3f} s"
        )

        print(
            f"Weighted Cache Latency: {self.weighted_cache_latency:.3f} s"
        )

        print(
            f"Speedup               : {self.speedup:.2%}"
        )

        print()

        print("Confusion Matrix")
        print("----------------")

        print(f"TP : {self.tp}")
        print(f"FP : {self.fp}")
        print(f"FN : {self.fn}")
        print(f"TN : {self.tn}")

        print("=" * 50)

        print("\nLatency Metrics")
        print("-" * 40)

        print(f"Average Cache Latency : {self.average_cache_latency*1000:.2f} ms")
        print(f"P50 Cache Latency     : {self.p50_cache_latency*1000:.2f} ms")
        print(f"P95 Cache Latency     : {self.p95_cache_latency*1000:.2f} ms")
        print(f"P99 Cache Latency     : {self.p99_cache_latency*1000:.2f} ms")

        print()

        print(f"Average LLM Latency   : {self.average_llm_latency:.3f} s")
        print(f"P50 LLM Latency       : {self.p50_llm_latency:.3f} s")
        print(f"P95 LLM Latency       : {self.p95_llm_latency:.3f} s")
        print(f"P99 LLM Latency       : {self.p99_llm_latency:.3f} s")

        print()

        print(f"Weighted Cache Latency: {self.weighted_cache_latency:.3f} s")
        print(f"Speedup               : {self.speedup:.2%}")


        print(f"Cache Hit Ratio  : {self.cache_hit_ratio:.2%}")
        print(f"Cache Miss Ratio : {self.cache_miss_ratio:.2%}")
    