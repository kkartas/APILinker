## Benchmarks

This document describes how to run reproducible, local benchmarks for ApiLinker.

### Goals

- Measure end-to-end sync latency for small/medium/large payloads
- Measure throughput (requests per second) and memory peak
- Provide repeatable results using a built-in mock HTTP server

### Scenarios

Benchmarks run against a lightweight local server that emulates a simple `GET /users` and `POST /users` workflow. Scenarios:

- small_batch: 10 users
- medium_batch: 1,000 users
- large_batch: 10,000 users

### Running

```bash
python -m benchmarks.run_benchmarks --iterations 10 --out benchmarks/results
```

This will produce:

- `benchmarks/results/results.json`: machine-readable stats
- `benchmarks/results/README.md`: human-readable summary

### Reported Metrics

- mean_ms, median_ms, p95_ms, min_ms, max_ms
- duration_seconds for all iterations
- rps (iterations per second)
- peak_memory_mb (via `tracemalloc`)

### Notes

- These benchmarks are local and synthetic; they do not hit third-party APIs
- For external API benchmarks, adapt `benchmarks/scenarios.py` to point to real endpoints with proper auth and rate limiting


