"""
Server-Sent Events (SSE) connector.

Provides a thin convenience wrapper around ``ApiConnector`` SSE capabilities.
"""

from typing import Any, Callable, Dict, Generator, List, Optional

from apilinker.core.connector import ApiConnector


class SSEConnector(ApiConnector):
    """
    Connector specialized for Server-Sent Events streams.

    Example:
        connector = SSEConnector(base_url="https://events.example.com")
        for event in connector.stream_events():
            print(event)
    """

    def __init__(
        self,
        base_url: str,
        endpoint_name: str = "events",
        endpoint_path: str = "/events",
        endpoints: Optional[Dict[str, Dict[str, Any]]] = None,
        default_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        resolved_endpoints = endpoints or {
            endpoint_name: {
                "path": endpoint_path,
                "method": "GET",
                "sse": {},
            }
        }

        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        }
        if default_headers:
            headers.update(default_headers)

        super().__init__(
            connector_type="sse",
            base_url=base_url,
            auth_config=None,
            endpoints=resolved_endpoints,
            default_headers=headers,
            **kwargs,
        )

        if endpoint_name in resolved_endpoints:
            self.default_endpoint = endpoint_name
        else:
            # Fallback to first configured endpoint if custom endpoints are supplied.
            self.default_endpoint = next(iter(resolved_endpoints))

    def stream_events(
        self,
        endpoint_name: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Generator[Dict[str, Any], None, None]:
        """Stream SSE events from the selected endpoint."""
        endpoint = endpoint_name or self.default_endpoint
        return self.stream_sse(endpoint_name=endpoint, params=params, **kwargs)

    def consume_events(
        self,
        endpoint_name: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        processor: Optional[Callable[[List[Dict[str, Any]]], Any]] = None,
        chunk_size: int = 50,
        max_events: Optional[int] = None,
        backpressure_buffer_size: int = 500,
        drop_policy: str = "block",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Consume SSE events in chunks with backpressure handling."""
        endpoint = endpoint_name or self.default_endpoint
        return self.consume_sse(
            endpoint_name=endpoint,
            params=params,
            processor=processor,
            chunk_size=chunk_size,
            max_events=max_events,
            backpressure_buffer_size=backpressure_buffer_size,
            drop_policy=drop_policy,
            **kwargs,
        )
