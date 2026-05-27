=======================
Plugin System Reference
=======================

.. automodule:: apilinker.core.plugins
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

ApiLinker's plugin system allows you to extend functionality through custom plugins
for data transformation, API connections, and authentication methods. The system is designed
to be flexible, type-safe, and easy to use.

Plugin Types
-----------

ApiLinker supports three main types of plugins:

1. **Transformer Plugins**: Convert data between formats, validate values, or perform calculations
2. **Connector Plugins**: Handle communication with different API types
3. **Auth Plugins**: Implement various authentication methods

Creating Custom Plugins
---------------------

To create a custom plugin, inherit from one of the base classes and implement the required methods:

.. code-block:: python

    from apilinker.core.plugins import TransformerPlugin
    
    class PhoneNumberFormatter(TransformerPlugin):
        """Format phone numbers to E.164 international format."""
        
        plugin_name = "phone_formatter"
        
        def transform(self, value, **kwargs):
            if not value:
                return None
                
            # Remove non-digits
            digits = ''.join(c for c in value if c.isdigit())
            
            # Format based on length
            if len(digits) == 10:  # US number without country code
                return f"+1{digits}"
            elif len(digits) > 10:  # Assume international number
                return f"+{digits}"
            else:
                return value  # Return original if can't format

Plugin Discovery
---------------

ApiLinker automatically discovers plugins from several locations:

1. Built-in plugins in ``apilinker.plugins.builtin``
2. User plugins in ``~/.apilinker/plugins/``
3. Package plugins in ``apilinker/plugins/``
4. Custom directories specified by the user

Using Plugins
------------

Once a plugin is registered, it can be used in configuration files or programmatically:

.. code-block:: yaml

    # In YAML config
    mapping:
      - source: user.phone
        target: contact.phoneNumber
        transform: phone_formatter

.. code-block:: python

    # In Python code
    from apilinker import ApiLinker
    
    linker = ApiLinker()
    
    # Use transformer directly
    transformer = linker.plugin_manager.get_transformer("phone_formatter")
    formatted = transformer("+1 (555) 123-4567")
    
    # Use auth plugin
    auth = linker.plugin_manager.get_auth_plugin("oauth2")
    credentials = auth.authenticate(
        client_id="client_id",
        client_secret="client_secret",
        token_url="https://auth.example.com/token"
    )

Error Handling
-------------

The plugin system includes comprehensive error handling:

- ``PluginNotFoundError``: Raised when a requested plugin cannot be found
- ``PluginValidationError``: Raised when a plugin fails validation checks
- ``PluginInitializationError``: Raised when a plugin cannot be initialized

Plugins should also include their own validation and error handling to ensure
robust operation and clear error messages.
