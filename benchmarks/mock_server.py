"""
Lightweight mock HTTP server for ApiLinker benchmarks.

Uses Python's built-in http.server to avoid extra deps.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict


class _Handler(BaseHTTPRequestHandler):
    routes: Dict[str, Dict[str, Any]] = {}

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 (http.server API)
        route = self.routes.get(("GET", self.path))
        if not route:
            self._send_json(404, {"error": "not found"})
            return
        self._send_json(200, route.get("response", {}))

    def do_POST(self):  # noqa: N802 (http.server API)
        route = self.routes.get(("POST", self.path))
        if not route:
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        _ = self.rfile.read(length) if length else b""
        self._send_json(201, route.get("response", {"ok": True}))

    def log_message(self, fmt, *args):  # Silence default logging
        return


class MockServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self._server = HTTPServer((host, port), _Handler)
        self._thread: threading.Thread | None = None

    def route(self, method: str, path: str, response: Any) -> None:
        _Handler.routes[(method.upper(), path)] = {"response": response}

    def start(self) -> None:
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        if self._thread:
            self._thread.join(timeout=2)


