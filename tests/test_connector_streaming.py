"""
Tests for generic streaming response handling in ApiConnector.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import patch

import httpx
import pytest

from apilinker.core.connector import ApiConnector
from apilinker.core.error_handling import ApiLinkerError, ErrorCategory


class DummyByteStreamResponse:
    """Context-managed byte stream response stub."""

    def __init__(
        self,
        chunks: List[bytes],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._chunks = chunks
        self.status_code = status_code
        self.headers = headers or {}

    def __enter__(self) -> "DummyByteStreamResponse":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://api.example.com/download")
            response = httpx.Response(self.status_code, request=request, text="failed")
            raise httpx.HTTPStatusError(
                f"{self.status_code} error", request=request, response=response
            )

    def iter_bytes(self, chunk_size: int = 65536):
        for chunk in self._chunks:
            yield chunk


@pytest.fixture
def connector() -> ApiConnector:
    return ApiConnector(
        connector_type="rest",
        base_url="https://api.example.com",
        endpoints={
            "download": {
                "path": "/download",
                "method": "GET",
                "streaming": {},
            }
        },
    )


def test_stream_response_yields_chunks_and_reports_progress(
    connector: ApiConnector,
) -> None:
    progress_events: List[Dict[str, Any]] = []
    response = DummyByteStreamResponse(
        [b"abc", b"defg"], headers={"Content-Length": "7"}
    )

    with patch.object(connector.client, "stream", return_value=response):
        chunks = list(
            connector.stream_response(
                "download",
                chunk_size=3,
                progress_callback=progress_events.append,
                read_timeout=5.0,
            )
        )

    assert chunks == [b"abc", b"defg"]
    assert progress_events[0]["bytes_processed"] == 0
    assert progress_events[-1]["done"] is True
    assert progress_events[-1]["bytes_processed"] == 7
    assert progress_events[-1]["total_bytes"] == 7
    assert progress_events[-1]["percent_complete"] == 100.0


def test_download_stream_resumes_when_server_supports_range(
    connector: ApiConnector, tmp_path
) -> None:
    target_path = tmp_path / "payload.bin"
    target_path.write_bytes(b"01234")
    progress_events: List[Dict[str, Any]] = []
    response = DummyByteStreamResponse(
        [b"56789"],
        status_code=206,
        headers={
            "Content-Length": "5",
            "Content-Range": "bytes 5-9/10",
        },
    )

    with patch.object(connector.client, "stream", return_value=response) as mock_stream:
        result = connector.download_stream(
            "download",
            str(target_path),
            progress_callback=progress_events.append,
        )

    _, kwargs = mock_stream.call_args
    assert kwargs["headers"]["Range"] == "bytes=5-"
    assert target_path.read_bytes() == b"0123456789"
    assert result["resumed"] is True
    assert result["resume_from"] == 5
    assert result["bytes_written"] == 5
    assert progress_events[-1]["bytes_processed"] == 10
    assert progress_events[-1]["done"] is True


def test_download_stream_restarts_when_server_ignores_resume_request(
    connector: ApiConnector, tmp_path
) -> None:
    target_path = tmp_path / "payload.bin"
    target_path.write_bytes(b"stale")
    response = DummyByteStreamResponse(
        [b"fresh"], status_code=200, headers={"Content-Length": "5"}
    )

    with patch.object(connector.client, "stream", return_value=response):
        result = connector.download_stream("download", str(target_path))

    assert target_path.read_bytes() == b"fresh"
    assert result["resumed"] is False
    assert result["resume_from"] == 0
    assert result["bytes_written"] == 5


def test_stream_response_wraps_transport_errors(connector: ApiConnector) -> None:
    with patch.object(
        connector.client, "stream", side_effect=httpx.ReadError("connection dropped")
    ):
        with pytest.raises(ApiLinkerError) as exc_info:
            list(connector.stream_response("download"))

    assert exc_info.value.error_category == ErrorCategory.NETWORK
