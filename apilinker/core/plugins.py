"""
Plugin system for extending ApiLinker functionality.
"""

import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class PluginBase:
    """Base class for all ApiLinker plugins."""
    
    plugin_type = "base"
    plugin_name = "base"
    
    def __init__(self, **kwargs):
        self.config = kwargs
        logger.debug(f"Initialized {self.plugin_type} plugin: {self.plugin_name}")
    
    @classmethod
    def get_plugin_info(cls) -> Dict[str, Any]:
        """Get information about this plugin."""
        return {
            "type": cls.plugin_type,
            "name": cls.plugin_name,
            "description": cls.__doc__,
        }


class TransformerPlugin(PluginBase):
    """Base class for data transformation plugins."""
    
    plugin_type = "transformer"
    
    def transform(self, value: Any, **kwargs) -> Any:
        """
        Transform a value.
        
        Args:
            value: Value to transform
            **kwargs: Additional parameters for the transformation
            
        Returns:
            Transformed value
        """
        raise NotImplementedError("Transformer plugins must implement transform method")


class ConnectorPlugin(PluginBase):
    """Base class for API connector plugins."""
    
    plugin_type = "connector"
    
    def connect(self, **kwargs) -> Any:
        """
        Create a connection to the API.
        
        Args:
            **kwargs: Connection parameters
            
        Returns:
            Connection object
        """
        raise NotImplementedError("Connector plugins must implement connect method")
    
    def fetch(self, connection: Any, endpoint: str, **kwargs) -> Any:
        """
        Fetch data from the API.
        
        Args:
            connection: Connection object from connect()
            endpoint: Endpoint to fetch from
            **kwargs: Additional parameters
            
        Returns:
            Fetched data
        """
        raise NotImplementedError("Connector plugins must implement fetch method")
    
    def send(self, connection: Any, endpoint: str, data: Any, **kwargs) -> Any:
        """
        Send data to the API.
        
        Args:
            connection: Connection object from connect()
            endpoint: Endpoint to send to
            data: Data to send
            **kwargs: Additional parameters
            
        Returns:
            API response
        """
        raise NotImplementedError("Connector plugins must implement send method")


class AuthPlugin(PluginBase):
    """Base class for authentication plugins."""
    
    plugin_type = "auth"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """
        Perform authentication and return credentials.
        
        Args:
            **kwargs: Authentication parameters
            
        Returns:
            Authentication result including credentials
        """
        raise NotImplementedError("Auth plugins must implement authenticate method")


class PluginManager:
    """
    Manager for loading and using plugins.
    
    This class handles the discovery, loading, and management of plugins
    for extending ApiLinker functionality.
    """
    
    def __init__(self):
        self.plugins: Dict[str, Dict[str, Type[PluginBase]]] = {
            "transformer": {},
            "connector": {},
            "auth": {},
        }
        logger.debug("Initialized PluginManager")
    
    def discover_plugins(self, plugin_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover available plugins.
        
        Args:
            plugin_dir: Directory to search for plugins (None for default paths)
            
        Returns:
            List of discovered plugin info
        """
        discovered = []
        
        # Check built-in plugins
        try:
            from apilinker.plugins import builtin
            module_plugins = self._get_plugins_from_module(builtin)
            discovered.extend(module_plugins)
        except ImportError:
            logger.debug("No built-in plugins found")
        
        # Check user-specified directory
        if plugin_dir:
            if os.path.exists(plugin_dir) and os.path.isdir(plugin_dir):
                sys.path.insert(0, plugin_dir)
                
                for filename in os.listdir(plugin_dir):
                    if filename.endswith(".py") and not filename.startswith("_"):
                        module_name = filename[:-3]
                        try:
                            module = importlib.import_module(module_name)
                            module_plugins = self._get_plugins_from_module(module)
                            discovered.extend(module_plugins)
                        except ImportError as e:
                            logger.warning(f"Failed to import plugin {module_name}: {e}")
                
                sys.path.pop(0)
            else:
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
        
        # Check user's home directory
        home_plugin_dir = os.path.join(Path.home(), ".apilinker", "plugins")
        if os.path.exists(home_plugin_dir) and os.path.isdir(home_plugin_dir):
            sys.path.insert(0, home_plugin_dir)
            
            for filename in os.listdir(home_plugin_dir):
                if filename.endswith(".py") and not filename.startswith("_"):
                    module_name = filename[:-3]
                    try:
                        module = importlib.import_module(module_name)
                        module_plugins = self._get_plugins_from_module(module)
                        discovered.extend(module_plugins)
                    except ImportError as e:
                        logger.warning(f"Failed to import plugin {module_name}: {e}")
            
            sys.path.pop(0)
        
        return discovered
    
    def _get_plugins_from_module(self, module) -> List[Dict[str, Any]]:
        """
        Extract plugin classes from a module.
        
        Args:
            module: Python module object
            
        Returns:
            List of plugin information dictionaries
        """
        plugins = []
        
        # Find all classes derived from PluginBase
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj is not PluginBase:
                if obj is not TransformerPlugin and obj is not ConnectorPlugin and obj is not AuthPlugin:
                    # Register the plugin
                    plugin_info = obj.get_plugin_info()
                    plugins.append(plugin_info)
                    self.register_plugin(obj)
        
        return plugins
    
    def register_plugin(self, plugin_class: Type[PluginBase]) -> None:
        """
        Register a plugin class.
        
        Args:
            plugin_class: Plugin class to register
        """
        plugin_type = plugin_class.plugin_type
        plugin_name = plugin_class.plugin_name
        
        if plugin_type not in self.plugins:
            self.plugins[plugin_type] = {}
        
        if plugin_name in self.plugins[plugin_type]:
            logger.warning(f"Overwriting existing plugin: {plugin_type}.{plugin_name}")
        
        self.plugins[plugin_type][plugin_name] = plugin_class
        logger.debug(f"Registered plugin: {plugin_type}.{plugin_name}")
    
    def get_plugin(self, plugin_type: str, plugin_name: str) -> Optional[Type[PluginBase]]:
        """
        Get a plugin class by type and name.
        
        Args:
            plugin_type: Type of plugin
            plugin_name: Name of plugin
            
        Returns:
            Plugin class or None if not found
        """
        if plugin_type not in self.plugins or plugin_name not in self.plugins[plugin_type]:
            return None
        
        return self.plugins[plugin_type][plugin_name]
    
    def instantiate_plugin(self, plugin_type: str, plugin_name: str, **kwargs) -> Optional[PluginBase]:
        """
        Create an instance of a plugin.
        
        Args:
            plugin_type: Type of plugin
            plugin_name: Name of plugin
            **kwargs: Plugin initialization parameters
            
        Returns:
            Plugin instance or None if not found
        """
        plugin_class = self.get_plugin(plugin_type, plugin_name)
        
        if not plugin_class:
            logger.warning(f"Plugin not found: {plugin_type}.{plugin_name}")
            return None
        
        try:
            return plugin_class(**kwargs)
        except Exception as e:
            logger.error(f"Error instantiating plugin {plugin_type}.{plugin_name}: {str(e)}")
            return None
    
    def get_transformer(self, name: str, **kwargs) -> Optional[Callable[[Any], Any]]:
        """
        Get a transformer function from a plugin.
        
        Args:
            name: Name of the transformer plugin
            **kwargs: Plugin initialization parameters
            
        Returns:
            Transformer function or None if not found
        """
        plugin = self.instantiate_plugin("transformer", name, **kwargs)
        
        if not plugin or not isinstance(plugin, TransformerPlugin):
            return None
        
        return lambda value, **params: plugin.transform(value, **params)
