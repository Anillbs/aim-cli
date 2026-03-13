"""Vulnerabilities API calls."""

from __future__ import annotations

from typing import Any

from aim_cli.api import endpoints
from aim_cli.api.client import request


def list_vulns(
    *,
    scan_id: int | None = None,
    site_id: int | None = None,
    severity: str | None = None,
    status: str | None = None,
    limit: int = 50,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """GET /api/vulnerabilities — list vulnerabilities with filters."""
    params: dict[str, Any] = {"limit": limit}
    if scan_id:
        params["scan_id"] = scan_id
    if site_id:
        params["site_id"] = site_id
    if severity:
        params["severity"] = severity
    if status:
        params["status"] = status

    resp = request("GET", endpoints.VULNS_LIST, params=params, api_key=api_key)
    data = resp.json()
    return data if isinstance(data, list) else data.get("data", [])


def show_vuln(vuln_id: int, *, api_key: str | None = None) -> dict[str, Any]:
    """GET /api/vulnerabilities/{id} — vulnerability detail."""
    path = endpoints.build(endpoints.VULNS_DETAIL, vuln_id=vuln_id)
    resp = request("GET", path, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]


def get_evidence(vuln_id: int, *, api_key: str | None = None) -> list[dict[str, Any]]:
    """GET /api/vulnerabilities/{id}/evidence — evidence list."""
    path = endpoints.build(endpoints.VULNS_EVIDENCE, vuln_id=vuln_id)
    resp = request("GET", path, api_key=api_key)
    data = resp.json()
    return data if isinstance(data, list) else data.get("data", [])


def get_curl(vuln_id: int, *, api_key: str | None = None) -> str:
    """GET /api/vulnerabilities/{id}/curl — cURL reproduction command."""
    path = endpoints.build(endpoints.VULNS_CURL, vuln_id=vuln_id)
    resp = request("GET", path, api_key=api_key)
    content_type = resp.headers.get("content-type", "")
    if "text/plain" in content_type:
        return resp.text
    return resp.json().get("curl", resp.text)
