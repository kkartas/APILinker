# Installation

There are several ways to install ApiLinker depending on your use case.

## Standard Installation

The easiest way to install ApiLinker is via pip:

```bash
pip install apilinker
```

This will install ApiLinker with its core dependencies.

## Development Installation

If you're planning to contribute to ApiLinker or want to install the package with development dependencies:

```bash
# Clone the repository
git clone https://github.com/yourusername/apilinker.git
cd apilinker

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Install with Optional Features

ApiLinker comes with optional dependencies for different features:

```bash
# Install with documentation tools
pip install "apilinker[docs]"

# Install with all optional dependencies
pip install "apilinker[dev,docs]"
```

## Requirements

ApiLinker requires:

- Python 3.8 or higher
- Core dependencies:
  - httpx: For HTTP requests
  - pydantic: For data validation
  - pyyaml: For YAML config support
  - typer: For CLI functionality
  - croniter: For cron-based scheduling

## Verifying Installation

After installation, you can verify that ApiLinker is working correctly:

```bash
# Check the version
apilinker version

# Create a sample configuration
apilinker init
```

## System Requirements

ApiLinker is designed to work on all major operating systems:

- Linux
- macOS
- Windows

The package is lightweight and doesn't require significant system resources for most use cases. However, performance may vary depending on the volume of data being processed and the frequency of API operations.
