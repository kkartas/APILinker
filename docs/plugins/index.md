# Extending with Plugins

ApiLinker is designed to be easily extended through plugins. This guide explains how to create, register, and use custom plugins.

## Plugin Types

ApiLinker supports three main types of plugins:

1. **Transformer Plugins**: Convert data between formats, perform calculations, or modify values
2. **Connector Plugins**: Handle communication with different API types and protocols
3. **Auth Plugins**: Implement authentication mechanisms for various services

## Creating Custom Plugins

### Transformer Plugins

Transformer plugins modify data during transfer between source and target. To create a transformer plugin:

```python
from apilinker.core.plugins import TransformerPlugin

class MyTransformer(TransformerPlugin):
    """Description of what your transformer does."""
    
    plugin_name = "my_transformer"  # Name used to reference the plugin
    
    def transform(self, value, **kwargs):
        """
        Transform the input value.
        
        Args:
            value: The input value to transform
            **kwargs: Additional parameters from the mapping configuration
            
        Returns:
            Transformed value
        """
        # Your transformation logic here
        transformed_value = do_something_with(value)
        return transformed_value
        
    def validate_input(self, value):
        """
        Optional method to validate input before transformation.
        
        Args:
            value: The input value to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(value, str)  # Example validation
```

### Connector Plugins

Connector plugins handle communication with different API types:

```python
from apilinker.core.plugins import ConnectorPlugin

class MyConnector(ConnectorPlugin):
    """Custom connector for a specific API type."""
    
    plugin_name = "my_connector"
    
    def connect(self, **kwargs):
        """
        Establish a connection to the API.
        
        Args:
            **kwargs: Connection parameters
            
        Returns:
            Connection object or context
        """
        # Create and return a connection object
        return {"connection_id": "12345", "base_url": kwargs.get("base_url")}
        
    def fetch(self, connection, endpoint, **kwargs):
        """
        Fetch data from the API.
        
        Args:
            connection: Connection object from connect()
            endpoint: Endpoint path
            **kwargs: Additional parameters
            
        Returns:
            API response data
        """
        # Fetch data using the connection
        return fetch_data(connection, endpoint, **kwargs)
        
    def send(self, connection, endpoint, data, **kwargs):
        """
        Send data to the API.
        
        Args:
            connection: Connection object from connect()
            endpoint: Endpoint path
            data: Data to send
            **kwargs: Additional parameters
            
        Returns:
            API response data
        """
        # Send data using the connection
        return send_data(connection, endpoint, data, **kwargs)
```

### Auth Plugins

Auth plugins handle different authentication methods:

```python
from apilinker.core.plugins import AuthPlugin

class MyAuth(AuthPlugin):
    """Custom authentication plugin."""
    
    plugin_name = "my_auth"
    
    def authenticate(self, **kwargs):
        """
        Authenticate with the API.
        
        Args:
            **kwargs: Authentication parameters
            
        Returns:
            dict: Authentication details including headers, tokens, etc.
        """
        # Perform authentication
        token = get_token(kwargs.get("client_id"), kwargs.get("client_secret"))
        
        # Return authentication details
        return {
            "type": "bearer",
            "headers": {"Authorization": f"Bearer {token}"},
            "token": token
        }
        
    def validate_credentials(self, credentials):
        """
        Validate authentication credentials.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(credentials, dict) and "token" in credentials
```

## Registering Plugins

### Method 1: Manual Registration

Register your plugin directly with the plugin manager:

```python
from apilinker import ApiLinker
from my_plugins import MyTransformer

# Initialize ApiLinker
linker = ApiLinker()

# Register the plugin
linker.plugin_manager.register_plugin(MyTransformer)
```

### Method 2: Auto-Discovery

Place your plugin modules in one of these locations for automatic discovery:

1. Built-in plugins: `apilinker/plugins/builtin/`
2. User plugins: `~/.apilinker/plugins/`
3. Custom directory specified in configuration

The plugin module should be a `.py` file that defines your plugin class.

## Using Custom Plugins

### Transformer Plugins

Use your transformer in mapping configurations:

```python
linker.add_mapping(
    source="get_users",
    target="create_contacts",
    fields=[
        {"source": "id", "target": "external_id"},
        {"source": "phone", "target": "phoneNumber", "transform": "my_transformer"}
    ]
)
```

Or use it programmatically:

```python
transformer = linker.plugin_manager.get_transformer("my_transformer")
transformed_value = transformer("original_value", extra_param="value")
```

### Connector Plugins

Specify your connector type in API configurations:

```python
linker.add_source(
    type="my_connector",  # Your connector plugin name
    base_url="https://api.example.com",
    # Other configuration...
)
```

### Auth Plugins

Specify your auth type in API configurations:

```python
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    auth={
        "type": "my_auth",  # Your auth plugin name
        "client_id": "${CLIENT_ID}",
        "client_secret": "${CLIENT_SECRET}"
    }
)
```

## Best Practices

1. **Error Handling**: Include robust error handling in your plugins
2. **Documentation**: Add detailed docstrings to your plugin classes and methods
3. **Input Validation**: Always validate inputs to prevent errors
4. **Version Compatibility**: Specify the ApiLinker versions your plugin is compatible with
5. **Testing**: Write unit tests for your plugins

## Examples

For more detailed examples, see the [example plugins](examples.md) documentation.
