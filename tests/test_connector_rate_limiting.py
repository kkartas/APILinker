import pytest
import time
from unittest.mock import MagicMock, patch
from apilinker.core.connector import ApiConnector, EndpointConfig


class TestConnectorRateLimiting:
    @pytest.fixture
    def connector(self):
        endpoints = {
            "limited_endpoint": {
                "path": "/limited",
                "method": "GET",
                "rate_limit": {"strategy": "TOKEN_BUCKET", "rate": 10, "burst": 1},
            },
            "unlimited_endpoint": {"path": "/unlimited", "method": "GET"},
        }
        return ApiConnector("test", "https://api.example.com", endpoints=endpoints)

    def test_rate_limiter_initialization(self, connector):
        assert connector.rate_limit_manager.get_limiter("limited_endpoint") is not None
        assert connector.rate_limit_manager.get_limiter("unlimited_endpoint") is None

    @patch("apilinker.core.connector.httpx.Client.request")
    def test_fetch_data_rate_limiting(self, mock_request, connector):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "ok"}
        mock_request.return_value = mock_response

        # Use a deterministic assertion by observing the internal sleep call
        # instead of wall-clock elapsed time, which is flaky on CI runners.
        with patch("apilinker.core.rate_limiting.time.sleep") as mock_sleep:
            connector.fetch_data("limited_endpoint")
            connector.fetch_data("limited_endpoint")

            assert mock_sleep.call_count >= 1
            waited_for = mock_sleep.call_args_list[-1][0][0]
            assert waited_for > 0

    @patch("apilinker.core.connector.httpx.Client.request")
    def test_update_from_response(self, mock_request, connector):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "ok"}
        # Mock headers
        mock_response.headers = {
            "X-RateLimit-Remaining": "50",
            "X-RateLimit-Reset": str(time.time() + 60),
        }
        mock_request.return_value = mock_response

        # Spy on update_from_headers
        limiter = connector.rate_limit_manager.get_limiter("limited_endpoint")
        with patch.object(
            limiter, "update_from_headers", wraps=limiter.update_from_headers
        ) as mock_update:
            connector.fetch_data("limited_endpoint")
            mock_update.assert_called_once()

    @patch("apilinker.core.connector.httpx.Client.request")
    def test_send_data_rate_limiting(self, mock_request, connector):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1}
        mock_request.return_value = mock_response

        data = [{"id": i} for i in range(3)]

        # Should call acquire 3 times
        limiter = connector.rate_limit_manager.get_limiter("limited_endpoint")
        with patch.object(limiter, "acquire", wraps=limiter.acquire) as mock_acquire:
            connector.send_data("limited_endpoint", data)
            assert mock_acquire.call_count == 3
