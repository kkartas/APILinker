"""
API Connector module for handling connections to different types of APIs.
"""

import json
import logging
import time
from collections import deque
from typing import Any, Callable, Deque, Dict, Generator, List, Optional, Tuple, Union

import httpx
from pydantic import BaseModel, Field
from pydantic import ConfigDict

from apilinker.core.auth import AuthConfig
from apilinker.core.error_handling import ApiLinkerError, ErrorCategory
from apilinker.core.validation import (
    validate_payload_against_schema,
    pretty_print_diffs,
    is_validator_available,
)
from apilinker.core.rate_limiting import RateLimitManager
from apilinker.core.monitoring import HealthCheckResult, HealthStatus

logger = logging.getLogger(__name__)


class EndpointConfig(BaseModel):
    """Configuration for an API endpoint."""

    path: str
    method: str = "GET"
    params: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    body_template: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, Any]] = None
    response_path: Optional[str] = None
    # Optional JSON Schemas for validation
    response_schema: Optional[Dict[str, Any]] = None
    request_schema: Optional[Dict[str, Any]] = None
    rate_limit: Optional[Dict[str, Any]] = None
    sse: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ApiConnector:
    """
    API Connector for interacting with REST APIs.

    This class handles the connection to APIs, making requests, and
    processing responses.

    Args:
        connector_type: Type of connector (rest, graphql, etc.)
        base_url: Base URL for the API
        auth_config: Authentication configuration
        endpoints: Dictionary of endpoint configurations
        timeout: Request timeout in seconds
        retry_count: Number of retries on failure
        retry_delay: Delay between retries in seconds
    """

    def __init__(
        self,
        connector_type: str,
        base_url: str,
        auth_config: Optional[AuthConfig] = None,
        endpoints: Optional[Dict[str, Dict[str, Any]]] = None,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: int = 1,
        default_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        self.connector_type = connector_type
        self.base_url = base_url
        self.auth_config = auth_config
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay

        # Default headers (may be provided via explicit parameter or legacy 'headers' kwarg)
        if default_headers is None and "headers" in kwargs:
            try:
                default_headers = dict(kwargs.pop("headers"))
            except Exception:
                default_headers = None
        self.default_headers: Dict[str, str] = default_headers or {}
        # Provide a backwards-compatible attribute name used by some connectors
        self.headers: Dict[str, str] = self.default_headers

        # Parse and store endpoint configurations
        self.endpoints: Dict[str, EndpointConfig] = {}
        if endpoints:
            for name, config in endpoints.items():
                self.endpoints[name] = EndpointConfig(**config)

        # Store additional settings
        self.settings: Dict[str, Any] = kwargs

        # Create HTTP client with default settings
        self.client = self._create_client()

        # Initialize Rate Limit Manager
        self.rate_limit_manager = RateLimitManager()

        # Configure rate limiters for endpoints
        for name, config in self.endpoints.items():
            if config.rate_limit:
                self.rate_limit_manager.create_limiter(name, config.rate_limit)

        logger.debug(f"Initialized {connector_type} connector for {base_url}")

    def _create_client(self) -> httpx.Client:
        """Create an HTTP client with appropriate settings."""
        # Initialize with default parameters
        auth = None
        if (
            self.auth_config
            and self.auth_config.type == "basic"
            and hasattr(self.auth_config, "username")
            and hasattr(self.auth_config, "password")
        ):
            auth = httpx.BasicAuth(
                username=getattr(self.auth_config, "username", ""),
                password=getattr(self.auth_config, "password", ""),
            )

        # Create client with properly structured parameters
        return httpx.Client(base_url=self.base_url, timeout=self.timeout, auth=auth)

    def _prepare_request(
        self, endpoint_name: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare a request for the given endpoint.

        Args:
            endpoint_name: Name of the endpoint to use
            params: Additional parameters to include in the request

        Returns:
            Dict containing request details (url, method, headers, params, json)
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]

        # Combine endpoint path with base URL
        url = endpoint.path

        # Combine params from endpoint config and provided params
        request_params = endpoint.params.copy()
        if params:
            request_params.update(params)

        # Prepare headers (merge default headers and endpoint-specific headers)
        headers = {**(self.default_headers or {}), **endpoint.headers}

        # Add auth headers if needed
        if self.auth_config:
            if (
                self.auth_config.type == "api_key"
                and hasattr(self.auth_config, "in_header")
                and getattr(self.auth_config, "in_header", False)
            ):
                header_name = getattr(self.auth_config, "header_name", "X-API-Key")
                key = getattr(self.auth_config, "key", "")
                headers[header_name] = key
            elif self.auth_config.type == "bearer" and hasattr(
                self.auth_config, "token"
            ):
                headers["Authorization"] = (
                    f"Bearer {getattr(self.auth_config, 'token', '')}"
                )

        # Prepare request object
        request = {
            "url": url,
            "method": endpoint.method,
            "headers": headers,
            "params": request_params,
        }

        # Add body if endpoint has a body template
        if endpoint.body_template:
            request["json"] = endpoint.body_template

        return request

    def _process_response(
        self, response: httpx.Response, endpoint_name: str
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process the API response.

        Args:
            response: The HTTP response
            endpoint_name: Name of the endpoint

        Returns:
            Parsed response data
        """
        # Update rate limiter from response headers
        self.rate_limit_manager.update_from_response(endpoint_name, response)

        # Raise for HTTP errors
        response.raise_for_status()

        # Parse JSON response
        data: Any = response.json()

        # Extract data from response path if configured
        endpoint = self.endpoints[endpoint_name]
        if endpoint.response_path and isinstance(data, dict):
            path_parts = endpoint.response_path.split(".")
            current_data: Any = data
            for part in path_parts:
                if isinstance(current_data, dict) and part in current_data:
                    current_data = current_data[part]
                else:
                    logger.warning(
                        f"Response path '{endpoint.response_path}' not found in response"
                    )
                    break
            # Only update data if we successfully navigated through the path
            if current_data is not data:
                data = current_data

        # Validate against response schema if provided
        endpoint = self.endpoints[endpoint_name]
        if endpoint.response_schema and is_validator_available():
            valid, diffs = validate_payload_against_schema(
                data, endpoint.response_schema
            )
            if not valid:
                logger.warning(
                    "Response schema validation failed for %s\n%s",
                    endpoint_name,
                    pretty_print_diffs(diffs),
                )
                # Record as a rate-limit or validation event via logger context (provenance layer may hook logs)

        # Ensure we return a valid type
        if isinstance(data, (dict, list)):
            return data
        else:
            # If response isn't a dict or list, wrap it in a dict
            return {"value": data}

    def _handle_pagination(
        self,
        initial_data: Union[Dict[str, Any], List[Dict[str, Any]]],
        endpoint_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Handle paginated responses if pagination is configured.

        Args:
            initial_data: Data from the first request
            endpoint_name: Name of the endpoint
            params: Request parameters

        Returns:
            Combined data from all pages
        """
        endpoint = self.endpoints[endpoint_name]

        # If no pagination config or initial data is not a dict, return as is
        if not endpoint.pagination or not isinstance(initial_data, dict):
            if isinstance(initial_data, list):
                return initial_data
            # Convert non-list data to a single-item list
            return (
                [initial_data]
                if isinstance(initial_data, dict)
                else [{"value": initial_data}]
            )

        # Extract the pagination configuration
        pagination = endpoint.pagination
        data_path = pagination.get("data_path", "")
        next_page_path = pagination.get("next_page_path", "")
        page_param = pagination.get("page_param", "page")

        # Extract the items from the first response
        if data_path:
            path_parts = data_path.split(".")
            items: Any = initial_data
            for part in path_parts:
                if isinstance(items, dict) and part in items:
                    items = items[part]
                else:
                    logger.warning(f"Data path '{data_path}' not found in response")
                    return [initial_data]
        else:
            # If no data path is specified, the entire response is the data
            items = initial_data

        # Normalize items to a list of dicts
        if not isinstance(items, list):
            items_list: List[Dict[str, Any]] = (
                [items] if isinstance(items, dict) else [{"value": items}]
            )
        else:
            items_list = []
            for elem in items:
                if isinstance(elem, dict):
                    items_list.append(elem)
                else:
                    items_list.append({"value": elem})

        # Extract next page token/URL if available
        next_page: Optional[Union[str, int]] = None
        if next_page_path:
            path_parts = next_page_path.split(".")
            temp_next_page: Any = initial_data
            for part in path_parts:
                if isinstance(temp_next_page, dict) and part in temp_next_page:
                    temp_next_page = temp_next_page[part]
                else:
                    temp_next_page = None
                    break
            # Only assign if it's a valid type for pagination
            if isinstance(temp_next_page, (str, int)):
                next_page = temp_next_page

        # Return the items if there's no next page
        if not next_page:
            return items_list

        # Fetch all pages
        all_items: List[Dict[str, Any]] = list(items_list)
        page = 2

        while next_page:
            # Update params for next page
            next_params: Dict[str, Any] = params.copy() if params else {}

            # Use either page number or next page token (refined to str|int in this loop)
            next_params[page_param] = next_page

            # Make the next request
            try:
                request = self._prepare_request(endpoint_name, next_params)
                response = self.client.request(
                    request["method"],
                    request["url"],
                    headers=request["headers"],
                    params=request["params"],
                    json=request.get("json"),
                )
                response.raise_for_status()
                page_data = response.json()

                # Extract items from this page
                page_items: Any
                if data_path:
                    path_parts = data_path.split(".")
                    page_items = page_data
                    for part in path_parts:
                        if isinstance(page_items, dict) and part in page_items:
                            page_items = page_items[part]
                        else:
                            page_items = []
                            break
                else:
                    page_items = page_data

                # Add items to the result, normalizing to list[dict]
                if isinstance(page_items, list):
                    for elem in page_items:
                        if isinstance(elem, dict):
                            all_items.append(elem)
                        else:
                            all_items.append({"value": elem})
                else:
                    all_items.append(
                        page_items
                        if isinstance(page_items, dict)
                        else {"value": page_items}
                    )

                # Extract next page token
                if next_page_path:
                    path_parts = next_page_path.split(".")
                    temp_next_page = page_data
                    for part in path_parts:
                        if isinstance(temp_next_page, dict) and part in temp_next_page:
                            temp_next_page = temp_next_page[part]
                        else:
                            temp_next_page = None
                            break
                    # Only assign if it's a valid type for pagination
                    if isinstance(temp_next_page, (str, int)):
                        next_page = temp_next_page
                    else:
                        next_page = None
                else:
                    # If no next page path, just increment the page number
                    page += 1
                    next_page = (
                        page if page <= pagination.get("max_pages", 10) else None
                    )

            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                break

        return all_items

    def _categorize_error(self, exc: Exception) -> Tuple[ErrorCategory, int]:
        """
        Categorize an exception to determine its error category and status code.

        Args:
            exc: The exception to categorize

        Returns:
            Tuple of (ErrorCategory, status_code)
        """
        # Default values
        category = ErrorCategory.UNKNOWN
        status_code = None

        # Check for HTTP-specific errors
        if isinstance(exc, httpx.TimeoutException):
            category = ErrorCategory.TIMEOUT
            status_code = 0  # Custom code for timeout
        elif isinstance(exc, httpx.TransportError) or isinstance(
            exc, httpx.RequestError
        ):
            category = ErrorCategory.NETWORK
            status_code = 0  # Custom code for network/transport errors
        elif isinstance(exc, httpx.HTTPStatusError):
            status_code = exc.response.status_code

            # Categorize based on HTTP status code
            if status_code == 401 or status_code == 403:
                category = ErrorCategory.AUTHENTICATION
            elif status_code == 422 or status_code == 400:
                category = ErrorCategory.VALIDATION
            elif status_code == 429:
                category = ErrorCategory.RATE_LIMIT
            elif status_code >= 500:
                category = ErrorCategory.SERVER
            elif status_code >= 400:
                category = ErrorCategory.CLIENT

        return category, status_code

    def _decode_sse_data(self, raw_data: str, decode_json: bool = True) -> Any:
        """
        Decode an SSE data field.

        Args:
            raw_data: Raw SSE data payload after line-join
            decode_json: Whether to attempt JSON decoding

        Returns:
            Decoded object or raw string payload
        """
        if not decode_json:
            return raw_data

        if raw_data.strip() == "":
            return raw_data

        try:
            return json.loads(raw_data)
        except Exception:
            return raw_data

    def _parse_sse_event(
        self, raw_lines: List[str], decode_json: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a single SSE event block (lines between blank separators).

        Args:
            raw_lines: Raw lines from the SSE stream
            decode_json: Whether to decode JSON payloads automatically

        Returns:
            Parsed event dictionary, or None if event is ignorable.
            Returned event includes a transient ``has_data`` flag used internally.
        """
        if not raw_lines:
            return None

        event_id: Optional[str] = None
        event_name = "message"
        data_lines: List[str] = []
        retry_ms: Optional[int] = None

        for line in raw_lines:
            if line.startswith(":"):
                # SSE comment/keepalive line
                continue

            if ":" in line:
                field, value = line.split(":", 1)
                if value.startswith(" "):
                    value = value[1:]
            else:
                field, value = line, ""

            if field == "event":
                event_name = value or "message"
            elif field == "data":
                data_lines.append(value)
            elif field == "id":
                # Ignore invalid ids per SSE spec guidance
                if "\x00" not in value:
                    event_id = value
            elif field == "retry":
                try:
                    parsed_retry = int(value)
                    if parsed_retry >= 0:
                        retry_ms = parsed_retry
                except (TypeError, ValueError):
                    logger.debug("Ignoring invalid SSE retry value: %s", value)

        has_data = len(data_lines) > 0
        if not has_data and retry_ms is None and event_id is None:
            return None

        raw_data = "\n".join(data_lines)
        return {
            "id": event_id,
            "event": event_name,
            "data": self._decode_sse_data(raw_data, decode_json) if has_data else None,
            "retry": retry_ms,
            "raw_data": raw_data,
            "has_data": has_data,
        }

    def _build_sse_request(
        self,
        endpoint_name: str,
        params: Optional[Dict[str, Any]] = None,
        last_event_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build a request dictionary for an SSE endpoint.

        Adds SSE-friendly headers while preserving endpoint/default headers.
        """
        request = self._prepare_request(endpoint_name, params)
        headers = dict(request.get("headers", {}))
        headers.setdefault("Accept", "text/event-stream")
        headers.setdefault("Cache-Control", "no-cache")
        if last_event_id:
            headers["Last-Event-ID"] = last_event_id
        request["headers"] = headers
        return request

    def _raise_sse_error(
        self, exc: Exception, endpoint_name: str, request: Dict[str, Any]
    ) -> None:
        """Raise an ``ApiLinkerError`` for SSE failures with rich context."""
        error_category, status_code = self._categorize_error(exc)
        response_body = None
        if hasattr(exc, "response"):
            try:
                response_body = exc.response.text[:1000]
            except Exception:
                response_body = "<Unable to read response body>"

        raise ApiLinkerError(
            message=f"Failed to stream SSE from {endpoint_name}: {str(exc)}",
            error_category=error_category,
            status_code=status_code,
            response_body=response_body,
            request_url=str(request.get("url")),
            request_method=request.get("method", "GET"),
            additional_context={"endpoint": endpoint_name},
        )

    def stream_sse(
        self,
        endpoint_name: str,
        params: Optional[Dict[str, Any]] = None,
        max_events: Optional[int] = None,
        reconnect: bool = True,
        reconnect_delay: float = 1.0,
        max_reconnect_attempts: Optional[int] = None,
        read_timeout: Optional[float] = None,
        decode_json: bool = True,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream events from an SSE endpoint.

        Supports automatic reconnection, Last-Event-ID resume, and optional
        JSON decoding of event payloads.

        Args:
            endpoint_name: Endpoint key configured in ``self.endpoints``.
            params: Query parameters.
            max_events: Stop after this many dispatched events.
            reconnect: Whether to reconnect on disconnect/error.
            reconnect_delay: Base reconnect delay in seconds.
            max_reconnect_attempts: Maximum reconnect attempts (None = unlimited).
            read_timeout: Per-stream read timeout. Defaults to connector timeout.
            decode_json: Whether to decode JSON payloads automatically.

        Yields:
            Parsed SSE events with keys: ``id``, ``event``, ``data``, ``retry``, ``raw_data``.
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]
        sse_config = endpoint.sse or {}

        if max_events is None and sse_config.get("max_events") is not None:
            max_events = int(sse_config["max_events"])

        reconnect = bool(sse_config.get("reconnect", reconnect))
        reconnect_delay = float(sse_config.get("reconnect_delay", reconnect_delay))

        if (
            max_reconnect_attempts is None
            and sse_config.get("max_reconnect_attempts") is not None
        ):
            max_reconnect_attempts = int(sse_config["max_reconnect_attempts"])

        if read_timeout is None:
            read_timeout = sse_config.get("read_timeout")
        if read_timeout is None:
            read_timeout = self.timeout

        decode_json = bool(sse_config.get("decode_json", decode_json))

        reconnect_attempts = 0
        received_events = 0
        last_event_id: Optional[str] = None
        effective_reconnect_delay = max(0.0, reconnect_delay)

        while True:
            request = self._build_sse_request(endpoint_name, params, last_event_id)
            try:
                # Apply endpoint-level rate limiting before opening/renewing stream
                self.rate_limit_manager.acquire(endpoint_name)

                with self.client.stream(
                    request["method"],
                    request["url"],
                    headers=request["headers"],
                    params=request["params"],
                    json=request.get("json"),
                    timeout=read_timeout,
                ) as response:
                    self.rate_limit_manager.update_from_response(
                        endpoint_name, response
                    )
                    response.raise_for_status()
                    logger.info(
                        "Connected to SSE endpoint: %s (%s %s)",
                        endpoint_name,
                        request["method"],
                        request["url"],
                    )

                    pending_lines: List[str] = []

                    def _dispatch_event(
                        event: Dict[str, Any],
                    ) -> Optional[Dict[str, Any]]:
                        nonlocal effective_reconnect_delay, last_event_id, received_events

                        retry_hint = event.get("retry")
                        if isinstance(retry_hint, int):
                            effective_reconnect_delay = max(
                                0.0, float(retry_hint) / 1000.0
                            )

                        event_id = event.get("id")
                        if event_id:
                            last_event_id = str(event_id)

                        if not event.get("has_data"):
                            # Retry/id-only control blocks are not dispatched
                            return None

                        event.pop("has_data", None)
                        received_events += 1
                        return event

                    for raw_line in response.iter_lines():
                        if raw_line is None:
                            continue

                        line = raw_line.rstrip("\r")

                        if line == "":
                            parsed = self._parse_sse_event(
                                pending_lines, decode_json=decode_json
                            )
                            pending_lines = []

                            if parsed is None:
                                continue

                            event = _dispatch_event(parsed)
                            if event is None:
                                continue

                            yield event
                            if max_events is not None and received_events >= max_events:
                                return
                        else:
                            pending_lines.append(line)

                    # Flush trailing buffered event block on connection close
                    if pending_lines:
                        parsed = self._parse_sse_event(
                            pending_lines, decode_json=decode_json
                        )
                        if parsed is not None:
                            event = _dispatch_event(parsed)
                            if event is not None:
                                yield event
                                if (
                                    max_events is not None
                                    and received_events >= max_events
                                ):
                                    return

            except Exception as exc:
                if not reconnect:
                    self._raise_sse_error(exc, endpoint_name, request)

                reconnect_attempts += 1
                if (
                    max_reconnect_attempts is not None
                    and reconnect_attempts > max_reconnect_attempts
                ):
                    self._raise_sse_error(exc, endpoint_name, request)

                logger.warning(
                    "SSE stream error on endpoint '%s': %s. Reconnecting in %.2fs (attempt %d)",
                    endpoint_name,
                    str(exc),
                    effective_reconnect_delay,
                    reconnect_attempts,
                )
                time.sleep(effective_reconnect_delay)
                continue

            # Reconnect when stream closes naturally, unless disabled.
            if not reconnect:
                return

            reconnect_attempts += 1
            if (
                max_reconnect_attempts is not None
                and reconnect_attempts > max_reconnect_attempts
            ):
                return

            logger.info(
                "SSE stream closed for endpoint '%s'. Reconnecting in %.2fs (attempt %d)",
                endpoint_name,
                effective_reconnect_delay,
                reconnect_attempts,
            )
            time.sleep(effective_reconnect_delay)

    def consume_sse(
        self,
        endpoint_name: str,
        params: Optional[Dict[str, Any]] = None,
        processor: Optional[Callable[[List[Dict[str, Any]]], Any]] = None,
        chunk_size: int = 50,
        max_events: Optional[int] = None,
        backpressure_buffer_size: int = 500,
        drop_policy: str = "block",
        **stream_kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Consume SSE events in chunks with bounded in-memory buffering.

        This method adds chunked processing and explicit backpressure handling:
        - ``drop_policy='block'``: flushes buffer chunks before accepting more data.
        - ``drop_policy='drop_oldest'``: drops oldest buffered events when full.

        Args:
            endpoint_name: Endpoint key configured in ``self.endpoints``.
            params: Query parameters.
            processor: Optional callback invoked with each chunk.
            chunk_size: Number of events per processing chunk.
            max_events: Maximum number of events to consume.
            backpressure_buffer_size: Max in-memory event buffer.
            drop_policy: ``block`` or ``drop_oldest``.
            **stream_kwargs: Extra kwargs forwarded to ``stream_sse``.

        Returns:
            Summary dictionary with processing metrics and chunk results.
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]
        sse_config = endpoint.sse or {}

        if max_events is None and sse_config.get("max_events") is not None:
            max_events = int(sse_config["max_events"])

        chunk_size = int(sse_config.get("chunk_size", chunk_size))
        backpressure_buffer_size = int(
            sse_config.get("backpressure_buffer_size", backpressure_buffer_size)
        )
        drop_policy = str(sse_config.get("drop_policy", drop_policy)).lower()

        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if backpressure_buffer_size <= 0:
            raise ValueError("backpressure_buffer_size must be > 0")
        if drop_policy not in {"block", "drop_oldest"}:
            raise ValueError("drop_policy must be either 'block' or 'drop_oldest'")

        buffer: Deque[Dict[str, Any]] = deque(maxlen=backpressure_buffer_size)
        dropped_events = 0
        processed_events = 0
        chunks_processed = 0
        chunk_results: List[Any] = []

        def _flush(force: bool = False) -> bool:
            nonlocal processed_events, chunks_processed
            flushed = False

            while buffer and (force or len(buffer) >= chunk_size):
                current_chunk_size = (
                    chunk_size if len(buffer) >= chunk_size else len(buffer)
                )
                chunk = [buffer.popleft() for _ in range(current_chunk_size)]
                chunks_processed += 1
                processed_events += len(chunk)
                flushed = True

                if processor:
                    chunk_results.append(processor(chunk))
                else:
                    chunk_results.append(chunk)

                # In non-force mode we flush at most one chunk each step.
                if not force:
                    break

            return flushed

        for event in self.stream_sse(
            endpoint_name=endpoint_name,
            params=params,
            max_events=max_events,
            **stream_kwargs,
        ):
            while len(buffer) >= backpressure_buffer_size:
                if drop_policy == "drop_oldest":
                    buffer.popleft()
                    dropped_events += 1
                    break

                # Block strategy: process buffered data before accepting more.
                if not _flush(force=False):
                    _flush(force=True)
                    break

            buffer.append(event)
            _flush(force=False)

        # Process any trailing events.
        _flush(force=True)

        return {
            "success": True,
            "processed_events": processed_events,
            "chunks_processed": chunks_processed,
            "dropped_events": dropped_events,
            "chunk_size": chunk_size,
            "buffer_max_size": backpressure_buffer_size,
            "results": chunk_results,
        }

    def fetch_data(
        self, endpoint_name: str, params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch data from the specified endpoint.

        Args:
            endpoint_name: Name of the endpoint to use
            params: Additional parameters for the request

        Returns:
            The parsed response data

        Raises:
            ApiLinkerError: On API request failure with enhanced error context
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]
        logger.info(
            f"Fetching data from endpoint: {endpoint_name} ({endpoint.method} {endpoint.path})"
        )

        # Prepare the request
        request = self._prepare_request(endpoint_name, params)

        # Make the request with retries (note: main retries are now handled by the error recovery manager)
        last_exception = None
        for attempt in range(1, self.retry_count + 1):
            try:
                # Apply rate limiting
                self.rate_limit_manager.acquire(endpoint_name)

                response = self.client.request(
                    request["method"],
                    request["url"],
                    headers=request["headers"],
                    params=request["params"],
                    json=request.get("json"),
                )
                response.raise_for_status()

                # Process the response
                result = self._process_response(response, endpoint_name)

                # Handle pagination if configured
                if endpoint.pagination:
                    result = self._handle_pagination(result, endpoint_name, params)

                logger.info(f"Data fetched successfully from {endpoint_name}")
                return result

            except Exception as e:
                last_exception = e
                error_category, status_code = self._categorize_error(e)

                # Log the error at an appropriate level
                if attempt < self.retry_count:
                    wait_time = self.retry_delay * attempt
                    logger.warning(
                        f"Error fetching data (attempt {attempt}/{self.retry_count}): {str(e)}"
                    )
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts failed: {str(e)}")

        # If we get here, all retry attempts failed
        if last_exception:
            error_category, status_code = self._categorize_error(last_exception)

            # Extract response data if available
            response_body = None
            if hasattr(last_exception, "response"):
                try:
                    response_body = last_exception.response.text[:1000]  # Limit size
                except:
                    response_body = "<Unable to read response body>"

            # Create an ApiLinkerError with enhanced context
            raise ApiLinkerError(
                message=f"Failed to fetch data from {endpoint_name}: {str(last_exception)}",
                error_category=error_category,
                status_code=status_code,
                response_body=response_body,
                request_url=str(request["url"]),
                request_method=request["method"],
                additional_context={"endpoint": endpoint_name, "params": params},
            )

        # Should not reach here
        raise ApiLinkerError(
            message=f"Unexpected state fetching data from {endpoint_name}",
            error_category=ErrorCategory.UNKNOWN,
            status_code=0,
        )

    def send_data(
        self, endpoint_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Send data to the specified endpoint.

        Args:
            endpoint_name: Name of the endpoint to use
            data: Data to send

        Returns:
            The parsed response

        Raises:
            ApiLinkerError: On API request failure with enhanced error context
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]
        logger.info(
            f"Sending data to endpoint: {endpoint_name} ({endpoint.method} {endpoint.path})"
        )

        # Prepare the request
        request = self._prepare_request(endpoint_name)

        # Validate single item(s) against request schema if provided
        endpoint = self.endpoints[endpoint_name]
        if endpoint.request_schema and is_validator_available():

            def _validate_item(item: Any) -> None:
                valid, diffs = validate_payload_against_schema(
                    item, endpoint.request_schema
                )
                if not valid:
                    logger.error(
                        "Request schema validation failed for %s\n%s",
                        endpoint_name,
                        pretty_print_diffs(diffs),
                    )
                    raise ApiLinkerError(
                        message="Request failed schema validation",
                        error_category=ErrorCategory.VALIDATION,
                        status_code=0,
                        additional_context={"endpoint": endpoint_name, "diffs": diffs},
                    )

            if isinstance(data, list):
                for item in data:
                    _validate_item(item)
            else:
                _validate_item(data)

        # If data is a list, send each item individually
        if isinstance(data, list):
            results = []
            successful = 0
            failed = 0
            failures = []

            for item_index, item in enumerate(data):
                try:
                    # Apply rate limiting
                    self.rate_limit_manager.acquire(endpoint_name)

                    response = self.client.request(
                        request["method"],
                        request["url"],
                        headers=request["headers"],
                        params=request["params"],
                        json=item,
                    )
                    response.raise_for_status()
                    result = response.json() if response.content else {}
                    results.append(result)
                    successful += 1

                except Exception as e:
                    error_category, status_code = self._categorize_error(e)

                    # Extract response data if available
                    response_body = None
                    if hasattr(e, "response"):
                        try:
                            response_body = e.response.text[:1000]  # Limit size
                        except:
                            response_body = "<Unable to read response body>"

                    error = ApiLinkerError(
                        message=f"Failed to send data item {item_index} to {endpoint_name}: {str(e)}",
                        error_category=error_category,
                        status_code=status_code,
                        response_body=response_body,
                        request_url=str(request["url"]),
                        request_method=request["method"],
                        additional_context={
                            "endpoint": endpoint_name,
                            "item_index": item_index,
                        },
                    )
                    failures.append(error.to_dict())
                    logger.error(f"Error sending data item {item_index}: {error}")
                    failed += 1

            logger.info(f"Sent {successful} items successfully, {failed} failed")
            return {
                "success": successful > 0 and failed == 0,
                "sent_count": successful,
                "failed_count": failed,
                "results": results,
                "failures": failures,
            }

        # If data is a single item, send it
        else:
            # Make the request with retries (note: main retries now handled by error recovery manager)
            last_exception = None

            for attempt in range(1, self.retry_count + 1):
                try:
                    # Apply rate limiting
                    self.rate_limit_manager.acquire(endpoint_name)

                    response = self.client.request(
                        request["method"],
                        request["url"],
                        headers=request["headers"],
                        params=request["params"],
                        json=data,
                    )
                    response.raise_for_status()
                    result = response.json() if response.content else {}

                    logger.info(f"Data sent successfully to {endpoint_name}")
                    return {
                        "success": True,
                        "result": result,
                    }

                except Exception as e:
                    last_exception = e

                    # Log the error at an appropriate level
                    if attempt < self.retry_count:
                        wait_time = self.retry_delay * attempt
                        logger.warning(
                            f"Error sending data (attempt {attempt}/{self.retry_count}): {str(e)}"
                        )
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All retry attempts failed: {str(e)}")

            # If we get here, all retry attempts failed
            if last_exception:
                error_category, status_code = self._categorize_error(last_exception)

                # Extract response data if available
                response_body = None
                if hasattr(last_exception, "response"):
                    try:
                        response_body = last_exception.response.text[
                            :1000
                        ]  # Limit size
                    except:
                        response_body = "<Unable to read response body>"

                # Create an ApiLinkerError with enhanced context
                raise ApiLinkerError(
                    message=f"Failed to send data to {endpoint_name}: {str(last_exception)}",
                    error_category=error_category,
                    status_code=status_code,
                    response_body=response_body,
                    request_url=str(request["url"]),
                    request_method=request["method"],
                    additional_context={"endpoint": endpoint_name},
                )

            # This should not be reached
            return {"success": False, "error": "Unknown error"}

    def check_health(self) -> HealthCheckResult:
        """
        Check the health of the API connection.

        Returns:
            HealthCheckResult indicating the status.
        """
        start_time = time.time()
        try:
            # Try to hit the base URL or a specific health endpoint if we had one configured
            # For now, just check if we can connect to the base URL
            response = self.client.get("/", timeout=5.0)

            latency = (time.time() - start_time) * 1000

            status = HealthStatus.HEALTHY
            message = f"Connected to {self.base_url}"

            # If we get a 5xx error, the server is definitely having issues
            if response.status_code >= 500:
                status = HealthStatus.UNHEALTHY
                message = f"Server returned {response.status_code}"

            return HealthCheckResult(
                status=status,
                component=f"connector:{self.base_url}",
                message=message,
                latency_ms=latency,
                details={"status_code": response.status_code},
            )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                component=f"connector:{self.base_url}",
                message=str(e),
                latency_ms=latency,
            )
