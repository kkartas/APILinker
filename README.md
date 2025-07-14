# ApiLinker

[![PyPI version](https://badge.fury.io/py/apilinker.svg)](https://badge.fury.io/py/apilinker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/kkartas/apilinker/workflows/Tests/badge.svg)](https://github.com/kkartas/apilinker/actions)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://kkartas.github.io/apilinker)

<div align="center">
  <h3>A universal bridge to connect, map, and automate data transfer between any two REST APIs</h3>
</div>

---

**ApiLinker** is an open-source Python package that simplifies the integration of REST APIs by providing a universal bridging solution. Built for developers, data engineers, and researchers who need to connect different systems without writing repetitive boilerplate code.

---

## 🌟 Features

- 🔄 **Universal Connectivity** - Connect any two REST APIs with simple configuration
- 🗺️ **Powerful Mapping** - Transform data between APIs with field mapping and path expressions
- 📊 **Data Transformation** - Apply built-in or custom transformations to your data
- 🔒 **Comprehensive Authentication** - Support for API Key, Bearer Token, Basic Auth, and OAuth2
- 📝 **Flexible Configuration** - Use YAML/JSON or configure programmatically in Python
- 🕒 **Automated Scheduling** - Run syncs once, on intervals, or using cron expressions
- 📋 **Data Validation** - Validate data with schemas and custom rules
- 🔌 **Plugin Architecture** - Extend with custom connectors, transformers, and authentication methods
- 📈 **Pagination Handling** - Automatic handling of paginated API responses
- 🔍 **Error Recovery** - Built-in retry logic and error handling
- 📦 **Minimal Dependencies** - Lightweight core with minimal external requirements

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Authentication Methods](#authentication-methods)
- [Field Mapping](#field-mapping)
- [Data Transformations](#data-transformations)
- [Scheduling](#scheduling)
- [Command Line Interface](#command-line-interface)
- [Python API](#python-api)
- [Examples](#examples)
- [Extending ApiLinker](#extending-apilinker)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [License](#license)

## 🚀 Installation

### Standard Installation

```bash
pip install apilinker
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/kkartas/apilinker.git
cd apilinker

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install with documentation tools
pip install -e ".[docs]"
```

## 🏁 Quick Start

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

For full documentation, visit [https://kkartas.github.io/apilinker](https://kkartas.github.io/apilinker).

- [Installation Guide](https://kkartas.github.io/apilinker/installation)
- [Configuration Guide](https://kkartas.github.io/apilinker/configuration)
- [API Reference](https://kkartas.github.io/apilinker/api)
- [Examples](https://kkartas.github.io/apilinker/examples)
- [Extending with Plugins](https://kkartas.github.io/apilinker/plugins)

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
