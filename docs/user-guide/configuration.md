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
