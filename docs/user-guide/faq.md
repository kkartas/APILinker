# Frequently Asked Questions (FAQ)

This document addresses common questions about ApiLinker.

## General Questions

### What is ApiLinker?

ApiLinker is a Python library that provides a universal bridge for connecting, mapping, and automating data transfer between any two REST APIs. It allows you to configure API integrations without writing repetitive boilerplate code.

### What Python versions are supported?

ApiLinker supports Python 3.8 and above.

### Is ApiLinker free to use?

Yes, ApiLinker is open-source software released under the MIT license, which allows for free use, modification, and distribution.

### Can I use ApiLinker in commercial projects?

Yes, the MIT license allows for commercial use.

## Installation & Setup

### How do I install ApiLinker?

```bash
pip install apilinker
```

### Why am I getting an error during installation?

Common installation issues include:

1. **Python version**: Make sure you're using Python 3.8 or newer
2. **Permission issues**: Try using `pip install --user apilinker` or use a virtual environment
3. **Dependency conflicts**: Create a clean virtual environment and try installing again

### How can I verify the installation?

```python
import apilinker
print(apilinker.__version__)
```

## Configuration

### How do I connect to an API that requires a custom authentication method?

You can create a custom authentication plugin by extending the `AuthPlugin` class:

```python
from apilinker.core.plugins import AuthPlugin

class CustomAuth(AuthPlugin):
    plugin_name = "custom_auth"
    
    def authenticate(self, **kwargs):
        # Custom authentication logic
        return {
            "headers": {"X-Custom-Auth": generate_auth_header(kwargs)},
            "type": "custom"
        }
```

### Can I use ApiLinker with GraphQL APIs?

Yes, you can create a custom connector plugin for GraphQL or use the REST connector with POST requests and GraphQL queries in the body.

### How do I handle API rate limits?

ApiLinker does not include built-in rate limiting. Use provider guidance, exponential backoff, and retries to handle 429 responses.

```yaml
source:
  type: rest
  base_url: "https://api.example.com"
  rate_limit:
    requests_per_second: 5
  retry:
    max_attempts: 3
    delay_seconds: 2
    backoff_factor: 1.5
    status_codes: [429, 500, 502, 503, 504]
```

## Data Mapping

### How do I transform data between APIs?

Use field mappings with transformers:

```yaml
fields:
  - source: user.profile.name
    target: contact.fullName
    transform: uppercase
```

### Can I apply multiple transformations to a single field?

Yes, specify them as a list:

```yaml
fields:
  - source: tags
    target: categories
    transform:
      - lowercase
      - strip
      - none_if_empty
```

### How do I create custom data transformers?

Register a custom transformer function:

```python
def phone_formatter(value, **kwargs):
    if not value:
        return ""
    digits = ''.join(c for c in value if c.isdigit())
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    return value

linker.mapper.register_transformer("phone_formatter", phone_formatter)
```

## Scheduling

### How do I schedule a sync to run periodically?

```python
# Run every hour
linker.add_schedule(interval_minutes=60)

# Or use cron expression
linker.add_schedule(cron_expression="0 */6 * * *")  # Every 6 hours

# Start the scheduler
linker.start_scheduled_sync()
```

### How do I stop a scheduled sync?

```python
linker.stop_scheduled_sync()
```

### Can I run multiple schedules with different frequencies?

Yes, you can create multiple ApiLinker instances with different schedules.

## Error Handling

### How do I handle errors during sync?

You can provide an error handler function:

```python
def handle_error(error, context):
    print(f"Error during sync: {error}")
    print(f"Context: {context}")
    # Log error, send notification, etc.
    return True  # Return True to retry, False to abort

linker.add_error_handler(handle_error)
```

### How can I debug issues with my API connections?

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in configuration
linker = ApiLinker(debug=True)
```

## Performance

### How can I optimize ApiLinker for large data transfers?

1. Use pagination settings appropriate for the API
2. Set batch sizes for processing large datasets
3. Consider using async operations for concurrent requests

```yaml
source:
  endpoints:
    get_data:
      pagination:
        limit: 1000  # Request larger page sizes
      batch_size: 500  # Process in batches
```

### Does ApiLinker support caching?

Yes, ApiLinker includes response caching capabilities:

```yaml
source:
  cache:
    enabled: true
    ttl: 3600  # Cache TTL in seconds
```

## Contributing

### How can I contribute to ApiLinker?

1. Fork the repository on GitHub
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Submit a pull request

### Where can I report bugs or request features?

Report issues on the [GitHub Issues page](https://github.com/kkartas/apilinker/issues).

## Advanced Usage

### Can ApiLinker handle binary data or file transfers?

Yes, ApiLinker can handle binary data transfers. Configure the content type and use appropriate encodings:

```yaml
target:
  endpoints:
    upload_file:
      path: /files/upload
      method: POST
      headers:
        Content-Type: application/octet-stream
```

### Is it possible to extend ApiLinker with custom plugins?

Yes, ApiLinker's plugin architecture allows for extending all major components:

- Create custom transformers
- Create custom connectors for different API types
- Create custom authentication methods
- Create custom validation rules

See the [Extending with Plugins](plugins/index.md) documentation for details.
