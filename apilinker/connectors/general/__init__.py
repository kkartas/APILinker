"""
General API connectors for research workflows across domains.

This module provides connectors for non-scientific APIs that are
valuable for research, including code repositories, social platforms,
and data sources.
"""

from .github import GitHubConnector
from .nasa import NASAConnector
from .sse import SSEConnector

__all__ = ["GitHubConnector", "NASAConnector", "SSEConnector"]
