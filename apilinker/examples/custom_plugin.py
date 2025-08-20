"""
Example: Creating a custom plugin for ApiLinker.

This example demonstrates how to create and register custom plugins
for ApiLinker, including a transformer plugin, a connector plugin,
and an authentication plugin.

To use these plugins:
1. Save this file to a directory (e.g., ~/.apilinker/plugins/)
2. When initializing ApiLinker, specify the plugin directory:
   linker = ApiLinker(plugin_dir="~/.apilinker/plugins/")

Or register them manually:
   from apilinker.core.plugins import PluginManager
   plugin_manager = PluginManager()
   plugin_manager.register_plugin(SentimentAnalysisTransformer)
"""

import json
import os
from typing import Any, Dict, List, Optional, Union

from apilinker.core.plugins import AuthPlugin, ConnectorPlugin, TransformerPlugin


class SentimentAnalysisTransformer(TransformerPlugin):
    """
    A transformer plugin that analyzes text sentiment.

    This is a simple example that uses a basic approach to sentiment analysis.
    In a real-world scenario, you might use a proper NLP library like NLTK,
    TextBlob, or a cloud API.
    """

    plugin_name = "sentiment_analysis"

    # Simple lists of positive and negative words for demo purposes
    POSITIVE_WORDS = [
        "good",
        "great",
        "excellent",
        "amazing",
        "awesome",
        "fantastic",
        "wonderful",
        "happy",
        "pleased",
        "satisfied",
        "love",
        "like",
    ]

    NEGATIVE_WORDS = [
        "bad",
        "terrible",
        "awful",
        "horrible",
        "poor",
        "disappointing",
        "sad",
        "angry",
        "hate",
        "dislike",
        "broken",
        "error",
        "issue",
        "bug",
    ]

    def transform(self, value: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze sentiment in text.

        Args:
            value: Text to analyze
            **kwargs: Additional parameters

        Returns:
            Dictionary with sentiment analysis results
        """
        if not value or not isinstance(value, str):
            return {"sentiment": "neutral", "score": 0.0}

        # Convert to lowercase for case-insensitive matching
        text = value.lower()

        # Count positive and negative words
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text)

        # Calculate a simple sentiment score from -1 (negative) to +1 (positive)
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total

        # Determine sentiment label
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_words": positive_count,
            "negative_words": negative_count,
        }


class WebhookConnector(ConnectorPlugin):
    """
    A connector plugin for handling webhook data.

    This connector can be used to process incoming webhook data and
    forward it to another system. It simulates storing and retrieving
    webhook data from a local file.
    """

    plugin_name = "webhook"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_file = kwargs.get("storage_file", "webhooks.json")

        # Initialize storage file if it doesn't exist
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "w") as f:
                json.dump([], f)

    def connect(self, **kwargs) -> Any:
        """Create a connection to the webhook storage."""
        return {"storage_file": self.storage_file}

    def fetch(self, connection: Any, endpoint: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch webhook data from storage.

        Args:
            connection: Connection object from connect()
            endpoint: Endpoint name (unused in this connector)
            **kwargs: Additional parameters

        Returns:
            List of webhook payloads
        """
        storage_file = connection["storage_file"]

        try:
            with open(storage_file, "r") as f:
                data = json.load(f)

            # Filter by event type if specified
            event_type = kwargs.get("event_type")
            if event_type:
                data = [item for item in data if item.get("event_type") == event_type]

            return data

        except Exception as e:
            raise Exception(f"Error fetching webhook data: {str(e)}")

    def send(
        self, connection: Any, endpoint: str, data: Any, **kwargs
    ) -> Dict[str, Any]:
        """
        Store webhook data.

        Args:
            connection: Connection object from connect()
            endpoint: Endpoint name (unused in this connector)
            data: Webhook payload to store
            **kwargs: Additional parameters

        Returns:
            Result of the operation
        """
        storage_file = connection["storage_file"]

        try:
            # Read existing data
            with open(storage_file, "r") as f:
                existing_data = json.load(f)

            # Add timestamp if not present
            if isinstance(data, dict) and "timestamp" not in data:
                from datetime import datetime

                data["timestamp"] = datetime.now().isoformat()

            # Add new data
            if isinstance(data, list):
                existing_data.extend(data)
            else:
                existing_data.append(data)

            # Write back to file
            with open(storage_file, "w") as f:
                json.dump(existing_data, f, indent=2)

            return {
                "success": True,
                "stored_count": 1 if isinstance(data, dict) else len(data),
            }

        except Exception as e:
            raise Exception(f"Error storing webhook data: {str(e)}")


class ApiKeyRotationAuth(AuthPlugin):
    """
    An authentication plugin that handles API key rotation.

    This plugin demonstrates how to implement API key rotation for
    enhanced security, where keys are automatically rotated based
    on usage count or time elapsed.
    """

    plugin_name = "api_key_rotation"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.primary_key = kwargs.get("primary_key")
        self.secondary_key = kwargs.get("secondary_key")
        self.max_uses = kwargs.get("max_uses", 1000)
        self.current_uses = 0
        self.active_key = "primary"

    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """
        Perform authentication with key rotation.

        Args:
            **kwargs: Authentication parameters

        Returns:
            Authentication result with credentials
        """
        # Increment usage counter
        self.current_uses += 1

        # Check if we need to rotate keys
        if self.current_uses >= self.max_uses:
            self._rotate_keys()
            self.current_uses = 0

        # Get the current active key
        current_key = (
            self.primary_key if self.active_key == "primary" else self.secondary_key
        )

        # Return authentication details
        return {
            "type": "api_key",
            "header_name": kwargs.get("header_name", "X-API-Key"),
            "key": current_key,
            "uses": self.current_uses,
            "max_uses": self.max_uses,
        }

    def _rotate_keys(self) -> None:
        """Rotate the API keys."""
        if self.active_key == "primary":
            self.active_key = "secondary"
        else:
            self.active_key = "primary"


# Example usage
if __name__ == "__main__":
    from apilinker.core.plugins import PluginManager

    # Initialize plugin manager
    plugin_manager = PluginManager()

    # Register plugins
    plugin_manager.register_plugin(SentimentAnalysisTransformer)
    plugin_manager.register_plugin(WebhookConnector)
    plugin_manager.register_plugin(ApiKeyRotationAuth)

    # List registered plugins
    plugins = plugin_manager.discover_plugins()
    print(f"Discovered {len(plugins)} plugins:")
    for plugin in plugins:
        print(f"- {plugin['type']}.{plugin['name']}")

    # Create and use a transformer plugin
    sentiment_transformer = plugin_manager.instantiate_plugin(
        "transformer", "sentiment_analysis"
    )

    if sentiment_transformer:
        result = sentiment_transformer.transform(
            "I really love this product, it's fantastic and works great!"
        )
        print("\nSentiment Analysis Result:")
        print(json.dumps(result, indent=2))
