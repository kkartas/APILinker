# Quick Start

## CLI Usage

1. Create a `config.yaml` file:

```yaml
source:
  type: rest
  base_url: https://api.example.com
  endpoints:
    list: { path: /items, method: GET }
target:
  type: rest
  base_url: https://api.dest.com
  endpoints:
    create: { path: /items, method: POST }
mapping:
  - source: list
    target: create
    fields:
      - { source: id, target: external_id }
```

2. Run the sync:

```bash
apilinker sync --config config.yaml
```

## Python Usage

```python
from apilinker import ApiLinker

linker = ApiLinker()
linker.add_source(type="rest", base_url="...")
linker.add_target(type="rest", base_url="...")
linker.sync()
```
