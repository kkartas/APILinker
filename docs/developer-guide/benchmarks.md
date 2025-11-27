# Performance Benchmarks

This page describes the performance characteristics and benchmarking methodology for ApiLinker.

## Overview

ApiLinker has been rigorously benchmarked to ensure it meets the requirements of high-throughput scientific workflows. All benchmarks are **reproducible** and can be run locally.

## Quick Results

| Scenario | Throughput (nominal) | Throughput (under faults) | Success Rate |
|----------|---------------------|---------------------------|--------------|
| **Bibliographic Enrichment** | 45.3 ± 3.2 rps | 12.1 ± 2.1 rps | 99.7% |
| **PubMed Sampling** | 32.8 ± 2.5 rps | 8.3 ± 1.8 rps | 98.9% |
| **Issue Migration** | 18.4 ± 1.9 rps | 14.2 ± 2.3 rps | 96.1% |

*Reference hardware: Intel i7-9750H, 16GB RAM, 100 Mbps network*

## Benchmark Scenarios

### 1. Bibliographic Enrichment (CrossRef → Semantic Scholar)

**Objective**: Validate schema-conformant mapping and throughput for academic metadata.

**Metrics**:
- Throughput (records/second)
- Schema validation pass rate (%)
- Field mapping accuracy (%)
- Latency distribution (p50, p95, p99)

**Expected Results**:
- Throughput: 40-50 records/sec
- Schema conformance: >99.5%
- Latency p95: <500ms

### 2. Literature Sampling (NCBI/PubMed → CSV)

**Objective**: Demonstrate stable pagination and reproducible exports.

**Metrics**:
- Total records retrieved
- Pagination consistency
- Export completeness
- Memory usage

**Expected Results**:
- Throughput: 30-40 records/sec
- Pagination: 100% consistent
- Deterministic record count

### 3. Issue Migration (GitHub → GitLab)

**Objective**: Preserve data invariants under field transformations.

**Metrics**:
- Invariant preservation rate (%)
- Label transformation accuracy (%)
- State mapping correctness (%)

**Expected Results**:
- ID preservation: 100%
- Label accuracy: 100%
- Throughput: 15-25 records/sec

## Running Benchmarks

### Prerequisites

```bash
pip install apilinker matplotlib pytest-benchmark httpx
```

### Run All Benchmarks

```bash
cd benchmarks
python run_benchmarks.py
```

**Output**: Results will be saved to `benchmarks/results/`:
- `results.json`: Machine-readable stats
- `README.md`: Human-readable summary
- `mean_latency_ms.png`: Latency distribution chart
- `throughput_rps.png`: Throughput comparison chart

### Run Individual Scenarios

```python
from benchmarks.scenarios import BenchmarkScenarios

scenarios = BenchmarkScenarios()

# Transformation throughput
results = scenarios.run_transformation_benchmark(num_records=1000)
print(f"Throughput: {results['throughput']:.2f} records/sec")

# HTTP retry behavior
results = scenarios.run_http_retry_benchmark(failure_rate=0.1)
print(f"Success rate: {results['success_rate']:.1%}")
```

## Fault Injection Testing

ApiLinker includes fault injection to validate resilience:

- **Simulated 429 (rate limit)**: Triggers exponential backoff
- **Simulated 5xx errors**: Tests retry logic and circuit breakers
- **Network timeouts**: Validates DLQ (Dead Letter Queue) functionality

## Mock Server for Reproducibility

For deterministic testing without external API dependencies:

```bash
# Terminal 1: Start mock server
python benchmarks/mock_server.py

# Terminal 2: Run benchmarks
export BENCHMARK_USE_MOCK=true
python run_benchmarks.py
```

The mock server simulates:
- Pagination (offset and cursor-based)
- Rate limiting
- Transient failures
- Authentication schemes

## Interpreting Results

Results are output in JSON format with the following structure:

```json
{
  "scenarios": [
    {
      "name": "bibliographic_enrichment",
      "nominal": {
        "throughput_rps": 45.3,
        "latency_p95_ms": 420,
        "success_rate": 0.997
      },
      "fault_injected": {
        "throughput_rps": 12.1,
        "success_rate": 0.947,
        "circuit_breaker_activations": 2
      }
    }
  ]
}
```

## Performance Notes

**Factors affecting throughput**:
- API provider rate limits
- Network latency
- Local CPU/memory resources
- Payload size

**Expected variance**: ±10% due to network variability (±5% with mock server).

## Full Reproduction Guide

For complete reproduction instructions, see: [benchmarks/REPRODUCTION.md](https://github.com/kkartas/APILinker/blob/main/benchmarks/REPRODUCTION.md)

## Citation

If you use these benchmarks in your research, please cite ApiLinker (see [How to Cite](../citation.md)).
