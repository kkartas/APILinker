# Changelog

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
  - Secure credential storage with encryption-at-rest
  - Request/response encryption options
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

### Added
- Placeholder for future additions

### Changed
- Placeholder for future changes

### Fixed
- Placeholder for future fixes
