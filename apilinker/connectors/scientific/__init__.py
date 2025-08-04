"""
Scientific API connectors for research workflows.

This module provides specialized connectors for common scientific APIs
used in research, including bioinformatics, academic publications,
and other research data sources.
"""

from .ncbi import NCBIConnector
from .arxiv import ArXivConnector

__all__ = [
    "NCBIConnector",
    "ArXivConnector"
]