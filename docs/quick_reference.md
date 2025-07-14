# ApiLinker Quick Reference

This quick reference provides a concise overview of ApiLinker's most common operations.

## Installation

```bash
pip install apilinker
```

## Basic Usage

```python
from apilinker import ApiLinker

# Initialize with optional logging configuration
linker = ApiLinker(log_level="INFO", log_file="apilinker.log")

# Configure source API
linker.add_source(
    type="rest",
    base_url="https://api.source.com",
    auth={
        "type": "bearer",
        "token": "${TOKEN_ENV_VAR}"  # Environment variable reference
    },
    endpoints={
        "get_data": {
            "path": "/data",
            "method": "GET",
            "params": {"limit": 100}
        }
    },
    # Connection settings
    timeout=30,           # 30 second timeout 
    retry_count=3,        # Retry failed requests 3 times
    retry_delay=1         # Wait 1 second between retries
)

# Configure target API
linker.add_target(
    type="rest",
    base_url="https://api.target.com",
    auth={
        "type": "api_key",
        "header_name": "X-API-Key",  # Note: 'header_name' not 'header'
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

# Check for errors
if not result.success:
    print(f"Errors occurred: {result.errors}")
```

## Authentication Methods

### API Key

```python
auth={
    "type": "api_key",
    "key": "your-api-key",  # Better: "${API_KEY_ENV_VAR}"
    "header_name": "X-API-Key",  # Default header name
    "in_header": True,  # Send in header (default)
    "in_query": False,  # Or set to True to send as query param
    "query_param": "api_key"  # Query parameter name if in_query=True
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

### OAuth2 Client Credentials

```python
auth={
    "type": "oauth2_client_credentials",  # Note the full type name
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
# Configure schedule by type

# Option 1: Interval-based schedule (runs every X time units)
linker.add_schedule(
    type="interval",
    minutes=60  # Run every 60 minutes
    # Can also use: seconds=30, hours=2, days=1
)

# Option 2: Cron-based schedule (runs according to cron expression)
linker.add_schedule(
    type="cron",
    expression="0 2 * * *"  # Run at 2 AM daily
)

# Option 3: One-time schedule (runs once at a specific time)
from datetime import datetime, timedelta

linker.add_schedule(
    type="once",
    datetime=datetime.now() + timedelta(hours=1)  # Run in 1 hour
)

# Start the scheduler in a background thread
linker.start_scheduled_sync()

# To stop the scheduler
# linker.stop_scheduled_sync()
```

## Error Handling

```python
# ApiLinker's sync method returns a SyncResult object with error information
result = linker.sync()
if not result.success:
    print(f"Sync failed with {len(result.errors)} errors:")
    for error in result.errors:
        print(f" - {error}")

# Implementing custom error handling with try/except
try:
    result = linker.sync()
    print(f"Synced {result.count} records")
except Exception as e:
    print(f"Error during sync: {e}")
    # Log the error, notify admins, etc.

# The ApiConnector has built-in retry logic for transient failures
# Configure when initializing the source/target:
linker.add_source(
    # other parameters...
    retry_count=3,    # Number of retries
    retry_delay=1     # Seconds between retries
)
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
