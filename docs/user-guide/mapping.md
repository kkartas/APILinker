# Mapping & Transformation

The mapping engine is the core of ApiLinker, allowing you to transform data structures between APIs.

## Field Mapping

Define mappings in the `mapping` section:

```yaml
mapping:
  - source: source_endpoint
    target: target_endpoint
    fields:
      - source: id
        target: external_id
```

## Transformations

Apply transformations to modify data during sync.

```yaml
- source: created_at
  target: timestamp
  transform: iso_to_timestamp
```

### Built-in Transformers

- `lowercase`, `uppercase`, `strip`
- `iso_to_timestamp`, `timestamp_to_iso`
- `to_int`, `to_float`, `to_bool`
- `json_parse`, `json_stringify`

## Conditional Mapping

Map fields only when specific conditions are met:

```yaml
- source: status
  target: active
  condition:
    field: status
    operator: eq
    value: active
```
