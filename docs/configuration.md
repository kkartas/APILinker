# Configuration Guide

ApiLinker uses a YAML-based configuration format to define API connections, field mappings, scheduling, and other settings. This guide explains all available configuration options in detail.

## Configuration File Structure

A complete ApiLinker configuration file has the following top-level sections:

```yaml
source:
  # Source API configuration
  
target:
  # Target API configuration
  
mapping:
  # Field mappings between APIs
  
schedule:
  # Optional scheduling configuration
  
logging:
  # Optional logging configuration
```

## Source and Target API Configuration

Both `source` and `target` sections use the same format:

```yaml
source:  # or target:
  type: rest
  base_url: https://api.example.com/v1
  auth:
    # Authentication configuration
  endpoints:
    # Endpoint definitions
  timeout: 30  # Request timeout in seconds (optional)
  retry_count: 3  # Number of retries on failure (optional)
  retry_delay: 1  # Delay between retries in seconds (optional)
```

### Authentication

ApiLinker supports multiple authentication methods:

#### API Key

```yaml
auth:
  type: api_key
  key: your_api_key  # Or use ${API_KEY_ENV_VAR} for environment variables
  header: X-API-Key  # Header name (default: X-API-Key)
  # OR for query parameter:
  in: query
  param_name: apikey
```

#### Bearer Token

```yaml
auth:
  type: bearer
  token: your_bearer_token  # Or use ${TOKEN_ENV_VAR}
```

#### Basic Authentication

```yaml
auth:
  type: basic
  username: your_username  # Or use ${USERNAME_ENV_VAR}
  password: your_password  # Or use ${PASSWORD_ENV_VAR}
```

#### OAuth2 Client Credentials

```yaml
auth:
  type: oauth2_client_credentials
  client_id: your_client_id  # Or use ${CLIENT_ID_ENV_VAR}
  client_secret: your_client_secret  # Or use ${CLIENT_SECRET_ENV_VAR}
  token_url: https://auth.example.com/oauth/token
  scope: read write  # Optional
```

### Endpoint Configuration

Define endpoints for each API:

```yaml
endpoints:
  list_users:  # Endpoint name used in mapping
    path: /users
    method: GET  # Default: GET
    params:  # Query parameters
      limit: 100
      updated_since: "{{last_sync}}"  # Template variable
    headers:  # Additional headers
      Accept: application/json
    
    # Pagination configuration (optional)
    pagination:
      data_path: data  # Path to data items in response
      next_page_path: meta.next_page  # Path to next page token/URL
      page_param: page  # Query parameter for page number/token
      max_pages: 10  # Maximum pages to fetch (optional)
    
    # Response configuration (optional)
    response_path: results  # Path to extract from response
    
    # JSON Schema validation (optional)
    response_schema:
      type: object
      properties:
        results:
          type: array
          items:
            type: object
            properties:
              id: { type: string }
              name: { type: string }
```

For endpoints that send data:

```yaml
endpoints:
  create_user:
    path: /users
    method: POST
    headers:
      Content-Type: application/json
    
    # Optional body template
    body_template:
      source: "apilinker"
      created_by: "integration"

    # Optional JSON Schema for validating request payloads
    request_schema:
      type: object
      properties:
        external_id: { type: string }
        title: { type: string }
      required: [external_id, title]
```

## Field Mappings

Mappings define how data is transformed between source and target:

```yaml
mapping:
  - source: list_users  # Source endpoint name
    target: create_user  # Target endpoint name
    fields:  # Field mappings
      # Simple field mapping
      - source: id
        target: external_id
      
      # Nested field mapping
      - source: profile.name
        target: user.full_name
      
      # Field with transformation
      - source: created_at
        target: metadata.created
        transform: iso_to_timestamp
      
      # Multiple transformations
      - source: tags
        target: labels
        transform:
          - lowercase
          - none_if_empty
      
      # Conditional field (only included if condition is met)
      - source: phone
        target: contact.phone
        condition:
          field: phone
          operator: exists  # exists, not_exists, eq, ne, gt, lt
          # value: ""  # Comparison value (for eq, ne, gt, lt)
      
      # Include null values (by default nulls are skipped)
      - source: status
        target: status
        include_nulls: true
```

### Built-in Transformers

ApiLinker includes several built-in transformers:

| Name | Description |
|------|-------------|
| `iso_to_timestamp` | Convert ISO date string to Unix timestamp |
| `timestamp_to_iso` | Convert Unix timestamp to ISO date string |
| `lowercase` | Convert string to lowercase |
| `uppercase` | Convert string to uppercase |
| `strip` | Remove whitespace from start/end of string |
| `to_string` | Convert value to string |
| `to_int` | Convert value to integer |
| `to_float` | Convert value to float |
| `to_bool` | Convert value to boolean |
| `default_empty_string` | Return empty string if value is null |
| `default_zero` | Return 0 if value is null |
| `none_if_empty` | Return null if value is empty string |

## Scheduling

Configure automatic sync intervals:

```yaml
# Run every X minutes/hours/days
schedule:
  type: interval
  minutes: 30
  # Or use hours: 1, days: 1, seconds: 30

# Or use cron expression
schedule:
  type: cron
  expression: "0 */6 * * *"  # Every 6 hours

# Or run once at a specific time
schedule:
  type: once
  datetime: "2023-12-31T23:59:59"
```

## Logging

Configure logging behavior:

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  file: logs/apilinker.log  # Optional log file path
```

## Provenance & Idempotency

Add optional provenance capture and idempotency to improve reproducibility and safe replays:

```yaml
provenance:
  output_dir: runs/                 # Write a sidecar JSON per run
  jsonl_log: logs/runs.jsonl        # Append-only JSONL event log

idempotency:
  enabled: true
  salt: "example-integration"       # Optional salt for key generation
```

Notes:
- The config hash is computed from the active config file; git SHA is recorded when the repository is available.
- Idempotency de-duplicates items within the same process. For distributed runs, use an external store or target-side idempotency.

## Environment Variables

You can use environment variables in your configuration file:

```yaml
auth:
  type: bearer
  token: ${API_TOKEN}  # Will be replaced with value of API_TOKEN env var
```

## Template Variables

Some special template variables are available:

- `{{last_sync}}`: Timestamp of the last successful sync
- `{{now}}`: Current timestamp
- `{{yesterday}}`: Timestamp 24 hours ago

## Complete Example

```yaml
source:
  type: rest
  base_url: https://api.source.com/v1
  auth:
    type: api_key
    header: X-API-Key
    key: ${SOURCE_API_KEY}
  endpoints:
    list_products:
      path: /products
      method: GET
      params:
        updated_since: "{{last_sync}}"
        limit: 100
      pagination:
        data_path: data
        next_page_path: meta.next_page
        page_param: page

target:
  type: rest
  base_url: https://api.destination.com/v2
  auth:
    type: bearer
    token: ${TARGET_API_TOKEN}
  endpoints:
    create_product:
      path: /products
      method: POST
    update_product:
      path: /products/{id}
      method: PUT

mapping:
  - source: list_products
    target: create_product
    fields:
      - source: id
        target: external_id
      - source: name
        target: title
      - source: description
        target: body.content
      - source: price
        target: pricing.amount
        transform: to_float
      - source: created_at
        target: metadata.created
        transform: iso_to_timestamp
      - source: tags
        target: categories
        transform: 
          - lowercase
          - none_if_empty

schedule:
  type: cron
  expression: "0 */6 * * *"  # Every 6 hours

logging:
  level: INFO
  file: logs/apilinker.log
```

## State & Resumability

Persist last sync cursors and checkpoints to resume safely on subsequent runs.

```yaml
state:
  type: file
  path: .apilinker/state.json
  default_last_sync: "2024-01-01T00:00:00Z"  # Used if no previous value exists
```

Behavior:
- The `updated_since` parameter is injected automatically from `state.last_sync[<source_endpoint>]` when not provided explicitly.
- After a successful sync, `last_sync` is updated to the current time (UTC ISO 8601).
- Checkpoints and DLQ pointers are available via the state store API for advanced workflows.
