---
title: 'ApiLinker: A Declarative Framework for Reproducible REST API Integration in Computational Research'
tags:
  - Python
  - REST API
  - data integration
  - research software engineering
  - reproducibility
  - FAIR principles
authors:
  - given-names: Kyriakos
    surname: Kartas
    orcid: 0009-0001-6477-4676
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 04 December 2025
bibliography: paper.bib
---

# Summary

ApiLinker is an open-source Python framework that provides a declarative, configuration-driven approach to REST API integration for computational research. The framework addresses a fundamental challenge in modern research computing: the heterogeneity of web-based data services, which manifests in divergent authentication protocols, pagination schemes, response structures, and rate-limiting policies. Rather than requiring researchers to implement bespoke integration scripts for each service combination, ApiLinker abstracts these concerns into reusable, composable components that can be specified through version-controlled configuration files.

The architecture decomposes API integration into five orthogonal concerns: transport (connectors), schema transformation (field mappers with composable transformers), credential management (authentication handlers), temporal orchestration (schedulers), and failure recovery (circuit breakers, exponential backoff, dead-letter queues). This separation enables focused reasoning about each concern while supporting composition for complex multi-service workflows. The framework ships with scientific connectors for NCBI E-utilities, arXiv, CrossRef, Semantic Scholar, PubChem, and ORCID, facilitating immediate productivity for common research data acquisition patterns. Enterprise-grade features include integrations with secret management systems (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, Google Cloud Secret Manager) and OpenTelemetry-based observability for production deployments.

By elevating API integrations from imperative scripts to declarative configurations, ApiLinker enables reproducible data pipelines that can be archived alongside research datasets, reviewed during peer evaluation, and re-executed across computing environments—supporting the FAIR principles of findability, accessibility, interoperability, and reusability [@Wilkinson2016].

# Statement of Need

Computational research increasingly depends on integrating data from distributed web services. Bibliometric analyses combine metadata from CrossRef with citation metrics from Semantic Scholar; bioinformatics workflows aggregate sequences from GenBank with compound properties from PubChem; systematic literature reviews harvest publications from PubMed and arXiv. Each service exposes REST APIs with distinct authentication requirements, pagination strategies, response schemas, and operational constraints [@Fowler2014].

This heterogeneity imposes substantial engineering overhead on researchers. Studies across bioinformatics [@Ison2013], environmental science [@Vitolo2015], and computational social science [@Lomborg2014] document that API integration code often constitutes a significant fraction of total development effort. The resulting scripts are typically optimised for immediate functionality rather than long-term maintainability, lacking the error handling, retry logic, and configuration management necessary for reliable operation. Such code resists peer review, complicates replication efforts, and frequently fails silently when upstream services modify their interfaces.

Existing solutions address different segments of this problem space but introduce their own constraints. Workflow orchestrators like Apache Airflow [@Airflow] provide sophisticated scheduling and monitoring but require substantial infrastructure overhead disproportionate to many research integration tasks. Visual automation platforms such as Zapier [@Zapier] and n8n [@n8n] reduce programming requirements but constrain transformation expressiveness and lack the configuration-as-code semantics essential for reproducible research. Service-specific client libraries abstract individual APIs but do not address cross-service coordination or standardised error handling.

ApiLinker occupies a distinctive position in this landscape: a lightweight, Python-native framework that prioritises declarative configuration, deterministic transformations, and explicit resilience mechanisms. The framework is designed to operate as an embedded library within existing research codebases or as a standalone command-line tool for scripted automation, with minimal external dependencies and no mandatory infrastructure requirements.

# Architecture and Implementation

ApiLinker comprises six principal components organised in a layered architecture. The central `ApiLinker` orchestrator coordinates workflow execution, managing source and target connectors, invoking the mapper for data transformation, and delegating to the scheduler for timed execution:

```python
from apilinker import ApiLinker

linker = ApiLinker(config_path="integration.yaml")
result = linker.sync()
```

**Connectors** encapsulate HTTP transport concerns including request construction, authentication application, response parsing, pagination traversal, and retry logic. The framework supports multiple pagination strategies (offset-based, cursor-based, link-header navigation) and respects provider-specified rate limits.

**Field Mappers** implement schema transformation using a declarative mapping model. Each rule specifies source and target field paths using dot notation for nested access, optional transformation functions, and conditional inclusion predicates:

```yaml
mapping:
  fields:
    - source: DOI
      target: identifier
      transform: lowercase
    - source: title[0]
      target: name
      condition:
        field: type
        operator: eq
        value: journal-article
```

Built-in transformers address common requirements (case conversion, date parsing, type coercion), while the plugin system enables registration of domain-specific transformations.

**Authentication Managers** support API keys, bearer tokens, basic authentication, and OAuth 2.0 (including client credentials, authorization code with PKCE, and device flow grants). Credentials may reference environment variables or integrate with enterprise secret managers.

**Schedulers** enable unattended execution using interval-based or cron-expression timing, with configurable alerting through PagerDuty, Slack, or email integrations.

**Error Handling** incorporates production-grade resilience patterns: exponential backoff with jitter for transient failures, circuit breakers [@Nygard2018] to prevent cascading failures, and dead-letter queues [@Hohpe2003] to preserve failed operations for analysis and replay.

The framework maintains a small dependency surface (httpx, pydantic, pyyaml, typer, croniter) to reduce installation friction, with optional integrations for observability (OpenTelemetry, Prometheus) and secret management available as extras.

# Scientific Connectors

ApiLinker provides pre-built connectors for research-oriented APIs:

- **NCBIConnector**: Access to PubMed, GenBank, ClinVar, and GEO via E-utilities, implementing appropriate rate limiting and batch protocols
- **ArXivConnector**: Preprint discovery and metadata retrieval with Atom XML parsing and category filtering
- **CrossRefConnector**: Bibliographic metadata queries by DOI, title, author, or ISSN with polite pool compliance
- **SemanticScholarConnector**: Citation counts, reference networks, and influential citation identification
- **PubChemConnector**: Chemical compound queries returning CIDs, SMILES representations, and bioactivity data
- **ORCIDConnector**: Researcher profiles and publication lists for disambiguation workflows

These connectors enable immediate productivity for systematic literature reviews, bibliometric analyses, and cheminformatics data aggregation without requiring researchers to implement service-specific protocols.

# Quality Assurance

The test suite comprises 38 modules with over 250 individual test cases, achieving 82% line coverage across core components. Continuous integration via GitHub Actions executes tests across Python versions 3.8 through 3.11, with parallel jobs for linting (flake8), type checking (mypy), and formatting verification (black).

Benchmark scenarios document performance characteristics: bibliographic enrichment (CrossRef → Semantic Scholar) achieves 45.3 ± 3.2 records per second under nominal conditions with 99.7% success rate; under 10% fault injection, circuit breakers and retries maintain 96-99% success rates while reducing throughput to 12-14 records per second. The dead-letter queue preserves 0.3-3.9% of operations for post-hoc analysis.

# Acknowledgements

We acknowledge contributions from the open-source community and feedback from early adopters who helped refine the design and functionality of ApiLinker.

# References
