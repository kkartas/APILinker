#!/usr/bin/env python
"""Setup script for ApiLinker."""

import os
import re
from setuptools import setup, find_packages

# Read version from __init__.py
with open(os.path.join("apilinker", "__init__.py"), encoding="utf-8") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

# Read long description from README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="apilinker",
    version=version,
    description="A universal bridge to connect, map, and automate data transfer between any two REST APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/apilinker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="api, integration, data mapping, rest api, connector",
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.23.0",
        "pyyaml>=6.0",
        "typer>=0.7.0",
        "pydantic>=1.10.2",
        "croniter>=1.3.8",
        "rich>=12.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.8.0",
            "isort>=5.10.1",
            "flake8>=5.0.4",
            "mypy>=0.982",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
            "sphinx-autodoc-typehints>=2.0.0",
            "sphinx-autoapi>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "apilinker=apilinker.cli:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
