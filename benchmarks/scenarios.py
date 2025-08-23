"""
Benchmark scenarios for ApiLinker.

Defines small end-to-end runs against a local mock server to measure:
 - Fetch latency
 - Mapping/transform time
 - Send latency
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict

from apilinker.api_linker import ApiLinker
from apilinker.core.async_connector import AsyncApiConnector
from .mock_server import MockServer


def _setup_linker(base_url: str) -> ApiLinker:
    linker = ApiLinker(
        source_config={
            "type": "rest",
            "base_url": base_url,
            "endpoints": {
                "list_users": {"path": "/users", "method": "GET"}
            },
        },
        target_config={
            "type": "rest",
            "base_url": base_url,
            "endpoints": {
                "create_user": {"path": "/users", "method": "POST"}
            },
        },
        mapping_config={
            "source": "list_users",
            "target": "create_user",
            "fields": [
                {"source": "id", "target": "external_id"},
                {"source": "name", "target": "full_name"},
            ],
        },
    )
    return linker
async def _setup_async_connectors(base_url: str) -> AsyncApiConnector:
    connector = AsyncApiConnector(
        connector_type="rest",
        base_url=base_url,
        endpoints={
            "list_users": {"path": "/users", "method": "GET"},
            "create_user": {"path": "/users", "method": "POST"},
        },
    )
    return connector

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def scenario_async_small_batch() -> None:
    server = MockServer()
    server.route("GET", "/users", {"data": [{"id": i, "name": f"user-{i}"} for i in range(10)]})
    server.route("POST", "/users", {"ok": True})
    server.start()
    try:
        async def run():
            connector = await _setup_async_connectors(f"http://{server.host}:{server.port}")
            try:
                src = await connector.fetch_data("list_users")
                data = src if isinstance(src, list) else src.get("data", [])
                await connector.send_data(
                    "create_user",
                    data,
                    concurrency_limit=_env_int("APILINKER_ASYNC_CONCURRENCY", 32),
                    batch_size=_env_int("APILINKER_ASYNC_BATCH", 10),
                )
            finally:
                await connector.aclose()
        import asyncio as _asyncio
        _asyncio.run(run())
    finally:
        server.stop()

def scenario_async_large_batch() -> None:
    server = MockServer()
    server.route("GET", "/users", {"data": [{"id": i, "name": f"user-{i}"} for i in range(10000)]})
    server.route("POST", "/users", {"ok": True})
    server.start()
    try:
        async def run():
            connector = await _setup_async_connectors(f"http://{server.host}:{server.port}")
            try:
                src = await connector.fetch_data("list_users")
                data = src if isinstance(src, list) else src.get("data", [])
                await connector.send_data(
                    "create_user",
                    data,
                    concurrency_limit=_env_int("APILINKER_ASYNC_CONCURRENCY", 256),
                    batch_size=_env_int("APILINKER_ASYNC_BATCH", 100),
                )
            finally:
                await connector.aclose()
        import asyncio as _asyncio
        _asyncio.run(run())
    finally:
        server.stop()


def scenario_small_batch() -> None:
    server = MockServer()
    server.route("GET", "/users", {"data": [{"id": i, "name": f"user-{i}"} for i in range(10)]})
    server.route("POST", "/users", {"ok": True})
    server.start()
    try:
        linker = _setup_linker(f"http://{server.host}:{server.port}")
        linker.sync("list_users", "create_user")
    finally:
        server.stop()


def scenario_medium_batch() -> None:
    server = MockServer()
    server.route("GET", "/users", {"data": [{"id": i, "name": f"user-{i}"} for i in range(1000)]})
    server.route("POST", "/users", {"ok": True})
    server.start()
    try:
        linker = _setup_linker(f"http://{server.host}:{server.port}")
        linker.sync("list_users", "create_user")
    finally:
        server.stop()


def scenario_large_batch() -> None:
    server = MockServer()
    server.route("GET", "/users", {"data": [{"id": i, "name": f"user-{i}"} for i in range(10000)]})
    server.route("POST", "/users", {"ok": True})
    server.start()
    try:
        linker = _setup_linker(f"http://{server.host}:{server.port}")
        linker.sync("list_users", "create_user")
    finally:
        server.stop()


SCENARIOS: Dict[str, Callable[[], None]] = {
    "small_batch": scenario_small_batch,
    "medium_batch": scenario_medium_batch,
    "large_batch": scenario_large_batch,
    "async_small_batch": scenario_async_small_batch,
    "async_large_batch": scenario_async_large_batch,
}


