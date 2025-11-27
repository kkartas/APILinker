# Development Guide

## Code Quality

This project maintains code quality through automated testing and linting tools.

### Running Tests

Run the full test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=apilinker --cov-report=html
```

### Code Formatting and Linting

Check code style:
```bash
flake8 apilinker
mypy apilinker
black apilinker --check
```

Auto-format code:
```bash
black apilinker
```

### Best Practices

1. **Write tests for new features** - Maintain or improve code coverage
2. **Run tests before committing** - Ensure changes don't break existing functionality
3. **Follow PEP 8 style guidelines** - Use black for consistent formatting
4. **Add type hints** - Help with code maintainability and IDE support
