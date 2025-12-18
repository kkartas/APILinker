# Changelog

## [0.4.0] - 2025-07-16

### Added
- JSON Schema validation for responses/requests with optional strict mode and readable diffs
- Schema probing CLI (`apilinker probe-schema`) to infer minimal schemas and mapping templates
- Provenance & audit: run metadata (config hash, git SHA, timings, events) to JSONL and sidecar JSON
- Idempotency support with stable keys and in-memory de-duplication
- State & resumability: file/SQLite stores; auto-inject `updated_since`; `apilinker state` CLI

### Changed
- Bump version to 0.4.0 across codebase and docs

## [0.3.0] - 2025-01-28

- Updated version to 0.3.0
- Added 8 research connectors for scientific workflows
- Comprehensive documentation enhancement and consolidation
- Enhanced authentication system with multiple methods
- Improved error handling and testing coverage
- GitHub URL updates to correct username (kkartas)
- Added local benchmarks suite under `benchmarks/` with mock server and harness; docs in `docs/benchmarks.md`

## [0.2.0] - 2025-07-16

### Added
- Robust error handling and recovery system:
  - Circuit breaker pattern to prevent cascading failures
  - Dead Letter Queue (DLQ) for storing and retrying failed operations
  - Configurable recovery strategies based on error types
  - Error analytics and monitoring
- Enhanced error categorization and context tracking
- Integration with existing retry mechanisms
- Advanced security features:
  - Secure credential storage (optional)
  - Removed custom request/response encryption in favor of HTTPS-only usage guidance
  - Fine-grained access control for multi-user environments
  - Additional OAuth flows: PKCE and Device Flow
- Added cryptography dependency for enhanced security features

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-14

### Added
- Initial release of ApiLinker
- Core components:
  - API Connector for REST APIs
  - Field Mapper with transform capabilities
  - Authentication manager (API Key, Bearer, Basic, OAuth2)
  - Scheduler for recurring syncs
  - Plugin system for extensibility
- Command line interface
- YAML configuration support
- Environment variable resolution
- Documentation
- Test suite
- JOSS paper draft

## [Unreleased]

See [ROADMAP.md](ROADMAP.md) for planned features and version roadmap.

### Added
- Message queue connector plugins (RabbitMQ, Redis Pub/Sub, AWS SQS, Kafka) and a dependency-free message routing/transformation pipeline

### Changed
- See ROADMAP.md for planned changes

### Fixed
- Bug fixes will be documented here as they are addressed
