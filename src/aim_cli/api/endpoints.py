"""API endpoint URL constants and path builders.

All API paths are centralized here — single point of change when API
versions evolve.  These map to the actual AIM Security Laravel API.
"""

from __future__ import annotations

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_LOGIN = "/api/login"
AUTH_ME = "/api/user"

# ── Sites ─────────────────────────────────────────────────────────────────────
SITES_LIST = "/api/sites"
SITES_ADD = "/api/sites"
SITES_DETAIL = "/api/sites/{site_id}"
SITES_DELETE = "/api/sites/{site_id}"
SITES_HISTORY = "/api/sites/{site_id}/history"

# ── Domain Verification ──────────────────────────────────────────────────────
DOMAINS_LIST = "/api/domains"
DOMAINS_ADD = "/api/domains"
DOMAINS_VERIFY = "/api/domains/{domain_id}/verify"

# ── Scans (CI/CD v1 endpoints — support both session & token auth) ────────────
SCANS_TRIGGER = "/api/v1/scans/trigger"
SCANS_STATUS = "/api/v1/scans/{scan_id}/status"
SCANS_EXPORT = "/api/v1/scans/{scan_id}/export"

# ── Scans (dashboard endpoints) ──────────────────────────────────────────────
SCAN_START = "/api/scan"
SCAN_STATUS_LEGACY = "/api/scan/{scan_id}/status"

# ── Vulnerabilities ──────────────────────────────────────────────────────────
VULNS_LIST = "/api/vulnerabilities"
VULNS_DETAIL = "/api/vulnerabilities/{vuln_id}"
VULNS_UPDATE = "/api/vulnerabilities/{vuln_id}"
VULNS_EVIDENCE = "/api/vulnerabilities/{vuln_id}/evidence"
VULNS_CURL = "/api/vulnerabilities/{vuln_id}/curl"

# ── Reports ───────────────────────────────────────────────────────────────────
REPORTS_LIST = "/api/reports"
REPORTS_GENERATE = "/api/reports"
REPORTS_SHOW = "/api/reports/{report_id}"
REPORTS_DOWNLOAD = "/api/reports/{report_id}/download"

# ── Tokens ────────────────────────────────────────────────────────────────────
TOKENS_LIST = "/api/tokens"
TOKENS_CREATE = "/api/tokens"
TOKENS_REVOKE = "/api/tokens/{token_id}"

# ── Subscription ──────────────────────────────────────────────────────────────
SUBSCRIPTION_SHOW = "/api/v1/subscription"

# ── Dashboard ─────────────────────────────────────────────────────────────────
DASHBOARD_STATS = "/api/dashboard/stats"


def build(template: str, **kwargs: object) -> str:
    """Build a URL path from a template and keyword arguments."""
    return template.format(**kwargs)
