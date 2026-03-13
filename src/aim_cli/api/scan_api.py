"""Scan API calls."""

from __future__ import annotations

from typing import Any

from aim_cli.api import endpoints
from aim_cli.api.client import request


def trigger(
    *,
    site_id: int | None = None,
    domain: str | None = None,
    profile: str = "standard",
    api_key: str | None = None,
) -> dict[str, Any]:
    """POST /api/v1/scans/trigger — start a new scan."""
    body: dict[str, Any] = {}
    if site_id is not None:
        body["site_id"] = site_id
    if domain:
        body["domain"] = domain
    body["scan_profile"] = profile

    resp = request("POST", endpoints.SCANS_TRIGGER, json=body, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]


def status(scan_id: int, *, api_key: str | None = None) -> dict[str, Any]:
    """GET /api/v1/scans/{id}/status — poll scan progress."""
    path = endpoints.build(endpoints.SCANS_STATUS, scan_id=scan_id)
    resp = request("GET", path, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]


def export(
    scan_id: int,
    fmt: str = "sarif",
    *,
    api_key: str | None = None,
) -> bytes:
    """GET /api/v1/scans/{id}/export?format=... — download report."""
    path = endpoints.build(endpoints.SCANS_EXPORT, scan_id=scan_id)
    resp = request("GET", path, params={"format": fmt}, api_key=api_key)
    return resp.content


def list_scans(
    *,
    site_id: int | None = None,
    limit: int = 20,
    api_key: str | None = None,
) -> dict[str, Any]:
    """GET /api/sites/{id}/history — scan history for a site."""
    if site_id:
        path = endpoints.build(endpoints.SITES_HISTORY, site_id=site_id)
    else:
        path = endpoints.DASHBOARD_STATS
    resp = request("GET", path, params={"limit": limit}, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]
