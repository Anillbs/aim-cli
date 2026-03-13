"""Auth API calls."""

from __future__ import annotations

from typing import Any

from aim_cli.api import endpoints
from aim_cli.api.client import request


def me(api_key: str | None = None) -> dict[str, Any]:
    """GET /api/user — current user profile."""
    resp = request("GET", endpoints.AUTH_ME, api_key=api_key)
    return resp.json()  # type: ignore[no-any-return]
