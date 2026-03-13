"""Reports API calls."""

from __future__ import annotations

from typing import Any

from aim_cli.api import endpoints
from aim_cli.api.client import request


def list_reports(*, api_key: str | None = None) -> list[dict[str, Any]]:
    """GET /api/reports — list available reports."""
    resp = request("GET", endpoints.REPORTS_LIST, api_key=api_key)
    data = resp.json()
    return data if isinstance(data, list) else data.get("data", [])


def generate(
    scan_id: int,
    *,
    template: str = "technical",
    api_key: str | None = None,
) -> dict[str, Any]:
    """POST /api/reports — trigger report generation."""
    resp = request(
        "POST",
        endpoints.REPORTS_GENERATE,
        json={"scan_id": scan_id, "template": template},
        api_key=api_key,
    )
    return resp.json()  # type: ignore[no-any-return]


def download(report_id: int, *, api_key: str | None = None) -> bytes:
    """GET /api/reports/{id}/download — download report file."""
    path = endpoints.build(endpoints.REPORTS_DOWNLOAD, report_id=report_id)
    resp = request("GET", path, api_key=api_key)
    return resp.content
