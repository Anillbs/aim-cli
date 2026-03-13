"""Shared test fixtures for AIM CLI tests."""

from __future__ import annotations

import pytest
import respx
import httpx


@pytest.fixture
def mock_api():
    """HTTPX mock router — use with respx to mock API calls."""
    with respx.mock(base_url="https://api.aimsecurity.io") as router:
        yield router


@pytest.fixture
def sample_user():
    """Sample user response from GET /api/user."""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "tenant_id": 10,
        "tenant_role": "owner",
        "role_display": "Owner",
        "permissions": ["manage_team", "view_evidence", "export_evidence"],
        "is_owner": True,
        "onboarding_completed": True,
    }


@pytest.fixture
def sample_scan_status():
    """Sample scan status response from GET /api/v1/scans/{id}/status."""
    return {
        "scan_id": 42,
        "status": "completed",
        "progress": 100,
        "progress_step": "completed",
        "score": 85,
        "domain": "example.com",
        "created_at": "2026-03-12T10:00:00+00:00",
        "updated_at": "2026-03-12T10:05:00+00:00",
        "completed": True,
        "source": "mysql",
        "summary": {
            "score": 85,
            "total_vulns": 5,
            "vulnerabilities": {"critical": 0, "high": 1, "medium": 2, "low": 2},
            "passed": True,
        },
    }


@pytest.fixture
def sample_vulns():
    """Sample vulnerability list."""
    return [
        {
            "id": 91,
            "vuln_type": "SQL Injection",
            "severity": "critical",
            "url": "https://example.com/api/search?q=",
            "status": "open",
            "details": {"owasp_id": "A03:2021", "cvss": 9.8},
        },
        {
            "id": 92,
            "vuln_type": "Stored XSS",
            "severity": "high",
            "url": "https://example.com/comments",
            "status": "open",
            "details": {"owasp_id": "A03:2021", "cvss": 7.1},
        },
    ]


@pytest.fixture
def sample_sites():
    """Sample site list."""
    return [
        {
            "id": 1,
            "name": "Production",
            "domain": "example.com",
            "url": "https://example.com",
            "last_score": 85,
            "status": "active",
        },
    ]
