# ApiLinker

**A universal bridge to connect, map, and automate data transfer between any two REST APIs.**

[![PyPI version](https://badge.fury.io/py/apilinker.svg)](https://badge.fury.io/py/apilinker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/kkartas/apilinker/workflows/Tests/badge.svg)](https://github.com/kkartas/apilinker/actions)
[![docs](https://readthedocs.org/projects/apilinker/badge/?version=latest)](https://apilinker.readthedocs.io/en/latest/)

## What is ApiLinker?

ApiLinker is an open-source Python package that makes it easy to connect, map, and automate data transfer between any two REST APIs. It provides a flexible and extensible framework for building API integrations with minimal code.

<!-- Overview image removed until asset is added to docs/assets -->

## Key Features

- 🔄 **Connect** any two REST APIs with simple configuration
- 🗺️ **Map** fields between APIs with powerful transformations
- 📊 **Transform** data with built-in functions or custom Python code
- 🔒 **Secure** authentication (API Key, Bearer Token, Basic Auth, OAuth2)
- 📝 **Configure** via YAML/JSON or Python code
- 🕒 **Schedule** data syncs on intervals or cron schedules
- 📋 **Validate** data with schemas and custom rules
- 🔌 **Extend** with custom plugins for connectors and transforms

## Installation

```bash
pip install apilinker
```

## Quick Example

### Configuration File (YAML)

```yaml
source:
  type: rest
  base_url: https://api.example.com/v1
  auth:
    type: bearer
    token: ${SOURCE_API_TOKEN}
  endpoints:
    list_items:
      path: /items
      method: GET

target:
  type: rest
  base_url: https://api.destination.com/v2
  auth:
    type: api_key
    header: X-API-Key
    key: ${TARGET_API_KEY}
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
```

### Command Line Usage

```bash
# Run a sync with a configuration file
apilinker sync --config config.yaml

# Start a scheduled sync process
apilinker run --config config.yaml
```

### Python Library Usage

```python
from apilinker import ApiLinker

# Initialize with config file
linker = ApiLinker(config_path="config.yaml")

# Or configure programmatically
linker = ApiLinker()
linker.add_source(
    type="rest",
    base_url="https://api.example.com/v1",
    auth={
        "type": "bearer",
        "token": "your_token_here"
    }
)
linker.add_target(
    type="rest",
    base_url="https://api.destination.com/v2",
    auth={
        "type": "api_key",
        "header": "X-API-Key",
        "key": "your_key_here"
    }
)
linker.add_mapping(
    source="list_items",
    target="create_item",
    fields=[
        {"source": "id", "target": "external_id"},
        {"source": "name", "target": "title"}
    ]
)

# Run the sync
result = linker.sync()
print(f"Synced {result.count} items")
```

## Use Cases

- **Data Integration**: Connect systems that need to share data but lack native integrations
- **API Migration**: Transfer data when migrating between API versions or providers
- **Data Pipelines**: Build automated data flows between systems
- **Research Data Collection**: Gather and standardize data from multiple API sources
- **Webhook Forwarding**: Transform and route webhook payloads to other services

## Why ApiLinker?

- **Simple Configuration**: Define complex integrations with minimal YAML or Python code
- **Flexible Mapping**: Map between different data structures with nested fields and transformations
- **Minimal Dependencies**: Built on standard Python libraries with minimal external dependencies
- **Extensible Design**: Add custom connectors, transformers, and authentication methods
- **Production Ready**: Robust error handling, retries, and logging

## Connectors Index

See the list of built-in connectors with links to source files and basic usage in the [Connectors Index](connectors_index.md).

## Error Handling

Configure circuit breakers, retries, and the DLQ with a few lines. See [Error Handling and Recovery](error_handling.md).

## License

ApiLinker is released under the MIT License. See the [LICENSE](https://github.com/kkartas/apilinker/blob/main/LICENSE) file for details.
