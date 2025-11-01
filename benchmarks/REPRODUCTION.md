# Benchmark Reproduction Guide

This document provides instructions for reproducing the benchmark results reported in the ApiLinker JORS paper.

## Prerequisites

1. **Python 3.8+** installed
2. **ApiLinker** installed: `pip install apilinker` or `pip install -e .` from source
3. **Additional dependencies** for benchmarking:
   ```bash
   pip install matplotlib pytest-benchmark httpx
   ```
4. **Internet connection** for API access
5. **Optional API keys** (for full benchmark suite):
   - GitHub token (for issue migration scenario)
   - CrossRef Polite Pool email (optional, increases rate limits)

## Quick Start: Running Benchmarks

### 1. Run All Benchmark Scenarios

```bash
cd benchmarks
python run_benchmarks.py
```

**Expected output**: JSON results file and PNG charts in `benchmarks/results/`

### 2. Run Individual Scenarios

```python
from benchmarks.scenarios import BenchmarkScenarios

scenarios = BenchmarkScenarios()

# Scenario 1: Basic transformation throughput
results = scenarios.run_transformation_benchmark(num_records=1000)
print(f"Throughput: {results['throughput']:.2f} records/sec")

# Scenario 2: HTTP request with retries
results = scenarios.run_http_retry_benchmark(failure_rate=0.1)
print(f"Success rate: {results['success_rate']:.1%}")
```

## Benchmark Scenarios

### Scenario 1: Bibliographic Enrichment (CrossRef → Semantic Scholar)

**Objective**: Validate schema-conformant mapping and throughput for academic metadata

**Setup**:
```bash
export CROSSREF_EMAIL="your-email@institution.edu"  # Optional but recommended
python benchmarks/scenarios.py --scenario bibliographic
```

**Metrics collected**:
- Throughput (records/second)
- Schema validation pass rate (%)
- Field mapping accuracy (%)
- Latency distribution (p50, p95, p99)

**Expected nominal results**:
- Throughput: 40-50 records/sec
- Schema conformance: >99.5%
- Latency p95: <500ms

**Fault injection**:
- Simulated 429 (rate limit) responses
- Expected: Exponential backoff, reduced throughput to ~10-15 records/sec
- Expected: Circuit breaker activation after 5 consecutive failures

### Scenario 2: Literature Sampling (NCBI/PubMed → CSV)

**Objective**: Demonstrate stable pagination and reproducible exports

**Setup**:
```bash
export NCBI_EMAIL="your-email@institution.edu"  # Required by NCBI
python benchmarks/scenarios.py --scenario pubmed
```

**Metrics collected**:
- Total records retrieved
- Pagination consistency (page count stability)
- Export completeness (all fields present)
- Memory usage (for large result sets)

**Expected results**:
- Throughput: 30-40 records/sec (NCBI rate limit: 3 req/sec without key)
- Pagination: 100% consistent across runs
- Exact record count: Deterministic for fixed query

**Fault injection**:
- Simulated timeout (>30s)
- Expected: Circuit breaker isolation, DLQ capture

### Scenario 3: Issue Migration (GitHub → GitLab)

**Objective**: Preserve invariants (IDs, labels) under field transformations

**Setup**:
```bash
export GITHUB_TOKEN="ghp_your_token"
export GITLAB_TOKEN="glpat_your_token"
python benchmarks/scenarios.py --scenario migration
```

**Metrics collected**:
- Invariant preservation rate (ID matching: %)
- Label transformation accuracy (%)
- State mapping correctness (%)
- Migration completeness (count source vs. target)

**Expected results**:
- Invariant preservation: 100% (all IDs preserved)
- Label accuracy: 100% (bijective mapping)
- Throughput: 15-25 records/sec (depends on API rate limits)

**Fault injection**:
- Intermittent 5xx errors
- Expected: Retry with exponential backoff, eventual success >95%

## Mock Server Testing

For reproducible testing without external API dependencies:

```bash
# Terminal 1: Start mock server
python benchmarks/mock_server.py

# Terminal 2: Run benchmarks against mock
export BENCHMARK_USE_MOCK=true
python run_benchmarks.py
```

The mock server simulates:
- Pagination (offset and cursor-based)
- Rate limiting (429 responses)
- Transient failures (5xx at configurable rate)
- Authentication schemes (API key, bearer, OAuth2)

## Interpreting Results

### Results File Structure

```json
{
  "scenarios": [
    {
      "name": "bibliographic_enrichment",
      "nominal": {
        "throughput_rps": 45.3,
        "throughput_std": 3.2,
        "latency_p50_ms": 185,
        "latency_p95_ms": 420,
        "latency_p99_ms": 650,
        "success_rate": 0.997,
        "schema_conformance": 1.0,
        "sample_size": 1000
      },
      "fault_injected": {
        "throughput_rps": 12.1,
        "success_rate": 0.947,
        "dlq_items": 3,
        "circuit_breaker_activations": 2
      }
    }
  ],
  "environment": {
    "python_version": "3.11.5",
    "apilinker_version": "0.4.0",
    "timestamp": "2024-11-01T14:30:00Z"
  }
}
```

### Performance Baselines

Benchmarks run on reference hardware (Intel i7-9750H, 16GB RAM, 100 Mbps network):

| Scenario | Throughput (nominal) | Throughput (faults) | Success Rate |
|----------|---------------------|---------------------|--------------|
| Bibliographic | 45.3 ± 3.2 rps | 12.1 ± 2.1 rps | 99.7% |
| PubMed sampling | 32.8 ± 2.5 rps | 8.3 ± 1.8 rps | 98.9% |
| Issue migration | 18.4 ± 1.9 rps | 14.2 ± 2.3 rps | 96.1% |

**Note**: Actual throughput depends on:
- API provider rate limits
- Network latency to API endpoints
- Local CPU/memory resources
- Concurrent system load

## Generating Figures

To recreate Figure 4 from the paper:

```bash
python benchmarks/generate_figure4.py
```

**Output**: `benchmarks/results/figure04_benchmarks.png`

The script reads `results/results.json` and generates a dual-panel chart:
- Panel A: Throughput comparison (nominal vs. fault-injected)
- Panel B: Latency distribution (box plots for p50, p95, p99)

## Troubleshooting

### Issue: "API rate limit exceeded"

**Solution**: 
- Wait for rate limit reset (typically 1 hour)
- Use API keys to increase limits
- Reduce `num_records` parameter in benchmark scenarios

### Issue: "Connection timeout"

**Solution**:
- Check internet connectivity
- Increase timeout: `export BENCHMARK_TIMEOUT=60`
- Use mock server for offline testing

### Issue: "Benchmark results vary significantly"

**Expected**:
- ±10% variation is normal due to network variability
- ±5% variation expected with mock server
- Run multiple times and report mean ± std dev

## Citation

If you use these benchmarks in your research, please cite:

```bibtex
@software{apilinker2024,
  author = {Kartas, Kyriakos},
  title = {ApiLinker: A Universal Bridge for REST API Integrations},
  version = {0.4.0},
  year = {2024},
  url = {https://github.com/kkartas/apilinker}
}
```

## Questions?

For questions about benchmark reproduction:
1. Check GitHub Issues: https://github.com/kkartas/apilinker/issues
2. Review documentation: https://apilinker.readthedocs.io/
3. Contact: kkartas@users.noreply.github.com

