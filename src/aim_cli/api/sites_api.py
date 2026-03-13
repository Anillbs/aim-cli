"""Sites API calls."""

from __future__ import annotations

from typing import Any

from aim_cli.api import endpoints
from aim_cli.api.client import request


def list_sites(*, api_key: str | None = None) -> list[dict[str, Any]]:
    """GET /api/sites — list all sites."""
    resp = request("GET", endpoints.SITES_LIST, api_key=api_key)
    data = resp.json()
    return data if isinstance(data, list) else data.get("data", data.get("sites", []))


def add_site(
    url: str,
    *,
    name: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """POST /api/sites — add a new site."""
    body: dict[str, Any] = {"url": url}
    if name:
        body["name"] = name
    resp = request("POST", endpoints.SITES_ADD, json=body, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]


def remove_site(site_id: int, *, api_key: str | None = None) -> dict[str, Any]:
    """DELETE /api/sites/{id} — remove a site."""
    path = endpoints.build(endpoints.SITES_DELETE, site_id=site_id)
    resp = request("DELETE", path, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]


def verify_site(domain_id: int, *, api_key: str | None = None) -> dict[str, Any]:
    """POST /api/domains/{id}/verify — trigger domain verification."""
    path = endpoints.build(endpoints.DOMAINS_VERIFY, domain_id=domain_id)
    resp = request("POST", path, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]
