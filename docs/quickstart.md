# Quick Start Guide

This guide will help you quickly set up and run your first API integration with ApiLinker.

## Prerequisites

- Python 3.8 or higher installed
- ApiLinker installed (`pip install apilinker`)
- Access to source and target APIs with appropriate credentials

## Step 1: Create a Configuration File

First, generate a template configuration file:

```bash
apilinker init --output my_config.yaml
```

This creates a starter YAML configuration file that you can customize:

```yaml
# my_config.yaml
source:
  type: rest
  base_url: https://api.example.com/v1
  auth:
    type: bearer
    token: ${SOURCE_API_TOKEN}  # Will be read from environment variable
  endpoints:
    list_items:
      path: /items
      method: GET
      params:
        updated_since: "{{last_sync}}"

target:
  type: rest
  base_url: https://api.destination.com/v2
  auth:
    type: api_key
    header: X-API-Key
    key: ${TARGET_API_KEY}  # Will be read from environment variable
  endpoints:
    create_item:
      path: /items
      method: POST

mapping:
  - source: list_items
    target: create_item
    fields:
      - source: id
        target: external_id
      - source: name
        target: title
      - source: description
        target: body.content
      - source: created_at
        target: metadata.created
        transform: iso_to_timestamp
```

## Step 2: Set Up Environment Variables

Set your API credentials as environment variables:

```bash
# Linux/macOS
export SOURCE_API_TOKEN=your_source_api_token
export TARGET_API_KEY=your_target_api_key

# Windows (Command Prompt)
set SOURCE_API_TOKEN=your_source_api_token
set TARGET_API_KEY=your_target_api_key

# Windows (PowerShell)
$env:SOURCE_API_TOKEN="your_source_api_token"
$env:TARGET_API_KEY="your_target_api_key"
```

## Step 3: Validate Your Configuration

Check that your configuration is valid:

```bash
apilinker validate --config my_config.yaml
```

## Step 4: Run a Test Sync

Perform a dry run to see what would happen without making changes:

```bash
apilinker sync --config my_config.yaml --dry-run
```

This shows details about the source and target APIs and the field mappings that will be used.

## Step 5: Perform the Sync

Now, run the actual sync operation:

```bash
apilinker sync --config my_config.yaml
```

You'll see output showing the number of items synced and any errors encountered.

## Step 6: Schedule Recurring Syncs (Optional)

To run the sync on a schedule:

```bash
apilinker run --config my_config.yaml
```

This starts a process that runs the sync based on the schedule configuration (which defaults to hourly if not specified).

## Using ApiLinker as a Python Library

You can also use ApiLinker directly in your Python code:

```python
from apilinker import ApiLinker

# Initialize with config file
linker = ApiLinker(config_path="my_config.yaml")

# Run the sync
result = linker.sync()
print(f"Synced {result.count} items")

# Check for errors
if not result.success:
    for error in result.errors:
        print(f"Error: {error}")
```

## Next Steps

- Learn how to create [custom data transformations](examples/transformers.md)
- Configure [advanced authentication methods](guide/authentication.md) 
- Set up [complex field mappings](guide/mapping.md) with conditions and filtering
- Explore [pagination handling](guide/connectors.md) for large datasets

For complete details on all configuration options and features, see the [Configuration Guide](configuration.md).
