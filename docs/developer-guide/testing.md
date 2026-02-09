# Testing & Validation

ApiLinker follows rigorous testing practices to ensure reliability and correctness.

## Test Suite Overview

The test suite covers:

- **Unit tests**: Core functionality (mapping, transformers, authentication)
- **Integration tests**: End-to-end API workflows
- **Connector tests**: Research connector validation
- **Error handling tests**: Retry logic, circuit breakers, DLQ

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=apilinker --cov-report=html
```

View coverage report at `htmlcov/index.html`.

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Connector tests
pytest tests/connectors/
```

## Test Coverage

Current test coverage: **>80%**

Coverage is tracked automatically in CI/CD. View the latest coverage report on [GitHub Actions](https://github.com/kkartas/APILinker/actions).

## Continuous Integration

ApiLinker uses GitHub Actions for automated testing on every commit:

- **Multi-platform**: Tests run on Ubuntu, Windows, and macOS
- **Multi-version**: Python 3.9, 3.10, 3.11, 3.12
- **Quality checks**: Linting (flake8, black), type checking (mypy)
- **Coverage enforcement**: Minimum 80% code coverage required

View CI configuration: [`.github/workflows/ci.yml`](https://github.com/kkartas/APILinker/blob/main/.github/workflows/ci.yml)

## Testing Methodology

### Unit Tests

Unit tests validate individual components in isolation:

```python
def test_field_mapper_basic():
    mapper = FieldMapper()
    mapper.add_mapping("source_field", "target_field")
    
    result = mapper.transform({"source_field": "value"})
    assert result == {"target_field": "value"}
```

### Integration Tests

Integration tests validate complete workflows:

```python
def test_github_to_gitlab_sync():
    linker = ApiLinker()
    linker.add_source(type="rest", base_url="...")
    linker.add_target(type="rest", base_url="...")
    
    result = linker.sync(dry_run=True)
    assert result.success == True
```

### Mock Testing

External APIs are mocked for deterministic testing:

```python
@pytest.fixture
def mock_api(requests_mock):
    requests_mock.get(
        "https://api.example.com/users",
        json=[{"id": 1, "name": "Alice"}]
    )
```

## Validation Framework

### Schema Validation

APIs can enforce JSON Schema validation:

```yaml
target:
  endpoints:
    create_item:
      request_schema:
        type: object
        properties:
          id: { type: string }
        required: [id]

validation:
  strict_mode: true  # Fail if schema validation fails
```

### Data Integrity Tests

Benchmarks include invariant preservation tests:

- **ID preservation**: Ensures unique identifiers are maintained
- **Type consistency**: Validates data type transformations
- **Referential integrity**: Checks foreign key relationships

## Performance Testing

See [Benchmarks](benchmarks.md) for performance validation.

## Reproducibility

All tests are designed for reproducibility:

- **Fixed random seeds** for deterministic behavior
- **Mock servers** for consistent external dependencies
- **Version pinning** in test environments

## Contributing Tests

When contributing code, please:

1. Add unit tests for new features
2. Ensure coverage remains >80%
3. Run full test suite before submitting PR
4. Document test scenarios

See [Contributing Guide](contributing.md) for details.
