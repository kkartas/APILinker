## Error Handling and Recovery

This page explains how to configure circuit breakers, retries, exponential backoff, and the Dead Letter Queue (DLQ).

### Quick start

Add error handling to your config file:

```yaml
error_handling:
  circuit_breakers:
    source_list_items:
      failure_threshold: 5
      reset_timeout_seconds: 60
      half_open_max_calls: 1
    target_create_item:
      failure_threshold: 3
      reset_timeout_seconds: 30
  recovery_strategies:
    network: [exponential_backoff]
    timeout: [exponential_backoff]
    server: [circuit_breaker, exponential_backoff]
    client: [fail_fast]
  dlq:
    directory: .apilinker_dlq
```

### Programmatic usage

```python
from apilinker import ApiLinker

linker = ApiLinker(
    error_handling_config={
        "circuit_breakers": {"source_list": {"failure_threshold": 5}},
        "recovery_strategies": {"server": ["circuit_breaker", "exponential_backoff"]},
        "dlq": {"directory": ".apilinker_dlq"},
    }
)

# Later, inspect analytics
summary = linker.get_error_analytics()
print(summary)

# Process DLQ items
results = linker.process_dlq(limit=10)
```

See `apilinker/core/error_handling.py` for supported strategies and categories.


