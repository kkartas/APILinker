## Test Coverage

We recommend running tests with coverage locally and in CI.

### Locally

```bash
pytest --cov=apilinker --cov-report=term-missing
```

### In CI

The CI workflow runs tests; to enable coverage and fail under a threshold, add:

```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=apilinker --cov-report=xml --cov-fail-under=80
```

Optionally, upload coverage to a service (Codecov/Coveralls) and add a badge to the README.


