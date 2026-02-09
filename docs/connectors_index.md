## Connectors Index

This page lists built-in connectors with links to source files and basic usage.

### Scientific Connectors

- NCBI (PubMed, GenBank) — `apilinker/connectors/scientific/ncbi.py`
  - Usage: `from apilinker import NCBIConnector`
- arXiv — `apilinker/connectors/scientific/arxiv.py`
  - Usage: `from apilinker import ArXivConnector`
- CrossRef — `apilinker/connectors/scientific/crossref.py`
  - Usage: `from apilinker import CrossRefConnector`
- Semantic Scholar — `apilinker/connectors/scientific/semantic_scholar.py`
  - Usage: `from apilinker import SemanticScholarConnector`
- PubChem — `apilinker/connectors/scientific/pubchem.py`
  - Usage: `from apilinker import PubChemConnector`
- ORCID — `apilinker/connectors/scientific/orcid.py`
  - Usage: `from apilinker import ORCIDConnector`

### General Research Connectors

- GitHub — `apilinker/connectors/general/github.py`
  - Usage: `from apilinker import GitHubConnector`
- NASA — `apilinker/connectors/general/nasa.py`
  - Usage: `from apilinker import NASAConnector`
- SSE - `apilinker/connectors/general/sse.py`
  - Usage: `from apilinker import SSEConnector`

### Notes

- All connectors inherit from the common `ApiConnector` base and expose endpoints via their `.endpoints` mapping.
- Authentication varies per provider (see each source file for details).
- Respect rate limits and terms of service; include a descriptive User-Agent where applicable.

The following connectors are exported at the top level in `apilinker/__init__.py` and available for import as shown above.


