"""
Tests for the plugin system.
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest

from apilinker.core.plugins import PluginManager, TransformerPlugin, PluginBase


class TestPluginManager:
    """Test suite for PluginManager."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.plugin_manager = PluginManager()

    def test_register_plugin(self):
        """Test registering a plugin."""
        # Create a mock plugin class
        class TestTransformer(TransformerPlugin):
            plugin_name = "test_transformer"
            
            def transform(self, value, **kwargs):
                return f"transformed_{value}"
        
        # Register the plugin
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Verify plugin was registered
        assert "transformer" in self.plugin_manager.plugins
        assert "test_transformer" in self.plugin_manager.plugins["transformer"]
        assert self.plugin_manager.plugins["transformer"]["test_transformer"] is TestTransformer
    
    def test_get_plugin_types(self):
        """Test getting available plugin types."""
        # Register a test plugin
        class TestTransformer(TransformerPlugin):
            plugin_name = "test"
            
            def transform(self, value, **kwargs):
                return f"transformed_{value}"
                
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Get plugin types
        types = list(self.plugin_manager.plugins.keys())
        
        # Verify transformer is in types
        assert "transformer" in types
    
    def test_get_plugins_by_type(self):
        """Test getting plugins of a specific type."""
        # Register test plugins
        class TestTransformer1(TransformerPlugin):
            plugin_name = "test1"
            
            def transform(self, value, **kwargs):
                return f"transformed1_{value}"
                
        class TestTransformer2(TransformerPlugin):
            plugin_name = "test2"
            
            def transform(self, value, **kwargs):
                return f"transformed2_{value}"
        
        self.plugin_manager.register_plugin(TestTransformer1)
        self.plugin_manager.register_plugin(TestTransformer2)
        
        # Get plugins by type
        plugins = self.plugin_manager.plugins["transformer"]
        
        # Verify plugins are returned
        assert len(plugins) == 2
        assert "test1" in plugins
        assert "test2" in plugins
        
    def test_instantiate_plugin(self):
        """Test instantiating a plugin."""
        # Create a plugin class that tracks instantiation
        class TestTransformer(TransformerPlugin):
            plugin_name = "test"
            
            def __init__(self, **kwargs):
                self.init_params = kwargs
                super().__init__(**kwargs)
                
            def transform(self, value, **kwargs):
                return f"transformed_{value}"
        
        # Register the plugin class
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Instantiate the plugin
        plugin = self.plugin_manager.instantiate_plugin("transformer", "test", param1="value1")
        
        # Verify plugin was instantiated with correct parameters
        assert plugin is not None
        assert isinstance(plugin, TestTransformer)
        assert plugin.init_params.get("param1") == "value1"
    
    def test_get_transformer(self):
        """Test getting a transformer function."""
        # Create a transformer plugin with known behavior
        class TestTransformer(TransformerPlugin):
            plugin_name = "test"
            
            def transform(self, value, **kwargs):
                suffix = kwargs.get('suffix', '')
                return f"transformed_{value}{suffix}"
        
        # Register the plugin class
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Get the transformer function
        transformer = self.plugin_manager.get_transformer("test")
        
        # Test the transformer function
        result = transformer("input", suffix="_extra")
        assert result == "transformed_input_extra"


class TestTransformerPlugin:
    """Test suite for TransformerPlugin base class."""
    
    def test_transform_not_implemented(self):
        """Test that transform raises NotImplementedError."""
        plugin = TransformerPlugin()
        with pytest.raises(NotImplementedError):
            plugin.transform("test")
