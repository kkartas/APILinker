# Research Connectors

ApiLinker includes specialized connectors for scientific and research APIs, featuring domain-specific optimizations like citation parsing and academic rate limiting.

## Supported Connectors

| Connector | Description |
|-----------|-------------|
| **NCBI** | PubMed, GenBank, ClinVar, and more. |
| **arXiv** | Academic preprints across sciences. |
| **CrossRef** | Citation data and DOI resolution. |
| **Semantic Scholar** | AI-powered academic search. |
| **PubChem** | Chemical compounds and bioassays. |
| **ORCID** | Researcher profiles. |

## Architecture

Research connectors inherit from `ResearchConnectorBase`, which adds:

- **Ethical Usage**: Automatic inclusion of contact info in User-Agent.
- **Rate Limiting**: Conservative defaults for academic infrastructure.
- **Citation Parsing**: Tools to extract structured metadata.

### Example: NCBI Connector

The `NCBIConnector` handles E-utilities authentication and batch processing.

```python
ncbi = NCBIConnector(email="researcher@university.edu")
papers = ncbi.search_pubmed("CRISPR", max_results=50)
```
