# Production Readiness Fix Plan (APILinker)

This document consolidates the fixes and improvements needed to bring this repository closer to a **state-of-the-art, production-grade open source Python library**.

## Scope / method

- This list is based on a repository scan focusing on:
  - packaging/metadata (`pyproject.toml`, `setup.py`, `requirements.txt`)
  - CI workflows (`.github/workflows/*`)
  - a set of core runtime modules (`apilinker/core/*`) and README/doc entry points
- It is **not a formal security audit** and does not replace SAST/DAST, dependency scanning, or pentesting.

## How to use this doc

- Treat each section as an issue/PR checklist.
- The recommended approach is to do this in **small PRs** in the order in the “PR plan” section.

---

# 0) Executive summary (highest-impact problems)

## Critical

1. **Dependency conflict**: `pydantic` requirement differs between `pyproject.toml` (v2) and `requirements.txt` (v1). This can cause runtime breaks depending on install method.
2. **Packaging duplication**: project metadata and dependencies are duplicated across `pyproject.toml` and `setup.py`, increasing drift risk.
3. **Docs split-brain**: repo contains both MkDocs and Sphinx configurations; deployment uses MkDocs, while `requirements.txt` includes Sphinx. This creates confusion, heavier installs, and likely stale docs.

## High

4. **HTTP calls without explicit timeouts** in core modules (risk of hangs).
5. **Broad exception handling** in many modules; some failures are swallowed or lose context.

---

# 1) Packaging, dependency management, and distribution

## 1.1 Make `pyproject.toml` the single source of truth

- **Problem**: `setup.py` duplicates project metadata and dependencies.
- **Fix**:
  - Preferred: remove `setup.py` entirely and rely on `pyproject.toml`/setuptools build backend.
  - If you must keep it: convert `setup.py` into a minimal shim that reads metadata from `pyproject.toml` (do not duplicate deps).

### Acceptance criteria

- `pip install .` and `python -m build` produce the same metadata regardless of install method.
- Only one file defines dependencies and versioning for distribution.

## 1.2 Fix dependency inconsistencies

- **Problem**: `requirements.txt` conflicts with `pyproject.toml` (`pydantic>=1.10.2` vs `pydantic>=2.0.0`).
- **Fix**:
  - Decide on one:
    - If the codebase uses Pydantic v2 (you already use `ConfigDict`), align everything to `pydantic>=2`.
    - Otherwise, downgrade code usage to v1 and pin `pydantic<2`.
  - Update `requirements.txt` accordingly or remove it entirely.

### Recommendation

- Prefer **Pydantic v2** and remove `requirements.txt` (or make it a thin developer convenience that delegates to extras).

## 1.3 Clarify optional dependency groups

- **Problem**: optional feature groups exist (`mq`, `webhooks`, `docs`) but `requirements.txt` includes optional stacks (Sphinx + OpenTelemetry + cloud SDKs + MQ libs), which is heavy and confusing.
- **Fix**:
  - Ensure all optional dependencies live under `project.optional-dependencies`.
  - Avoid a root-level requirements file that installs *everything*.

## 1.4 Version management consistency

- **Observation**: version is managed across multiple files via `.bumpversion.toml`.
- **Fix**:
  - Keep `.bumpversion.toml` as authoritative for “where version exists”, but ensure:
    - docs don’t hardcode old versions in narrative text
    - URL casing and canonical name are consistent

---

# 2) Documentation system cleanup

## 2.1 Pick one docs toolchain (MkDocs or Sphinx)

- **Problem**: MkDocs is deployed (`mkdocs gh-deploy`) while a full Sphinx setup also exists.
- **Fix options**:
  - **Option A (recommended)**: Keep MkDocs only.
    - Remove Sphinx from default requirements.
    - Either delete `docs/sphinx_setup/` or clearly mark it deprecated.
  - **Option B**: Keep Sphinx only.
    - Remove MkDocs workflow and `mkdocs.yml`.

### Acceptance criteria

- There is exactly one official docs build pipeline.
- `pyproject.toml` “Documentation” URL points to the actual deployed docs.

## 2.2 Align documentation URLs and naming

- **Problem**: documentation URL differs between `pyproject.toml` (ReadTheDocs) and README (GitHub Pages).
- **Fix**:
  - Choose the canonical docs URL and use it everywhere:
    - `pyproject.toml`
    - README
    - CITATION.cff (if needed)

## 2.3 Remove/avoid committing built artifacts

- **Problem**: built docs directories (`site/`, `_build/`) should not be tracked.
- **Fix**:
  - Ensure these directories are not committed.
  - Keep `.gitignore` entries for them.

## 2.4 README “production usage” guidance

- **Problem**: current README shows a minimal worker loop but lacks production guidance.
- **Fix**:
  - Add a “Production notes” section:
    - graceful shutdown (SIGTERM handling)
    - configuring log level/format
    - DLQ location and retention
    - recommended broker-native DLQ features (RabbitMQ DLX, SQS redrive, Kafka DLT)

---

# 3) Networking, reliability, and runtime safety

## 3.1 Add explicit timeouts to every outbound request

### Issues found

- `apilinker/core/auth.py`: uses `httpx.post(...)` without explicit `timeout=`.
- `apilinker/core/monitoring.py`: uses `httpx.Client()` without configured timeouts.

### Fix

- Introduce a shared, configurable default timeout (e.g., via config or constants).
- Ensure every call uses one of:
  - `httpx.Client(timeout=...)`
  - `httpx.post(..., timeout=...)`

### Acceptance criteria

- No `httpx.*` call occurs without explicit timeout.

## 3.2 Standardize HTTP client lifecycle

- **Problem**: modules create new `httpx.Client()` inside methods (monitoring) and direct module-level calls (`httpx.post`).
- **Fix**:
  - Use reusable clients where appropriate.
  - Allow injecting a client/session in integrations (PagerDuty/Slack) to facilitate testing and resource reuse.

## 3.3 Stop swallowing exceptions without observability

### Issues found

- Broad catches (`except Exception`) appear in many core modules.
- Some code paths explicitly `pass` on errors (e.g., best-effort provenance writes, router predicate failures, JSON parsing fallback).

### Fix

- Replace broad catches with narrower ones where possible.
- Where broad catches are needed:
  - log with `exc_info=True`
  - include structured context (operation type, endpoint, message_id)
  - define the policy: retry / DLQ / fail-fast

## 3.4 Improve `message_queue.py` semantics

### Items

- Protocol method stubs should use `...` instead of `pass`.
- `JsonMessageSerializer.loads` should not silently coerce invalid JSON to string without at least debug logging.
- `MessageRouter.route` should log when predicates raise exceptions (currently it silently continues).
- `MessageWorker.run` uses `time.sleep(...)` which cannot be interrupted until sleep ends.

### Recommended fixes

- Change Protocol stubs to `...`.
- Add debug logs for JSON decode failures and predicate exceptions.
- Consider implementing an interruptible sleep helper (sleep in small increments and check `stop_event`).

---

# 4) Security hardening

## 4.1 JWT verification correctness

- **Observation**: `JWTVerifier.verify` uses `jwt.decode(..., options={"verify_signature": True})`.
- **Risk**: issuer/audience handling is defined but not clearly enforced via standard PyJWT parameters (this may be correct or may be incomplete depending on PyJWT version).
- **Fix**:
  - Ensure verification includes:
    - issuer (`issuer=`) when configured
    - audience (`audience=`) when configured
    - algorithm allowlist is enforced
    - expiration/nbf validation behavior is explicit (defaults may vary)

## 4.2 Secret handling expectations

- **Observation**: secret management module is extensive.
- **Fixes / checks**:
  - Ensure no secrets are ever logged.
  - Consider adding redaction utilities for logs.
  - Ensure environment-variable fallback does not inadvertently encourage storing secrets in plaintext files.

## 4.3 Add automated security scanning

- Add CI steps/tools (choose based on your preferences):
  - `pip-audit` (dependency vulnerabilities)
  - `bandit` (basic static checks)
  - GitHub Dependabot configuration

---

# 5) CI, testing, and quality gates

## 5.1 CI improvements

- **Current**: black, flake8, mypy, pytest with coverage threshold.

### Recommended changes

- Add:
  - dependency vulnerability scan (`pip-audit`)
  - `ruff` (optional) as a faster linter (if you want to modernize)
  - build/test of sdist/wheel install to ensure packaging works

## 5.2 Coverage configuration

- **Observation**: coverage omits many modules (security, scheduler, async connector, secrets, observability, webhooks).
- **Risk**: you may ship untested core behavior.
- **Fix**:
  - Reduce omit list over time.
  - If modules are truly optional, split them behind extras and conditionally test them.

## 5.3 Add “smoke tests” for docs/examples

- Ensure README snippets and key examples execute.
- Suggested approach:
  - doctest-style tests for README code blocks (or curated snippets)
  - minimal integration tests for message queue pipeline with dummy connectors (already present)

---

# 6) Repository hygiene

## 6.1 Clean up root-level ignored markdown files

- **Problem**: `.gitignore` lists multiple root markdown files suggesting internal/review artifacts.
- **Fix**:
  - Either:
    - move them into `docs/developer-guide/` and track them, or
    - delete them and stop generating them.

## 6.2 Generated build outputs

- Ensure `build/`, `dist/`, `site/`, and Sphinx build outputs are not tracked.

---

# 7) Recommended PR plan (small, safe increments)

## PR 1 — Dependency and packaging correctness (Critical)

- Fix `pydantic` mismatch.
- Decide the fate of `requirements.txt`.
- Ensure `pyproject.toml` is authoritative.

## PR 2 — Docs consolidation (Critical/High)

- Choose MkDocs vs Sphinx.
- Align documentation URLs.
- Remove stale configs/artifacts.

## PR 3 — HTTP timeouts and client policy (High)

- Add explicit timeouts everywhere.
- Add reusable clients / injection points for monitoring integrations.

## PR 4 — Error handling and observability (High)

- Replace broad exception catches where possible.
- Add structured logging in critical swallow points.

## PR 5 — Message queue hardening (Medium)

- Protocol stubs `...`.
- Logging for router predicate exceptions and serializer decode errors.
- Interruptible sleeps for graceful shutdown.

## PR 6 — Security tooling (Medium)

- Add `pip-audit` and optionally `bandit`.
- Add Dependabot config.

---

# 8) Open questions (decisions required)

1. **Docs**: do you want to officially support MkDocs or Sphinx?
2. **Pydantic**: commit to v2 everywhere, or downgrade to v1?
3. **Public API stability**: which modules/classes are considered stable and supported (e.g. message queue connectors)?

---

# 9) Tracking checklist (copy/paste into GitHub issues)

## Critical

- [ ] Resolve `pydantic` version conflict across installation methods
- [ ] Remove duplicated packaging metadata (`setup.py` vs `pyproject.toml`)
- [ ] Consolidate docs pipeline (MkDocs vs Sphinx) and remove the other

## High

- [ ] Add explicit `httpx` timeouts everywhere
- [ ] Introduce consistent error handling policy (retry/DLQ/fail-fast) and logging

## Medium

- [ ] Improve `message_queue.py` observability (router/serializer)
- [ ] Improve graceful shutdown responsiveness in `MessageWorker`

## Medium/Low

- [ ] Changelog ordering and conventions
- [ ] Align project naming/URLs across docs and metadata
- [ ] Add security scanning in CI
