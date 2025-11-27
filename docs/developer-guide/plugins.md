# Plugin System Architecture

ApiLinker features an extensible plugin architecture allowing users to add custom functionality without modifying the core codebase.

## Plugin Types

- **ConnectorPlugin**: Custom API connectors.
- **TransformerPlugin**: Data transformation functions.
- **AuthPlugin**: Authentication methods.
- **SchedulerPlugin**: Custom scheduling triggers.
- **MonitoringPlugin**: Metrics and monitoring.

## Creating a Plugin

Plugins inherit from `PluginBase` and must implement `initialize` and `cleanup` methods.

### Example: Custom Connector

```python
from apilinker.core.plugins import ConnectorPlugin
from apilinker.core.connector import ApiConnector

class CustomAPIConnector(ConnectorPlugin, ApiConnector):
    plugin_type = "connector"
    plugin_name = "custom_api"
    
    def fetch_data(self, endpoint_name: str, **kwargs):
        # Implementation
        pass
```

### Plugin Discovery

The `PluginManager` automatically discovers plugins in:
1. The `apilinker.plugins` namespace.
2. Directories specified in configuration.
3. Registered entry points.
