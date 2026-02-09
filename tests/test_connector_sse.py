"""
Tests for Server-Sent Events (SSE) support in ApiConnector.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import patch

import httpx
import pytest

from apilinker.connectors.general.sse import SSEConnector
from apilinker.core.connector import ApiConnector
from apilinker.core.error_handling import ApiLinkerError, ErrorCategory


class DummySSEStream:
    """Simple context-managed SSE response stub."""

    def __init__(
        self,
        lines: List[str],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._lines = lines
        self.status_code = status_code
        self.headers = headers or {}

    def __enter__(self) -> "DummySSEStream":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://api.example.com/events")
            response = httpx.Response(self.status_code, request=request, text="failed")
            raise httpx.HTTPStatusError(
                f"{self.status_code} error", request=request, response=response
            )

    def iter_lines(self):
        for line in self._lines:
            yield line


@pytest.fixture
def connector() -> ApiConnector:
    return ApiConnector(
        connector_type="rest",
        base_url="https://api.example.com",
        endpoints={
            "events": {
                "path": "/events",
                "method": "GET",
                "sse": {},
            }
        },
    )


def test_parse_sse_event_with_json_payload(connector: ApiConnector) -> None:
    parsed = connector._parse_sse_event(
        [
            "id: 42",
            "event: update",
            'data: {"value": 7}',
            "retry: 1500",
        ]
    )

    assert parsed is not None
    assert parsed["id"] == "42"
    assert parsed["event"] == "update"
    assert parsed["data"] == {"value": 7}
    assert parsed["retry"] == 1500
    assert parsed["has_data"] is True


def test_stream_sse_emits_data_events_and_ignores_retry_only_blocks(
    connector: ApiConnector,
) -> None:
    lines = [
        "retry: 2500",
        "",
        "id: 1",
        'data: {"value": 1}',
        "",
        "data: plain-text",
        "",
    ]
    with patch.object(connector.client, "stream", return_value=DummySSEStream(lines)):
        events = list(connector.stream_sse("events", reconnect=False))

    assert len(events) == 2
    assert events[0]["id"] == "1"
    assert events[0]["data"] == {"value": 1}
    assert events[1]["data"] == "plain-text"


def test_stream_sse_reconnects_after_transport_error(connector: ApiConnector) -> None:
    stream_side_effect = [
        httpx.ReadError("connection dropped"),
        DummySSEStream(["data: ok", ""]),
    ]

    with patch.object(connector.client, "stream", side_effect=stream_side_effect):
        with patch("apilinker.core.connector.time.sleep") as mock_sleep:
            events = list(
                connector.stream_sse(
                    "events",
                    reconnect=True,
                    reconnect_delay=0.1,
                    max_reconnect_attempts=2,
                    max_events=1,
                )
            )

    assert len(events) == 1
    assert events[0]["data"] == "ok"
    mock_sleep.assert_called_once_with(0.1)


def test_stream_sse_raises_after_max_reconnect_attempts(
    connector: ApiConnector,
) -> None:
    stream_side_effect = [
        httpx.ReadError("first failure"),
        httpx.ReadError("second failure"),
    ]

    with patch.object(connector.client, "stream", side_effect=stream_side_effect):
        with patch("apilinker.core.connector.time.sleep"):
            with pytest.raises(ApiLinkerError) as exc_info:
                list(
                    connector.stream_sse(
                        "events",
                        reconnect=True,
                        reconnect_delay=0.0,
                        max_reconnect_attempts=1,
                    )
                )

    assert exc_info.value.error_category == ErrorCategory.NETWORK


def test_consume_sse_drop_oldest_backpressure(connector: ApiConnector) -> None:
    events = [
        {
            "id": str(i),
            "event": "message",
            "data": {"n": i},
            "retry": None,
            "raw_data": f'{{"n": {i}}}',
        }
        for i in range(5)
    ]

    with patch.object(connector, "stream_sse", return_value=iter(events)):
        result = connector.consume_sse(
            "events",
            chunk_size=3,
            backpressure_buffer_size=2,
            drop_policy="drop_oldest",
        )

    assert result["dropped_events"] == 3
    assert result["processed_events"] == 2
    assert result["chunks_processed"] == 1
    assert [item["data"]["n"] for item in result["results"][0]] == [3, 4]


def test_consume_sse_block_backpressure(connector: ApiConnector) -> None:
    events = [
        {
            "id": str(i),
            "event": "message",
            "data": {"n": i},
            "retry": None,
            "raw_data": f'{{"n": {i}}}',
        }
        for i in range(4)
    ]

    with patch.object(connector, "stream_sse", return_value=iter(events)):
        result = connector.consume_sse(
            "events",
            chunk_size=2,
            backpressure_buffer_size=2,
            drop_policy="block",
            processor=lambda chunk: [item["data"]["n"] for item in chunk],
        )

    assert result["dropped_events"] == 0
    assert result["processed_events"] == 4
    assert result["chunks_processed"] == 2
    assert result["results"] == [[0, 1], [2, 3]]


def test_sse_connector_defaults() -> None:
    connector = SSEConnector(base_url="https://events.example.com")

    assert connector.connector_type == "sse"
    assert connector.default_endpoint == "events"
    assert "events" in connector.endpoints
    assert connector.default_headers["Accept"] == "text/event-stream"


def test_sse_connector_stream_events_delegates() -> None:
    connector = SSEConnector(base_url="https://events.example.com")
    expected = [{"id": "1", "event": "message", "data": "ok"}]

    with patch.object(connector, "stream_sse", return_value=iter(expected)) as mock_fn:
        events = list(connector.stream_events())

    assert events == expected
    mock_fn.assert_called_once_with(endpoint_name="events", params=None)
