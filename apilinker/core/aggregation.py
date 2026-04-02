"""
Multi-source aggregation utilities for combining records across connectors.
"""

import logging
from copy import deepcopy
from enum import Enum
from itertools import product
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from apilinker.core.mapper import FieldMapper

logger = logging.getLogger(__name__)


class JoinType(str, Enum):
    """Supported join strategies for multi-source aggregation."""

    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    OUTER = "outer"


class MergeStrategy(str, Enum):
    """Supported record merge strategies."""

    FLAT = "flat"
    NAMESPACE = "namespace"


class ConflictResolution(str, Enum):
    """Conflict resolution policy for flat merges."""

    PREFER_FIRST = "prefer_first"
    PREFER_LAST = "prefer_last"
    ERROR = "error"


class AggregationSourceConfig(BaseModel):
    """Configuration for a single aggregated source."""

    name: str
    join_key: str = "id"
    fields: Optional[List[Dict[str, Any]]] = None
    namespace: Optional[str] = None


class MultiSourceAggregationConfig(BaseModel):
    """Configuration model for multi-source aggregation."""

    sources: List[AggregationSourceConfig] = Field(default_factory=list)
    join_type: JoinType = JoinType.INNER
    merge_strategy: MergeStrategy = MergeStrategy.FLAT
    conflict_resolution: ConflictResolution = ConflictResolution.PREFER_FIRST


class MultiSourceAggregator:
    """
    Combine records fetched from multiple sources using keyed joins.

    The aggregator is intentionally independent from connector I/O. It operates
    on already-fetched payloads so ApiLinker can orchestrate fetching separately
    and optionally do it in parallel.
    """

    def __init__(self, mapper: Optional[FieldMapper] = None) -> None:
        self.mapper = mapper or FieldMapper()

    def aggregate(
        self,
        source_data: Dict[str, Union[Dict[str, Any], List[Dict[str, Any]]]],
        config: Union[MultiSourceAggregationConfig, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Aggregate payloads from multiple sources according to a join plan.

        Args:
            source_data: Mapping of source name to fetched payload.
            config: Aggregation config model or raw dict.

        Returns:
            Aggregated record list.
        """
        aggregation_config = (
            config
            if isinstance(config, MultiSourceAggregationConfig)
            else MultiSourceAggregationConfig(**config)
        )

        if not aggregation_config.sources:
            raise ValueError("Aggregation config must define at least one source")

        prepared_sources = []
        for source_config in aggregation_config.sources:
            if source_config.name not in source_data:
                raise ValueError(
                    f"Aggregation source '{source_config.name}' is missing from source data"
                )
            prepared_sources.append(
                self._prepare_source(source_config, source_data[source_config.name])
            )

        join_keys = self._select_join_keys(
            prepared_sources, aggregation_config.join_type
        )

        aggregated_rows: List[Dict[str, Any]] = []
        for join_key in join_keys:
            grouped_records = []
            for prepared_source in prepared_sources:
                records = prepared_source["index"].get(join_key)
                grouped_records.append(records if records else [None])

            for record_group in product(*grouped_records):
                aggregated_rows.append(
                    self._merge_record_group(
                        prepared_sources,
                        list(record_group),
                        aggregation_config.merge_strategy,
                        aggregation_config.conflict_resolution,
                    )
                )

        return aggregated_rows

    def _prepare_source(
        self,
        source_config: AggregationSourceConfig,
        raw_payload: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Index a source payload by join key while preserving source order."""
        records = self._normalize_records(raw_payload)
        indexed_records: Dict[Any, List[Dict[str, Any]]] = {}
        ordered_keys: List[Any] = []

        for record in records:
            join_value = self.mapper.get_value_from_path(record, source_config.join_key)
            if join_value is None:
                logger.debug(
                    "Skipping record from source '%s' without join key '%s'",
                    source_config.name,
                    source_config.join_key,
                )
                continue

            projected_record = (
                self.mapper.map_fields(record, source_config.fields)
                if source_config.fields
                else deepcopy(record)
            )

            if join_value not in indexed_records:
                indexed_records[join_value] = []
                ordered_keys.append(join_value)
            indexed_records[join_value].append(projected_record)

        return {
            "config": source_config,
            "index": indexed_records,
            "ordered_keys": ordered_keys,
        }

    def _normalize_records(
        self, payload: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Normalize payloads to a list of dictionaries."""
        if isinstance(payload, list):
            normalized: List[Dict[str, Any]] = []
            for item in payload:
                if isinstance(item, dict):
                    normalized.append(item)
                else:
                    normalized.append({"value": item})
            return normalized

        if isinstance(payload, dict):
            return [payload]

        return [{"value": payload}]

    def _select_join_keys(
        self, prepared_sources: List[Dict[str, Any]], join_type: JoinType
    ) -> List[Any]:
        """Select join keys while keeping stable source ordering."""
        if not prepared_sources:
            return []

        if join_type == JoinType.LEFT:
            return list(prepared_sources[0]["ordered_keys"])

        if join_type == JoinType.RIGHT:
            return list(prepared_sources[-1]["ordered_keys"])

        if join_type == JoinType.INNER:
            first_keys = prepared_sources[0]["ordered_keys"]
            return [
                join_key
                for join_key in first_keys
                if all(join_key in source["index"] for source in prepared_sources[1:])
            ]

        ordered_join_keys: List[Any] = []
        seen_keys = set()
        for prepared_source in prepared_sources:
            for join_key in prepared_source["ordered_keys"]:
                if join_key not in seen_keys:
                    seen_keys.add(join_key)
                    ordered_join_keys.append(join_key)
        return ordered_join_keys

    def _merge_record_group(
        self,
        prepared_sources: List[Dict[str, Any]],
        record_group: List[Optional[Dict[str, Any]]],
        merge_strategy: MergeStrategy,
        conflict_resolution: ConflictResolution,
    ) -> Dict[str, Any]:
        """Merge one joined record combination into an output row."""
        if merge_strategy == MergeStrategy.NAMESPACE:
            namespaced_record: Dict[str, Any] = {}
            for prepared_source, record in zip(prepared_sources, record_group):
                source_config = prepared_source["config"]
                namespace = source_config.namespace or source_config.name
                namespaced_record[namespace] = deepcopy(record) if record else None
            return namespaced_record

        merged_record: Dict[str, Any] = {}
        for prepared_source, record in zip(prepared_sources, record_group):
            if not record:
                continue
            source_name = prepared_source["config"].name
            self._merge_flat_record(
                merged_record, record, conflict_resolution, source_name
            )
        return merged_record

    def _merge_flat_record(
        self,
        current: Dict[str, Any],
        incoming: Dict[str, Any],
        conflict_resolution: ConflictResolution,
        source_name: str,
        field_path: str = "",
    ) -> None:
        """Recursively merge a record into the current output row."""
        for key, value in incoming.items():
            current_path = f"{field_path}.{key}" if field_path else key

            if key not in current:
                current[key] = deepcopy(value)
                continue

            existing_value = current[key]

            if isinstance(existing_value, dict) and isinstance(value, dict):
                self._merge_flat_record(
                    existing_value,
                    value,
                    conflict_resolution,
                    source_name,
                    field_path=current_path,
                )
                continue

            if value is None or existing_value == value:
                continue

            if existing_value is None or conflict_resolution == ConflictResolution.PREFER_LAST:
                current[key] = deepcopy(value)
                continue

            if conflict_resolution == ConflictResolution.PREFER_FIRST:
                continue

            raise ValueError(
                f"Conflict detected for field '{current_path}' while merging source '{source_name}'"
            )
