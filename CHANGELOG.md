# Changelog

All notable changes to AIM CLI will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-03-12

### Added
- Initial release
- `aim auth login/logout/whoami/status` — Token-based authentication
- `aim scan start/status/list` — Scan management with `--wait` polling
- `aim sites add/list/remove/verify` — Site/domain management
- `aim vulns list/show/export` — Vulnerability results with SARIF/JSON/CSV
- `aim reports generate/download/list` — Report management
- `aim config set/get/reset/show` — TOML-based configuration
- `aim doctor` — Environment diagnostics
- OS Keyring token storage (Windows Credential Locker, macOS Keychain, Linux libsecret)
- CI/CD quality gate (`--fail-on critical|high|medium|low`)
- Rich terminal UI with colored tables, spinners, progress bars
- Proxy and custom CA certificate support
