# ApiLinker Quick Reference

This quick reference provides a concise overview of ApiLinker's most common operations.

## Installation

```bash
pip install apilinker
```

## Basic Usage

```python
from apilinker import ApiLinker

# Initialize
linker = ApiLinker()

# Configure source API
linker.add_source(
    type="rest",
    base_url="https://api.source.com",
    auth={
        "type": "bearer",
        "token": "${TOKEN_ENV_VAR}"
    },
    endpoints={
        "get_data": {
            "path": "/data",
            "method": "GET"
        }
    }
)

# Configure target API
linker.add_target(
    type="rest",
    base_url="https://api.target.com",
    auth={
        "type": "api_key",
        "header": "X-API-Key",
        "key": "${API_KEY_ENV_VAR}"
    },
    endpoints={
        "post_data": {
            "path": "/data",
            "method": "POST"
        }
    }
)

# Add field mapping
linker.add_mapping(
    source="get_data",
    target="post_data",
    fields=[
        {"source": "id", "target": "external_id"},
        {"source": "name", "target": "full_name"},
        {"source": "email", "target": "contact.email"}
    ]
)

# Run the sync
result = linker.sync()
print(f"Synced {result.count} records")
```

## Authentication Methods

### API Key

```python
auth={
    "type": "api_key",
    "header": "X-API-Key",  # or in: "query", param_name: "api_key"
    "key": "your-api-key"  # Better: "${API_KEY_ENV_VAR}"
}
```

### Bearer Token

```python
auth={
    "type": "bearer",
    "token": "your-token"  # Better: "${TOKEN_ENV_VAR}"
}
```

### Basic Auth

```python
auth={
    "type": "basic",
    "username": "your-username",  # Better: "${USERNAME_ENV_VAR}"
    "password": "your-password"   # Better: "${PASSWORD_ENV_VAR}"
}
```

### OAuth2

```python
auth={
    "type": "oauth2",
    "client_id": "${CLIENT_ID}",
    "client_secret": "${CLIENT_SECRET}",
    "token_url": "https://auth.example.com/token",
    "scope": "read write"  # Optional
}
```

## Common Transformers

```python
# Register a custom transformer
def format_phone(value, **kwargs):
    if not value:
        return ""
    digits = ''.join(c for c in value if c.isdigit())
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    return value

linker.mapper.register_transformer("format_phone", format_phone)

# Use in mapping
linker.add_mapping(
    source="get_users",
    target="create_contacts",
    fields=[
        # Built-in transformers
        {"source": "name", "target": "name", "transform": "lowercase"},
        {"source": "created_at", "target": "created", "transform": "iso_to_timestamp"},
        # Custom transformer
        {"source": "phone", "target": "phoneNumber", "transform": "format_phone"}
    ]
)
```

## Pagination

```python
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    endpoints={
        "get_users": {
            "path": "/users",
            "method": "GET",
            "pagination": {
                "data_path": "data",
                "next_page_path": "meta.next_page",
                "page_param": "page"
            }
        }
    }
)
```

## Scheduling

```python
# Run every hour
linker.add_schedule(interval_minutes=60)

# Or with cron expression (every day at 2 AM)
linker.add_schedule(cron_expression="0 2 * * *")

# Start the scheduler
linker.start_scheduled_sync()
```

## Error Handling

```python
def handle_error(error, context):
    print(f"Error: {error}")
    # Return True to retry, False to abort
    return True

linker.add_error_handler(handle_error)
```

## Config File (YAML)

```yaml
source:
  type: rest
  base_url: https://api.example.com/v1
  auth:
    type: bearer
    token: ${TOKEN_ENV_VAR}
  endpoints:
    get_items:
      path: /items
      method: GET
      params:
        limit: 100

target:
  type: rest
  base_url: https://api.target.com/v2
  auth:
    type: api_key
    header: X-API-Key
    key: ${API_KEY_ENV_VAR}
  endpoints:
    create_item:
      path: /items
      method: POST

mapping:
  - source: get_items
    target: create_item
    fields:
      - source: id
        target: external_id
      - source: name
        target: title
      - source: created_at
        target: meta.created
        transform: iso_to_timestamp

schedule:
  type: interval
  minutes: 60
```

Load from config file:

```python
linker = ApiLinker(config_path="config.yaml")
```
