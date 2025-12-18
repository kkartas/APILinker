from apilinker.core.plugins import PluginManager


def test_builtin_message_queue_connectors_discoverable():
    pm = PluginManager()
    discovered = pm.discover_plugins()

    connector_names = [p["name"] for p in discovered if p.get("type") == "connector"]

    # These are built-in plugins exposed via apilinker.plugins.builtin
    assert "rabbitmq" in connector_names
    assert "redis_pubsub" in connector_names
    assert "aws_sqs" in connector_names
    assert "kafka" in connector_names

    # Instantiation should work even without dependencies (constructor is dependency-free)
    c = pm.instantiate_plugin("connector", "rabbitmq")
    assert c is not None
