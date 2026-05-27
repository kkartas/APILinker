# Configuration Guide

ApiLinker uses a YAML configuration format to define sources, targets, mappings, and other settings.

## Basic Structure

```yaml
source:
  # Source API configuration
target:
  # Target API configuration
mapping:
  # Field mapping rules
schedule:
  # Automation settings
logging:
  # Logging preferences
```

## Source and Target

Both sections share the same structure:

```yaml
source:
  type: rest
  base_url: https://api.example.com
  auth:
    type: bearer
    token: ${API_TOKEN}
  endpoints:
    list_items:
      path: /items
      method: GET
```

## Environment Variables

You can reference environment variables using the `${VAR_NAME}` syntax. This is recommended for sensitive values if not using the Secret Manager.

## Validation

You can enforce schema validation on requests and responses:

```yaml
validation:
  strict_mode: true
```

## SSE Endpoint Configuration

ApiLinker supports Server-Sent Events (SSE) with built-in reconnect and chunked consumption controls.

```yaml
source:
  type: sse
  base_url: https://events.example.com
  endpoints:
    feed:
      path: /stream
      method: GET
      sse:
        reconnect: true
        reconnect_delay: 1.0
        max_reconnect_attempts: 10
        read_timeout: 60
        decode_json: true
        chunk_size: 50
        backpressure_buffer_size: 500
        drop_policy: block  # block | drop_oldest
```

Use `stream_sse(...)` for event-by-event processing and `consume_sse(...)` for chunked/backpressure-aware processing.

## HTTP byte streaming

For large file or binary downloads (not SSE), configure optional `streaming` on a REST endpoint:

```yaml
source:
  endpoints:
    export_dump:
      path: /exports/latest
      method: GET
      streaming:
        chunk_size: 65536
        resume: true
        read_timeout: 120
        headers:
          Accept: application/octet-stream
```

In Python:

```python
summary = connector.download_stream(
    "export_dump",
    destination_path="./data/export.bin",
    progress_callback=lambda p: print(p["percent_complete"]),
)
```

`stream_response(...)` yields byte chunks when you need custom handling instead of writing to a file. When `resume` is enabled and the destination file exists, ApiLinker sends a `Range` header and appends on `206 Partial Content` responses.
