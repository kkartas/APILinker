# Webhooks

APILinker provides first-class webhook support for receiving webhooks and triggering syncs in real-time, event-driven integrations.

## Overview

The webhook module enables you to:

- Run an HTTP server to receive webhooks from external services
- Register and manage multiple webhook endpoints
- Verify webhook signatures (HMAC, JWT)
- Filter and route events to handlers
- Replay historical events
- Automatically retry failed processing

## Installation

Install APILinker with webhook dependencies:

```bash
pip install apilinker[webhooks]
```

This installs FastAPI, uvicorn, and PyJWT for webhook functionality.

## Quick Start

```python
from apilinker import (
    WebhookServer,
    WebhookEndpoint,
    SignatureType,
)

# 1. Create and configure endpoint
endpoint = WebhookEndpoint(
    path="/hooks/github",
    secret="your-webhook-secret",
    signature_type=SignatureType.HMAC_SHA256,
    signature_header="X-Hub-Signature-256",
)

# 2. Create server and register endpoint
server = WebhookServer(host="0.0.0.0", port=8000)
server.register_endpoint(endpoint)

# 3. Add event handler
def on_webhook(event):
    print(f"Received: {event.payload}")

server.add_event_handler(on_webhook)

# 4. Start server
server.start(blocking=True)
```

## Webhook Manager

For advanced use cases, use `WebhookManager` which provides routing, retry, and replay:

```python
from apilinker import (
    WebhookManager,
    WebhookConfig,
    WebhookEndpoint,
    WebhookEventFilter,
    SignatureType,
)

# Configure the manager
config = WebhookConfig(
    host="0.0.0.0",
    port=8000,
    max_retry_attempts=3,
    event_history_size=1000,
)

manager = WebhookManager(config)

# Register endpoints
manager.register_endpoint(WebhookEndpoint(
    path="/hooks/github",
    secret="github-secret",
    signature_type=SignatureType.HMAC_SHA256,
))

manager.register_endpoint(WebhookEndpoint(
    path="/hooks/stripe",
    secret="stripe-secret",
    signature_type=SignatureType.HMAC_SHA256,
    signature_header="Stripe-Signature",
))

# Add filtered handlers
def handle_github_push(event):
    if event.payload.get("action") == "push":
        # Trigger a sync
        pass

manager.add_handler(
    handle_github_push,
    filter_=WebhookEventFilter(endpoint_paths=["/hooks/github"]),
    name="github_push_handler",
)

# Start the manager
manager.start(blocking=True)
```

## Signature Verification

APILinker supports multiple signature verification methods:

### HMAC-SHA256 (GitHub, Stripe, etc.)

```python
endpoint = WebhookEndpoint(
    path="/hooks/github",
    secret="your-secret",
    signature_type=SignatureType.HMAC_SHA256,
    signature_header="X-Hub-Signature-256",
)
```

### HMAC-SHA1 (Legacy webhooks)

```python
endpoint = WebhookEndpoint(
    path="/hooks/legacy",
    secret="your-secret",
    signature_type=SignatureType.HMAC_SHA1,
    signature_header="X-Signature",
)
```

### JWT Verification

```python
from apilinker.core.webhooks import JWTVerifier

endpoint = WebhookEndpoint(
    path="/hooks/jwt",
    secret="jwt-secret",
    signature_type=SignatureType.JWT,
    signature_header="Authorization",
)
```

## Event Filtering

Filter events based on various criteria:

```python
from apilinker import WebhookEventFilter

# Filter by endpoint path (supports wildcards)
filter_github = WebhookEventFilter(
    endpoint_paths=["/hooks/github", "/hooks/gitlab"]
)

# Filter by HTTP method
filter_posts = WebhookEventFilter(methods=["POST"])

# Filter by header patterns (regex)
filter_push = WebhookEventFilter(
    header_patterns={"x-github-event": "push|pull_request"}
)

# Filter by payload content (JSON path)
filter_opened = WebhookEventFilter(
    payload_patterns={
        "action": "opened",
        "repository.name": "my-repo.*",
    }
)

# Combine filters
filter_combined = WebhookEventFilter(
    endpoint_paths=["/hooks/github"],
    methods=["POST"],
    payload_patterns={"action": "opened"},
)
```

## Retry Mechanism

Failed webhook processing automatically retries with exponential backoff:

```python
config = WebhookConfig(
    max_retry_attempts=3,      # Maximum retries
    retry_delay_seconds=1.0,   # Initial delay
    retry_backoff_multiplier=2.0,  # Backoff multiplier
)
```

The retry sequence would be: 1s → 2s → 4s (max 3 attempts).

## Event Replay

Replay historical events for debugging or reprocessing:

```python
# Get event history
history = manager.get_event_history(
    endpoint_path="/hooks/github",
    limit=100,
)

# Replay a specific event
if history:
    result = manager.replay_event(history[0].id)
    print(f"Replay result: {result.success}")
```

## Integration with APILinker Syncs

Trigger APILinker syncs from webhooks:

```python
from apilinker import ApiLinker, WebhookManager, WebhookEventFilter

# Setup your ApiLinker
linker = ApiLinker(
    source_config={...},
    target_config={...},
    field_mapping={...},
)

# Create webhook handler that triggers sync
def trigger_sync(event):
    result = linker.sync()
    return {"synced": result.items_processed}

# Register with webhook manager
manager = WebhookManager()
manager.add_handler(
    trigger_sync,
    filter_=WebhookEventFilter(endpoint_paths=["/hooks/trigger"]),
    name="sync_trigger",
)
```

## Security Considerations

> [!WARNING]
> Always use signature verification in production to prevent unauthorized webhook calls.

Best practices:

1. **Always verify signatures** - Use `signature_type` and `secret` for all endpoints
2. **Use HTTPS** - Deploy behind a reverse proxy with TLS
3. **Validate payloads** - Use filters to ensure expected payload structure
4. **Limit exposure** - Only expose necessary endpoints
5. **Monitor events** - Use event history for auditing

## API Reference

### WebhookEndpoint

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | str | required | URL path for the endpoint |
| `name` | str | auto | Human-readable name |
| `secret` | str | None | Secret for signature verification |
| `signature_type` | SignatureType | NONE | Verification type |
| `signature_header` | str | X-Hub-Signature-256 | Header containing signature |
| `methods` | List[str] | ["POST"] | Allowed HTTP methods |
| `enabled` | bool | True | Enable/disable endpoint |

### WebhookConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | 0.0.0.0 | Host to bind server |
| `port` | int | 8000 | Port to listen on |
| `max_retry_attempts` | int | 3 | Maximum retry attempts |
| `retry_delay_seconds` | float | 1.0 | Initial retry delay |
| `event_history_size` | int | 1000 | Max events in history |
