# ApiLinker

[![PyPI version](https://badge.fury.io/py/apilinker.svg)](https://badge.fury.io/py/apilinker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/apilinker/workflows/Tests/badge.svg)](https://github.com/yourusername/apilinker/actions)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://yourusername.github.io/apilinker)

A universal bridge to connect, map, and automate data transfer between any two REST APIs.

## Features

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

## Quick Start

### Using the CLI

Create a configuration file `config.yaml`:

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
      params:
        updated_since: "{{last_sync}}"

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
  - source: items
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

schedule:
  type: interval
  minutes: 60

logging:
  level: INFO
  file: apilinker.log
```

Run a sync with:

```bash
apilinker sync --config config.yaml
```

### Using as a Python Library

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
    source="items",
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

## Documentation

For full documentation, visit [https://yourusername.github.io/apilinker](https://yourusername.github.io/apilinker).

- [Installation Guide](https://yourusername.github.io/apilinker/installation)
- [Configuration Guide](https://yourusername.github.io/apilinker/configuration)
- [API Reference](https://yourusername.github.io/apilinker/api)
- [Examples](https://yourusername.github.io/apilinker/examples)
- [Extending with Plugins](https://yourusername.github.io/apilinker/plugins)

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e ".[dev]"`)
4. Make your changes
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
