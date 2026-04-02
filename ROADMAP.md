# ApiLinker Roadmap

This document tracks planned features, enhancements, and improvements for ApiLinker. Features are organized by version and priority.

**Current Version:** 0.7.0
**Last Updated:** 2026-02-09

## Version Strategy

- **Patch releases (0.7.x)**: Stability, CI/build correctness, runtime reliability, documentation consistency
- **Minor releases (0.8.x, 0.9.x, 1.1.x)**: New capabilities, readiness hardening, scientific workflow expansion
- **Major releases (1.0.0, 2.0.0)**: Production guarantees, compatibility policy, and long-term architecture evolution

---

## Version 0.5.0 - Observability & Enterprise Security
**Focus:** Production observability and enterprise-grade secret management

### High Priority

#### OpenTelemetry Integration ⭐ ✅
- **Status:** Implemented (v0.4.2)
- **Priority:** High
- **Description:** Structured metrics and distributed tracing for production observability
- **Features:**
  - ✅ OpenTelemetry SDK integration
  - ✅ Distributed tracing for sync operations
  - ✅ Prometheus metrics export (requests/sec, latency, error rates)
  - ✅ Custom metrics for API calls, transformations, errors
  - ✅ Performance monitoring dashboards support
  - ✅ Request/response instrumentation
- **Dependencies:** `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-prometheus`
- **Impact:** Critical for production deployments and debugging
- **Implementation:** `apilinker/core/observability.py`

#### Secret Management Integrations ⭐ ✅
- **Status:** Implemented (v0.5.0)
- **Priority:** High
- **Description:** Enterprise secret storage integrations with least-privilege defaults
- **Features:**
  - ✅ HashiCorp Vault integration
  - ✅ AWS Secrets Manager support
  - ✅ Azure Key Vault support
  - ✅ Google Secret Manager support
  - ✅ Pluggable secret provider interface
  - ✅ Automatic credential rotation support
  - ✅ Least-privilege access patterns
- **Dependencies:** `hvac` (Vault), `boto3` (AWS), `azure-keyvault-secrets`, `google-cloud-secret-manager`
- **Impact:** Essential for enterprise deployments and security compliance
- **Implementation:** `apilinker/core/secrets.py`

### Medium Priority

#### Enhanced Rate Limiting Management ✅
- **Status:** Implemented (v0.5.3)
- **Priority:** Medium
- **Description:** Built-in intelligent rate limit handling
- **Features:**
  - Token bucket algorithm implementation
  - Leaky bucket algorithm support
  - Per-endpoint rate limit tracking
  - Automatic throttling based on API responses
  - Rate limit headers parsing (X-RateLimit-*)
  - Configurable rate limit strategies
- **Dependencies:** None (built-in)
- **Impact:** Improves reliability and prevents API bans

#### Advanced Monitoring & Alerting ✅
- **Status:** Implemented (v0.5.4)
- **Priority:** Medium
- **Description:** Production-ready monitoring and alerting capabilities
- **Features:**
  - ✅ Health check endpoints (HealthStatus, HealthCheckResult)
  - ✅ Configurable alert rules (ThresholdAlertRule, StatusAlertRule)
  - ✅ Integration with PagerDuty, Slack, email
  - ✅ Alert thresholds and conditions
  - ✅ Alert history and deduplication
- **Dependencies:** `httpx` (for webhooks)
- **Impact:** Critical for production operations
- **Implementation:** `apilinker/core/monitoring.py`

---

## Version 0.6.0 - Event-Driven Architecture
**Focus:** Webhooks, message queues, and real-time data processing

### High Priority

#### Webhook Connectors ⭐ ✅
- **Status:** Implemented (v0.6.0)
- **Priority:** High
- **Description:** First-class support for receiving webhooks and triggering syncs
- **Features:**
  - ✅ HTTP webhook server/listener (FastAPI-based)
  - ✅ Webhook endpoint registration and management
  - ✅ Event filtering and routing
  - ✅ Signature verification (HMAC, JWT)
  - ✅ Webhook replay and retry mechanisms
  - ✅ Webhook-to-API mapping
  - ✅ Configurable webhook endpoints
- **Dependencies:** `fastapi`, `uvicorn` (webhook server), `pyjwt` (JWT verification)
- **Impact:** Enables real-time, event-driven integrations
- **Implementation:** `apilinker/core/webhooks.py`

#### Message Queue Connectors ⭐
- **Status:** Implemented (v0.6.0)
- **Priority:** High
- **Description:** Support for event-driven pipelines via message queues
- **Features:**
  - ✅ RabbitMQ connector (consumer/producer)
  - ✅ Redis Pub/Sub support
  - ✅ AWS SQS integration
  - ✅ Apache Kafka connector (basic)
  - ✅ Message transformation and routing
  - ✅ Dead letter queue integration
  - ✅ Consumer group management (Kafka group id)
- **Dependencies:** `pika` (RabbitMQ), `redis`, `boto3` (SQS), `kafka-python`
- **Impact:** Enables scalable, event-driven architectures
- **Implementation:** `apilinker/core/message_queue.py`, `apilinker/core/message_queue_connectors.py`

### Medium Priority

#### Server-Sent Events (SSE) Support
- **Status:** Implemented (post-v0.6.1)
- **Priority:** Medium
- **Description:** Real-time data processing via SSE
- **Features:**
  - ✅  SSE client connector (`SSEConnector`)
  - ✅  Streaming response handling (`ApiConnector.stream_sse`)
  - ✅  Chunked data processing (`ApiConnector.consume_sse`)
  - ✅  Backpressure management (`block` and `drop_oldest` policies)
  - ✅  Reconnection logic (automatic reconnect + Last-Event-ID resume)
- **Dependencies:** None (built-in `httpx` streaming implementation)
- **Impact:** Enables real-time data streams
- **Implementation:** `apilinker/core/connector.py`, `apilinker/connectors/general/sse.py`

#### Streaming Response Handling
- **Status:** Implemented (v0.6.0)
- **Priority:** Medium
- **Description:** Handle large streaming responses efficiently
- **Features:**
  - Chunked response processing
  - Memory-efficient streaming
  - Progress tracking for large downloads
  - Resume interrupted streams
- **Dependencies:** None (httpx supports streaming)
- **Impact:** Improves memory efficiency for large datasets
- **Implementation:** `apilinker/core/connector.py`, `apilinker/api_linker.py`

---

## Version 0.7.0 - Advanced Data Processing
**Focus:** Enhanced data transformation, validation, and multi-source operations

### High Priority

#### Multi-Source Aggregation
- **Status:** Implemented (v0.7.0)
- **Priority:** High
- **Description:** Combine data from multiple sources
- **Features:**
  - Join operations (inner, left, right, outer)
  - Data merging strategies
  - Conflict resolution policies
  - Multi-source mapping configuration
  - Parallel source fetching
- **Dependencies:** None (built-in)
- **Impact:** Enables complex data integration scenarios
- **Implementation:** `apilinker/core/aggregation.py`, `apilinker/api_linker.py`

#### Enhanced Incremental Sync
- **Status:** Planned
- **Priority:** High
- **Description:** Advanced change detection and delta sync
- **Features:**
  - Change data capture (CDC) patterns
  - Delta sync with timestamps/versions
  - Conflict resolution strategies
  - Change tracking and audit
  - Incremental sync optimization
- **Dependencies:** None (extends existing state store)
- **Impact:** Improves efficiency for large datasets

### Medium Priority

#### Advanced Data Validation
- **Status:** Planned
- **Priority:** Medium
- **Description:** Enhanced validation capabilities
- **Features:**
  - Custom validation rules
  - Data quality scoring
  - Anomaly detection
  - Validation rule composition
  - Validation reporting
- **Dependencies:** `pandas` (optional, for data quality)
- **Impact:** Improves data reliability

#### Data Transformation Visual Editor (CLI-based)
- **Status:** Planned
- **Priority:** Medium
- **Description:** Interactive CLI tool for mapping configuration
- **Features:**
  - Interactive field mapping wizard
  - Transformation preview
  - Schema exploration
  - Configuration validation
- **Dependencies:** `rich` (already included)
- **Impact:** Improves developer experience

---

## Version 0.7.1 - Build, Packaging, and CI Stabilization
**Focus:** Deterministic CI and install correctness across supported Python versions

### High Priority

#### Packaging Source-of-Truth Consolidation
- **Status:** Planned
- **Priority:** High
- **Description:** Eliminate metadata/dependency drift between packaging files
- **Features:**
  - Make `pyproject.toml` the authoritative dependency source
  - Minimize or remove duplicate dependency definitions in `setup.py`
  - Ensure `pip install .` and `pip install -e ".[dev]"` resolve consistently
  - Add packaging smoke tests for sdist/wheel install in CI
- **Dependencies:** None (packaging/tooling refactor)
- **Impact:** Prevents install failures and version skew

#### CI Determinism and Flake Reduction
- **Status:** Planned
- **Priority:** High
- **Description:** Remove timing-sensitive and environment-sensitive failures
- **Features:**
  - Replace wall-clock timing assertions with deterministic mocks where possible
  - Run a repeat/failure-detection lane for flaky tests
  - Lock formatter/linter behavior across OS matrix
  - Add explicit failure triage labels for flaky vs regression failures
- **Dependencies:** None (CI workflow updates)
- **Impact:** Increases trust in CI signal and reduces release risk

---

## Version 0.7.2 - Runtime Reliability Hardening
**Focus:** Safer networking, clearer failures, and graceful runtime behavior

### High Priority

#### Explicit Timeout and HTTP Client Policy
- **Status:** Planned
- **Priority:** High
- **Description:** Ensure all outbound HTTP calls have bounded latency
- **Features:**
  - Enforce explicit timeouts for all direct `httpx` calls
  - Standardize client lifecycle and reuse/injection patterns
  - Add timeout-related integration tests for auth/monitoring/webhooks flows
- **Dependencies:** None (runtime hardening)
- **Impact:** Prevents hangs and improves production reliability

#### Error Semantics and Recovery Completion
- **Status:** Planned
- **Priority:** High
- **Description:** Make error handling explicit, observable, and complete
- **Features:**
  - Replace broad exception catch blocks with narrower categories where possible
  - Add structured logging context for swallowed/non-fatal exceptions
  - Implement fallback recovery strategy behavior in error handling
  - Complete `Retry-After` HTTP-date parsing in adaptive rate limiting
- **Dependencies:** None (core reliability refactor)
- **Impact:** Improves incident debugging and recovery behavior

### Medium Priority

#### Graceful Shutdown Responsiveness
- **Status:** Planned
- **Priority:** Medium
- **Description:** Improve stop latency for worker/scheduler loops
- **Features:**
  - Use interruptible sleep loops in long-running workers
  - Add shutdown-path tests for schedulers and message workers
  - Document operational stop semantics
- **Dependencies:** None (runtime loop improvements)
- **Impact:** Safer deployments and cleaner restarts

---

## Version 0.7.3 - Documentation and Metadata Integrity
**Focus:** Accurate docs, coherent tooling, and version consistency

### High Priority

#### Documentation Stack Unification
- **Status:** Planned
- **Priority:** High
- **Description:** Remove split-brain docs architecture and stale pages
- **Features:**
  - Choose a single canonical docs toolchain for published docs
  - Align docs URLs across README, project metadata, and guides
  - Remove or archive duplicate/stale doc trees
  - Add doc-link and snippet validation checks in CI
- **Dependencies:** None (docs/tooling consolidation)
- **Impact:** Reduces user confusion and onboarding errors

#### Version and Content Consistency Sweep
- **Status:** Planned
- **Priority:** High
- **Description:** Ensure examples, paper, and docs match current release state
- **Features:**
  - Update stale version strings and historical placeholder values
  - Fix encoding/mojibake artifacts in markdown docs
  - Validate research docs against actual connector behavior
- **Dependencies:** None (docs quality updates)
- **Impact:** Improves credibility and scientific usability

---

## Version 0.8.0 - GraphQL & Additional Protocols
**Focus:** Protocol expansion, API versioning, and connector contract hardening

### High Priority

#### GraphQL Support
- **Status:** Planned
- **Priority:** High
- **Description:** Native GraphQL connector
- **Features:**
  - GraphQL query builder
  - Schema introspection
  - GraphQL → REST mapping
  - GraphQL subscriptions support
  - Query optimization
- **Dependencies:** `gql` or `graphql-core`
- **Impact:** Expands protocol support

#### API Versioning Support
- **Status:** Planned
- **Priority:** Medium
- **Description:** Handle API version changes gracefully
- **Features:**
  - Version negotiation
  - Backward compatibility layer
  - Version migration tools
  - Version-aware configuration
  - Deprecation warnings
- **Dependencies:** None (built-in)
- **Impact:** Improves long-term maintainability

#### Unified Connector Contract
- **Status:** Planned
- **Priority:** High
- **Description:** Standardize behavioral guarantees across connectors
- **Features:**
  - Common semantics for retries, pagination, rate limit handling, and errors
  - Connector compliance test suite with reusable fixtures
  - Contract tests for sync and async connector parity
- **Dependencies:** None (built-in)
- **Impact:** Predictable integration behavior at scale

#### Scientific Connector Completion Pass
- **Status:** Planned
- **Priority:** High
- **Description:** Convert partial/conceptual behaviors into explicit capabilities
- **Features:**
  - Replace conceptual placeholder returns with production endpoints or explicit experimental flags
  - Define supported capability matrix per scientific connector
  - Add robust fallback modes that preserve provenance of partial results
- **Dependencies:** None (extends existing scientific connectors)
- **Impact:** Higher trust for research use cases

### Medium Priority

#### SOAP Support (Basic)
- **Status:** Planned
- **Priority:** Low
- **Description:** Basic SOAP/WSDL support for legacy systems
- **Features:**
  - WSDL parsing
  - SOAP request/response handling
  - Basic SOAP → REST mapping
- **Dependencies:** `zeep` or `suds-py3`
- **Impact:** Legacy system integration

---

## Version 0.9.0 - Developer Experience & Tooling
**Focus:** Testing, templates, developer productivity, and scientific reproducibility

### High Priority

#### Testing Framework
- **Status:** Planned
- **Priority:** High
- **Description:** Built-in testing utilities
- **Features:**
  - Mock API server
  - Integration test helpers
  - Test data generators
  - Configuration testing utilities
  - Test fixtures and factories
- **Dependencies:** `responses` or `httpx-mock`
- **Impact:** Improves code quality and reliability

#### Configuration Templates Library
- **Status:** Planned
- **Priority:** Medium
- **Description:** Pre-built configs for common APIs
- **Features:**
  - Template library (GitHub, GitLab, Salesforce, etc.)
  - Community-contributed templates
  - Template validation
  - Template marketplace/registry
  - Template versioning
- **Dependencies:** None (built-in)
- **Impact:** Accelerates onboarding

#### Reproducible Research Execution Model
- **Status:** Planned
- **Priority:** High
- **Description:** Make runs reproducible and auditable across environments
- **Features:**
  - Capture query fingerprints, connector version, and run metadata in provenance
  - Export reproducibility manifests with deterministic ordering/hashes
  - Add replay utilities for representative benchmark/research scenarios
- **Dependencies:** None (extends provenance and benchmark modules)
- **Impact:** Enables stronger scientific reproducibility claims

#### Data Quality and Validation Framework
- **Status:** Planned
- **Priority:** High
- **Description:** Move from basic schema checks to scientific data quality controls
- **Features:**
  - Connector-specific quality checks (identifier completeness, field consistency)
  - Configurable quality thresholds and fail/allow policies
  - Quality summaries in sync results and benchmark outputs
- **Dependencies:** None (extends validation and connector layers)
- **Impact:** Improves reliability of downstream scientific analysis

### Medium Priority

#### API Documentation Generator
- **Status:** Planned
- **Priority:** Medium
- **Description:** Auto-generate API documentation from configs
- **Features:**
  - OpenAPI/Swagger generation
  - Interactive API explorer
  - Documentation from configurations
  - API contract generation
- **Dependencies:** `openapi-core` or similar
- **Impact:** Improves documentation quality

#### Enhanced CLI Tools
- **Status:** Planned
- **Priority:** Medium
- **Description:** Additional CLI utilities
- **Features:**
  - Interactive configuration wizard
  - Configuration diff tool
  - Migration assistant
  - Performance profiler
- **Dependencies:** `rich` (already included)
- **Impact:** Improves developer experience

---

## Version 1.0.0 - Production Ready
**Focus:** Stability, performance, enterprise features, and production guarantees

### High Priority

#### Performance Optimization
- **Status:** Planned
- **Priority:** High
- **Description:** Advanced performance features
- **Features:**
  - Enhanced connection pooling
  - Request deduplication
  - Smart retry strategies
  - Caching layer improvements
  - Performance profiling tools
- **Dependencies:** None (built-in optimizations)
- **Impact:** Critical for production scale

#### Data Caching Layer
- **Status:** Planned
- **Priority:** High
- **Description:** Intelligent caching system
- **Features:**
  - Response caching
  - Cache invalidation strategies
  - Redis/Memcached integration
  - Cache warming
  - Cache statistics
- **Dependencies:** `redis`, `pymemcache` (optional)
- **Impact:** Improves performance and reduces API calls

#### Workflow Orchestration
- **Status:** Planned
- **Priority:** High
- **Description:** Complex multi-step workflows
- **Features:**
  - Conditional branching
  - Parallel execution
  - Workflow templates
  - Workflow visualization
  - Error handling in workflows
- **Dependencies:** None (built-in)
- **Impact:** Enables complex integration scenarios

#### Stability and Compatibility Policy
- **Status:** Planned
- **Priority:** High
- **Description:** Define what is stable and how changes are managed
- **Features:**
  - Public API compatibility contract and deprecation policy
  - Migration guide from pre-1.0 releases
  - SemVer enforcement in release process and changelog rules
- **Dependencies:** None (process and policy)
- **Impact:** Safe adoption for long-lived production systems

#### Security and Supply Chain Baseline
- **Status:** Planned
- **Priority:** High
- **Description:** Establish minimum security posture for production deployments
- **Features:**
  - Dependency vulnerability scanning and reporting in CI
  - Secret redaction policy for logs/error paths
  - Signed release artifacts and provenance metadata
  - Hardened verification paths for webhook/JWT/auth flows
- **Dependencies:** `pip-audit`/security tooling (CI)
- **Impact:** Reduces operational and compliance risk

### Medium Priority

#### Multi-Tenant Support
- **Status:** Planned
- **Priority:** Medium
- **Description:** Support for multiple tenants
- **Features:**
  - Tenant isolation
  - Per-tenant configurations
  - Resource quotas
  - Tenant-specific logging
- **Dependencies:** None (built-in)
- **Impact:** Enables SaaS deployments

#### Backup and Restore
- **Status:** Planned
- **Priority:** Medium
- **Description:** Configuration and state management
- **Features:**
  - Config versioning
  - State snapshots
  - Disaster recovery
  - Backup automation
- **Dependencies:** None (built-in)
- **Impact:** Improves reliability

#### Compliance and Governance
- **Status:** Planned
- **Priority:** Medium
- **Description:** Enterprise compliance features
- **Features:**
  - Enhanced audit logging
  - Data retention policies
  - GDPR/privacy compliance tools
  - Compliance reporting
- **Dependencies:** None (built-in)
- **Impact:** Essential for regulated industries

#### Additional Data Export Formats
- **Status:** Planned
- **Priority:** Medium
- **Description:** More output format options
- **Features:**
  - CSV/Excel export
  - Parquet/Arrow support
  - Database direct writes (PostgreSQL, MySQL, etc.)
  - Format-specific optimizations
- **Dependencies:** `pandas`, `pyarrow`, `sqlalchemy`
- **Impact:** Expands use cases

#### Coverage and Reliability Gate Raise
- **Status:** Planned
- **Priority:** Medium
- **Description:** Increase confidence in previously under-tested modules
- **Features:**
  - Expand tests for optional modules through extras-enabled CI lanes
  - Reduce coverage omit list for core production code
  - Add long-run soak tests for streaming and queue workers
- **Dependencies:** None (test/CI infrastructure)
- **Impact:** Stronger production confidence before GA

---

## Version 1.1.0 - Scientific Interoperability
**Focus:** Scientific ecosystem integration beyond baseline reproducibility

### Medium Priority

#### Interoperable Scientific Export
- **Status:** Planned
- **Priority:** Medium
- **Description:** Improve portability into research toolchains
- **Features:**
  - Structured exports for citation and metadata pipelines
  - Improved schema mapping templates for literature/compound/researcher data
  - End-to-end examples for reproducible multi-database studies
- **Dependencies:** None (extends existing export/mapping capabilities)
- **Impact:** Better adoption in real research workflows

---

## Version 2.0.0 - Architecture Simplification
**Focus:** Breaking cleanup for long-term maintainability and scale

### High Priority

#### API and Module Simplification
- **Status:** Planned
- **Priority:** High
- **Description:** Remove legacy surfaces and normalize extension points
- **Features:**
  - Remove deprecated APIs accumulated through 0.x/1.x
  - Unify sync/async connector abstractions where they diverge
  - Stabilize plugin lifecycle contracts and versioned plugin API
  - Rework internal module boundaries for lower coupling
- **Dependencies:** None (core refactor)
- **Impact:** Lower maintenance cost and clearer long-term evolution

---

## Future Considerations (Beyond 2.0)

### Web Dashboard/UI
- **Status:** Future
- **Priority:** Low
- **Description:** Web-based management interface
- **Features:**
  - Configuration editor
  - Sync monitoring dashboard
  - Error visualization
  - Performance metrics visualization
  - Real-time sync status
- **Dependencies:** `fastapi`, `react` or similar frontend
- **Impact:** Improves usability for non-technical users
- **Note:** May be a separate project or optional component

### Machine Learning Integration
- **Status:** Future
- **Priority:** Low
- **Description:** ML-powered features
- **Features:**
  - Automatic schema inference
  - Intelligent field mapping suggestions
  - Anomaly detection
  - Predictive error handling
- **Dependencies:** `scikit-learn` or similar (optional)
- **Impact:** Advanced automation

---

## Feature Status Legend

- ⭐ **High Priority** - Critical for roadmap goals
- **Planned** - Feature is planned but not started
- **In Progress** - Feature is currently being developed
- **Beta** - Feature is in beta testing
- **Released** - Feature is available in a released version

## Contributing

If you'd like to contribute to any of these features, please:
1. Check existing issues on GitHub
2. Open a new issue to discuss the feature
3. Follow the contributing guidelines in `CONTRIBUTING.md`

## Version History

- **0.5.0** - Observability & Enterprise Security
- **0.6.0** - Event-Driven Architecture
- **0.7.0** - Advanced Data Processing
- **0.7.1** - Build, Packaging, and CI Stabilization
- **0.7.2** - Runtime Reliability Hardening
- **0.7.3** - Documentation and Metadata Integrity
- **0.8.0** - GraphQL & Additional Protocols
- **0.9.0** - Developer Experience & Tooling
- **1.0.0** - Production Ready
- **1.1.0** - Scientific Interoperability
- **2.0.0** - Architecture Simplification

---

**Note:** This roadmap is subject to change based on community feedback, technical constraints, and project priorities.
