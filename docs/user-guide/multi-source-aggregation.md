# Multi-Source Aggregation

ApiLinker v0.7.1 can combine records from multiple REST sources using keyed joins before you map or send data to a target API. This is useful when identifiers live in different systems (for example CRM users and a billing service).

!!! note "Library API only"
    YAML configuration and CLI commands for aggregation are planned for v0.7.2. In v0.7.1, use the Python API shown below.

## Overview

| Component | Role |
|-----------|------|
| `MultiSourceAggregator` | Joins pre-fetched payloads by key |
| `ApiLinker.aggregate_sources()` | Fetches from named connectors, then aggregates |
| `ApiLinker.register_source()` | Registers extra source connectors by alias |

## Join types

- `inner` — only keys present in every source
- `left` — all keys from the first configured source
- `right` — all keys from the last configured source
- `outer` — union of keys across sources

## Merge strategies

- `flat` — merge fields into one object (use `conflict_resolution` when names collide)
- `namespace` — nest each source under its configured `namespace`

## Conflict resolution (flat merge)

- `prefer_first` — keep the first source’s value
- `prefer_last` — keep the last source’s value
- `error` — raise if the same field exists in multiple sources

## Example

```python
from apilinker import ApiLinker

linker = ApiLinker(log_level="INFO")

# Register connectors (or load from YAML and call register_source)
linker.register_source("crm", crm_connector)
linker.register_source("billing", billing_connector)

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

rows = linker.aggregate_sources(
    source_requests={
        "crm": {"connector": "crm", "endpoint": "list_users"},
        "billing": {"connector": "billing", "endpoint": "list_plans"},
    },
    aggregation_config=aggregation_config,
    parallel=True,
)

# rows is a list of merged dicts ready for mapping or target sync
```

## Pre-fetched data

If you already have payloads, use `aggregate_source_data()`:

```python
merged = linker.aggregate_source_data(
    {
        "crm": [{"id": 1, "name": "Alice"}],
        "billing": [{"customer_id": 1, "plan": "pro"}],
    },
    aggregation_config,
)
```

## Parallel fetching

`aggregate_sources(..., parallel=True)` uses a thread pool (up to eight workers) when more than one source is requested. Set `parallel=False` for deterministic, sequential fetches.

## See also

- [Core Components](../developer-guide/core-components.md) — streaming and connector APIs
- `examples/multi_source_aggregation.py` — runnable stub example
- [ROADMAP.md](https://github.com/kkartas/APILinker/blob/main/ROADMAP.md) — YAML/CLI aggregation (v0.7.2)
