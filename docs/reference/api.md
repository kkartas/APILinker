# API Reference

This page provides comprehensive API documentation for all ApiLinker classes and modules.

## Core Classes

### ApiLinker

Main orchestrator class for API integration workflows.

::: apilinker.ApiLinker
    options:
      show_source: true
      members:
        - __init__
        - add_source
        - add_target
        - add_mapping
        - sync
        - fetch
        - send

### ApiConnector

Base class for all API connectors.

::: apilinker.core.connector.ApiConnector
    options:
      show_source: true
      members:
        - __init__
        - fetch_data
        - send_data
        - stream_sse
        - consume_sse
        - check_health

### FieldMapper

Data transformation and field mapping engine.

::: apilinker.core.mapper.FieldMapper
    options:
      show_source: true
      members:
        - add_mapping
        - transform
        - register_transformer

### Monitoring & Alerting

System monitoring and health checks.

::: apilinker.core.monitoring.MonitoringManager
    options:
      show_source: true
      members:
        - __init__
        - register_health_check
        - add_rule
        - add_integration
        - run_health_checks
        - get_alert_history

## Research Connectors

For research connector documentation, see [Research Connectors Guide](../user-guide/research-connectors.md).

### Available Connectors

- **NCBIConnector**: PubMed and GenBank
- **ArXivConnector**: arXiv preprints  
- **CrossRefConnector**: Citation data
- **SemanticScholarConnector**: AI-powered search
- **PubChemConnector**: Chemical compounds
- **ORCIDConnector**: Researcher profiles
- **GitHubConnector**: Code repositories
- **NASAConnector**: Earth/space data
- **SSEConnector**: Real-time Server-Sent Events streams
