#!/usr/bin/env python3
"""
Example: multi-source aggregation with ApiLinker v0.7.1+

Demonstrates joining CRM and billing payloads by key using the library API.
Replace the StaticSourceConnector stubs with real ApiConnector instances.
"""

from typing import Any

from apilinker import ApiLinker
from apilinker.core.connector import ApiConnector


class StaticSourceConnector(ApiConnector):
    """Minimal connector that returns a fixed list for demonstration."""

    def __init__(self, name: str, payload: Any) -> None:
        super().__init__(
            "rest",
            base_url="https://api.example.com",
            endpoints={"items": {"path": "/items", "method": "GET"}},
        )
        self._name = name
        self._payload = payload

    def fetch_data(self, endpoint_name: str, params=None):
        return self._payload


def main() -> None:
    linker = ApiLinker(log_level="INFO")
    linker.register_source(
        "crm",
        StaticSourceConnector(
            "crm",
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
        ),
    )
    linker.register_source(
        "billing",
        StaticSourceConnector(
            "billing",
            [
                {"customer_id": 1, "plan": "pro"},
                {"customer_id": 2, "plan": "basic"},
            ],
        ),
    )

    aggregation_config = {
        "join_type": "inner",
        "merge_strategy": "flat",
        "conflict_resolution": "prefer_last",
        "sources": [
            {
                "name": "crm",
                "join_key": "id",
                "fields": [
                    {"source": "id", "target": "id"},
                    {"source": "name", "target": "name"},
                ],
            },
            {
                "name": "billing",
                "join_key": "customer_id",
                "fields": [{"source": "plan", "target": "plan"}],
            },
        ],
    }

    merged = linker.aggregate_sources(
        source_requests={
            "crm": {"connector": "crm", "endpoint": "items"},
            "billing": {"connector": "billing", "endpoint": "items"},
        },
        aggregation_config=aggregation_config,
        parallel=True,
    )

    for row in merged:
        print(row)


if __name__ == "__main__":
    main()
