"""
ApiLinker: A universal bridge to connect, map, and automate data transfer between any two REST APIs.

This package provides tools for connecting to REST APIs, mapping data fields between them,
scheduling automatic data transfers, and extending functionality through plugins.

New in version 1.1: Scientific API connectors for research workflows including
NCBI (PubMed, GenBank) and arXiv connectors.
"""

__version__ = "1.0.4"

# Core components
from apilinker.core.connector import ApiConnector
from apilinker.core.mapper import FieldMapper
from apilinker.core.scheduler import Scheduler

# Main class
from .api_linker import ApiLinker, SyncResult

# Scientific connectors for research workflows
try:
    from .connectors.scientific.ncbi import NCBIConnector
    from .connectors.scientific.arxiv import ArXivConnector
    scientific_connectors_available = True
    
    __all__ = [
        "ApiLinker", 
        "SyncResult",
        "ApiConnector", 
        "FieldMapper", 
        "Scheduler",
        "NCBIConnector",
        "ArXivConnector"
    ]
except ImportError:
    # Scientific connectors not available
    scientific_connectors_available = False
    
    __all__ = [
        "ApiLinker",
        "SyncResult", 
        "ApiConnector", 
        "FieldMapper", 
        "Scheduler"
    ]
