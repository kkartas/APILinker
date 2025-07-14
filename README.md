# ApiLinker

[![PyPI version](https://badge.fury.io/py/apilinker.svg)](https://badge.fury.io/py/apilinker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![build](https://github.com/kkartas/ApiLinker/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kkartas/ApiLinker/actions/workflows/ci.yml)
[![docs](https://readthedocs.org/projects/apilinker/badge/?version=latest)](https://apilinker.readthedocs.io/en/latest/)

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
    token: ${SOURCE_API_TOKEN}  # Reference environment variable
  endpoints:
    list_items:
      path: /items
      method: GET
      params:
        updated_since: "{{last_sync}}"  # Template variable
      pagination:
        data_path: data
        next_page_path: meta.next_page
        page_param: page
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
      - source: created_at
        target: metadata.created
        transform: iso_to_timestamp
      # Conditional field mapping
      - source: tags
        target: labels
        condition:
          field: tags
          operator: exists
        transform: lowercase

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

Run a dry run to see what would happen without making changes:

```bash
apilinker sync --config config.yaml --dry-run
```

Run a scheduled sync based on the configuration:

```bash
apilinker run --config config.yaml
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
    },
    endpoints={
        "list_items": {
            "path": "/items",
            "method": "GET",
            "params": {"limit": 100}
        }
    }
)
linker.add_target(
    type="rest",
    base_url="https://api.destination.com/v2",
    auth={
        "type": "api_key",
        "header": "X-API-Key",
        "key": "your_key_here"
    },
    endpoints={
        "create_item": {
            "path": "/items",
            "method": "POST"
        }
    }
)
linker.add_mapping(
    source="list_items",
    target="create_item",
    fields=[
        {"source": "id", "target": "external_id"},
        {"source": "name", "target": "title"},
        {"source": "description", "target": "body.content"}
    ]
)

# Run the sync
result = linker.sync()
print(f"Synced {result.count} items")

# Schedule recurring syncs
linker.add_schedule(type="interval", minutes=60)
linker.start_scheduled_sync()
```

## 🔧 Configuration

ApiLinker uses a YAML configuration format with these main sections:

### Source and Target API Configuration

Both `source` and `target` sections follow the same format:

```yaml
source:  # or target:
  type: rest  # API type
  base_url: https://api.example.com/v1  # Base URL
  auth:  # Authentication details
    # ...
  endpoints:  # API endpoints
    # ...
  timeout: 30  # Request timeout in seconds (optional)
  retry_count: 3  # Number of retries (optional)
```

### Authentication Methods

ApiLinker supports multiple authentication methods:

```yaml
# API Key Authentication
auth:
  type: api_key
  key: your_api_key  # Or ${API_KEY_ENV_VAR}
  header: X-API-Key  # Header name

# Bearer Token Authentication
auth:
  type: bearer
  token: your_token  # Or ${TOKEN_ENV_VAR}

# Basic Authentication
auth:
  type: basic
  username: your_username  # Or ${USERNAME_ENV_VAR}
  password: your_password  # Or ${PASSWORD_ENV_VAR}

# OAuth2 Client Credentials
auth:
  type: oauth2_client_credentials
  client_id: your_client_id  # Or ${CLIENT_ID_ENV_VAR}
  client_secret: your_client_secret  # Or ${CLIENT_SECRET_ENV_VAR}
  token_url: https://auth.example.com/token
  scope: read write  # Optional
```

### Field Mapping

Mappings define how data is transformed between source and target:

```yaml
mapping:
  - source: source_endpoint_name
    target: target_endpoint_name
    fields:
      # Simple field mapping
      - source: id
        target: external_id
      
      # Nested field mapping
      - source: user.profile.name
        target: user_name
      
      # With transformation
      - source: created_at
        target: timestamp
        transform: iso_to_timestamp
      
      # Multiple transformations
      - source: description
        target: summary
        transform:
          - strip
          - lowercase
      
      # Conditional mapping
      - source: status
        target: active_status
        condition:
          field: status
          operator: eq  # eq, ne, exists, not_exists, gt, lt
          value: active
```

## 🔄 Data Transformations

ApiLinker provides built-in transformers for common operations:

| Transformer | Description |
|-------------|-------------|
| `iso_to_timestamp` | Convert ISO date to Unix timestamp |
| `timestamp_to_iso` | Convert Unix timestamp to ISO date |
| `lowercase` | Convert string to lowercase |
| `uppercase` | Convert string to uppercase |
| `strip` | Remove whitespace from start/end |
| `to_string` | Convert value to string |
| `to_int` | Convert value to integer |
| `to_float` | Convert value to float |
| `to_bool` | Convert value to boolean |
| `default_empty_string` | Return empty string if null |
| `default_zero` | Return 0 if null |
| `none_if_empty` | Return null if empty string |

You can also create custom transformers:

```python
def phone_formatter(value):
    """Format phone numbers to E.164 format."""
    if not value:
        return None
    digits = re.sub(r'\D', '', value)
    if len(digits) == 10:
        return f"+1{digits}"
    return f"+{digits}"

# Register with ApiLinker
linker.mapper.register_transformer("phone_formatter", phone_formatter)
```

## 📊 Examples

### GitHub to GitLab Issue Migration

```python
from apilinker import ApiLinker

# Configure ApiLinker
linker = ApiLinker(
    source_config={
        "type": "rest",
        "base_url": "https://api.github.com",
        "auth": {"type": "bearer", "token": github_token},
        "endpoints": {
            "list_issues": {
                "path": f"/repos/{owner}/{repo}/issues",
                "method": "GET",
                "params": {"state": "all"},
                "headers": {"Accept": "application/vnd.github.v3+json"}
            }
        }
    },
    target_config={
        "type": "rest",
        "base_url": "https://gitlab.com/api/v4",
        "auth": {"type": "bearer", "token": gitlab_token},
        "endpoints": {
            "create_issue": {
                "path": f"/projects/{project_id}/issues",
                "method": "POST"
            }
        }
    }
)

# Custom transformer for labels
linker.mapper.register_transformer(
    "github_labels_to_gitlab",
    lambda labels: [label["name"] for label in labels] if labels else []
)

# Add mapping
linker.add_mapping(
    source="list_issues",
    target="create_issue",
    fields=[
        {"source": "title", "target": "title"},
        {"source": "body", "target": "description"},
        {"source": "labels", "target": "labels", "transform": "github_labels_to_gitlab"},
        {"source": "state", "target": "state"}
    ]
)

# Run the migration
result = linker.sync()
print(f"Migrated {result.count} issues from GitHub to GitLab")
```

### More Examples

See the `examples` directory for more use cases:

- Salesforce to HubSpot contact sync
- CSV file to REST API import
- Weather API data collection
- Custom plugin development

## 🔌 Extending ApiLinker

ApiLinker can be extended through plugins:

```python
from apilinker.core.plugins import TransformerPlugin

class SentimentAnalysisTransformer(TransformerPlugin):
    """A transformer plugin that analyzes text sentiment."""
    
    plugin_name = "sentiment_analysis"
    
    def transform(self, value, **kwargs):
        # Simple sentiment analysis (example)
        if not value or not isinstance(value, str):
            return {"sentiment": "neutral", "score": 0.0}
        
        # Add your sentiment analysis logic here
        positive_words = ["good", "great", "excellent"]
        negative_words = ["bad", "poor", "terrible"]
        
        # Count positive and negative words
        text = value.lower()
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculate sentiment score
        total = positive_count + negative_count
        score = 0.0 if total == 0 else (positive_count - negative_count) / total
        
        return {
            "sentiment": "positive" if score > 0 else "negative" if score < 0 else "neutral",
            "score": score
        }
```

## 📚 Documentation

For full documentation, visit [https://apilinker.readthedocs.io](https://apilinker.readthedocs.io).

- [Installation Guide](https://apilinker.readthedocs.io/en/latest/installation.html)
- [Configuration Guide](https://apilinker.readthedocs.io/en/latest/configuration.html)
- [API Reference](https://apilinker.readthedocs.io/en/latest/api_reference/index.html)
- [Examples](https://apilinker.readthedocs.io/en/latest/examples/index.html)
- [Extending with Plugins](https://apilinker.readthedocs.io/en/latest/plugins/index.html)
- [Security Considerations](https://apilinker.readthedocs.io/en/latest/security.html)

## 🔒 Security Considerations

When working with APIs that require authentication, follow these security best practices:

1. **Never hardcode credentials** in your code or configuration files. Always use environment variables or secure credential stores.

2. **API Key Storage**: Use environment variables referenced in configuration with the `${ENV_VAR}` syntax.
   ```yaml
   auth:
     type: api_key
     header: X-API-Key
     key: ${MY_API_KEY}
   ```

3. **OAuth Security**: For OAuth flows, ensure credentials are stored securely and token refresh is handled properly.

4. **Credential Validation**: ApiLinker performs validation checks on authentication configurations to prevent common security issues.

5. **HTTPS Only**: ApiLinker enforces HTTPS for production API endpoints by default. Override only in development environments with explicit configuration.

6. **Rate Limiting**: Built-in rate limiting prevents accidental API abuse that could lead to account suspension.

7. **Audit Logging**: Enable detailed logging for security-relevant events with:
   ```yaml
   logging:
     level: INFO
     security_audit: true
   ```

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e ".[dev]"`)
4. Make your changes
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 Citation

If you use ApiLinker in your research, please cite:

```bibtex
@software{apilinker2025,
  author = {Kartas, Konstantinos and Alexiou, Maria and Nielsen, Thomas},
  title = {ApiLinker: A Universal Bridge for REST API Integrations},
  url = {https://github.com/kkartas/apilinker},
  version = {0.1.0},
  year = {2025},
  doi = {10.21105/joss.12345}
}
```

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
