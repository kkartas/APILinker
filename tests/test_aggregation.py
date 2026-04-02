"""
Tests for multi-source aggregation support.
"""

from typing import Any

import pytest

from apilinker.api_linker import ApiLinker
from apilinker.core.aggregation import MultiSourceAggregator
from apilinker.core.connector import ApiConnector


class StaticSourceConnector(ApiConnector):
    """Connector stub that returns a static payload for a single endpoint."""

    def __init__(self, payload: Any) -> None:
        super().__init__(
            "rest",
            base_url="https://api.example.com",
            endpoints={"items": {"path": "/items", "method": "GET"}},
        )
        self.payload = payload

    def fetch_data(self, endpoint_name: str, params=None):
        return self.payload


def test_multi_source_aggregator_inner_join_flat_prefer_last() -> None:
    aggregator = MultiSourceAggregator()
    source_data = {
        "users": [
            {"id": 1, "name": "Alice", "status": "active"},
            {"id": 2, "name": "Bob", "status": "inactive"},
        ],
        "billing": [
            {"customer_id": 1, "plan": "pro", "status": "paid"},
            {"customer_id": 3, "plan": "basic", "status": "trial"},
        ],
    }
    config = {
        "sources": [
            {
                "name": "users",
                "join_key": "id",
                "fields": [
                    {"source": "id", "target": "id"},
                    {"source": "name", "target": "name"},
                    {"source": "status", "target": "status"},
                ],
            },
            {
                "name": "billing",
                "join_key": "customer_id",
                "fields": [
                    {"source": "plan", "target": "plan"},
                    {"source": "status", "target": "status"},
                ],
            },
        ],
        "join_type": "inner",
        "merge_strategy": "flat",
        "conflict_resolution": "prefer_last",
    }

    result = aggregator.aggregate(source_data, config)

    assert result == [{"id": 1, "name": "Alice", "status": "paid", "plan": "pro"}]


def test_multi_source_aggregator_outer_join_namespace_merge() -> None:
    aggregator = MultiSourceAggregator()
    source_data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ],
        "billing": [
            {"customer_id": 1, "plan": "pro"},
            {"customer_id": 3, "plan": "basic"},
        ],
    }
    config = {
        "sources": [
            {
                "name": "users",
                "join_key": "id",
                "fields": [
                    {"source": "id", "target": "id"},
                    {"source": "name", "target": "name"},
                ],
            },
            {
                "name": "billing",
                "join_key": "customer_id",
                "fields": [
                    {"source": "customer_id", "target": "customer_id"},
                    {"source": "plan", "target": "plan"},
                ],
            },
        ],
        "join_type": "outer",
        "merge_strategy": "namespace",
    }

    result = aggregator.aggregate(source_data, config)

    assert len(result) == 3
    assert result[0]["users"]["id"] == 1
    assert result[0]["billing"]["plan"] == "pro"
    assert result[1]["users"]["id"] == 2
    assert result[1]["billing"] is None
    assert result[2]["users"] is None
    assert result[2]["billing"]["customer_id"] == 3


def test_multi_source_aggregator_raises_on_conflicting_flat_merge() -> None:
    aggregator = MultiSourceAggregator()
    source_data = {
        "a": [{"id": 1, "status": "active"}],
        "b": [{"id": 1, "status": "inactive"}],
    }
    config = {
        "sources": [
            {
                "name": "a",
                "join_key": "id",
                "fields": [
                    {"source": "id", "target": "id"},
                    {"source": "status", "target": "status"},
                ],
            },
            {
                "name": "b",
                "join_key": "id",
                "fields": [
                    {"source": "status", "target": "status"},
                ],
            },
        ],
        "join_type": "inner",
        "merge_strategy": "flat",
        "conflict_resolution": "error",
    }

    with pytest.raises(ValueError, match="Conflict detected for field 'status'"):
        aggregator.aggregate(source_data, config)


def test_api_linker_aggregate_sources_uses_named_connectors() -> None:
    linker = ApiLinker(log_level="ERROR")
    linker.sources["crm"] = StaticSourceConnector(
        [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    )
    linker.sources["billing"] = StaticSourceConnector(
        [
            {"customer_id": 1, "plan": "pro"},
            {"customer_id": 2, "plan": "basic"},
        ]
    )
    aggregation_config = {
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
                "fields": [
                    {"source": "plan", "target": "plan"},
                ],
            },
        ],
        "join_type": "inner",
        "merge_strategy": "flat",
    }

    result = linker.aggregate_sources(
        source_requests={
            "crm": {"connector": "crm", "endpoint": "items"},
            "billing": {"connector": "billing", "endpoint": "items"},
        },
        aggregation_config=aggregation_config,
        parallel=True,
    )

    assert result == [
        {"id": 1, "name": "Alice", "plan": "pro"},
        {"id": 2, "name": "Bob", "plan": "basic"},
    ]
