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
