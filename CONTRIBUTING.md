# Contributing to ApiLinker

Thank you for your interest in contributing to ApiLinker! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it to understand what kind of behavior is expected in our community.

## Getting Started

### Development Setup

1. **Fork the repository** on GitHub.

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/apilinker.git
   cd apilinker
   ```

3. **Set up the development environment**:
   ```bash
   # Create and activate a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Development Workflow

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code and tests for your changes
   - Follow the coding style guidelines (see below)
   - Keep your changes focused and related to one issue/feature

3. **Run the tests** to ensure your changes don't break existing functionality:
   ```bash
   pytest
   ```

4. **Run code quality checks**:
   ```bash
   flake8 apilinker
   mypy apilinker
   black apilinker --check
   ```

5. **Commit your changes** using clear commit messages:
   ```bash
   git commit -m "Add feature: concise description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a pull request** to the main repository.

## Coding Style Guidelines

- Follow [PEP 8](https://pep8.org/) for Python code style
- Use [Black](https://black.readthedocs.io/) for automatic code formatting
- Write docstrings in the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Maintain 100% test coverage for new code when possible

## Pull Request Guidelines

- **One feature or bug fix per pull request** to keep the review process simple
- **Include tests** for any new functionality
- **Update documentation** for any changed functionality
- **Describe your changes** in the pull request description
- **Reference related issues** in the pull request description

## Adding Features

### Adding a New Transformer

1. Add the new transformer function to `apilinker.core.mapper.FieldMapper._register_built_in_transformers`
2. Add documentation for the transformer in `docs/guide/mapping.md`
3. Add tests for the transformer in `tests/test_mapper.py`

### Adding a New Connector Type

1. Create a new connector class that extends the base connector
2. Update the connector factory to support the new type
3. Add documentation for the new connector type
4. Add tests for the new connector

## Creating Plugins

ApiLinker supports plugins for custom connectors, transformers, and authentication methods. See the [Plugin Development Guide](https://kkartas.github.io/apilinker/guide/plugins) for details on creating plugins.

## Documentation

- Update the documentation when adding or changing features
- Use clear, concise language accessible to users with different experience levels
- Include examples for new features

### Building the Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build the docs
mkdocs build

# Serve the docs locally
mkdocs serve
```

## Reporting Issues

- Use the GitHub issue tracker
- Include a detailed description of the issue
- Include steps to reproduce, expected vs actual behavior
- Include version information (Python version, ApiLinker version, OS)

## Release Process

Project maintainers are responsible for releases, which follow this process:

1. Update version in `pyproject.toml`
2. Update the changelog with all significant changes
3. Create a GitHub release with release notes
4. Publish to PyPI using the CI/CD pipeline

## Thank You

Thank you for contributing to ApiLinker! Your help is essential for making this project better for everyone.
