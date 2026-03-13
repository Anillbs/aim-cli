"""Tests for api/client.py — HTTPX client factory and request handling."""

from __future__ import annotations

import pytest
import respx
import httpx

from aim_cli.core.errors import (
    AuthenticationError,
    ConnectionFailedError,
    ForbiddenError,
    NotFoundError,
    ServerError,
    ValidationError,
)


@pytest.fixture
def patched_client(monkeypatch, tmp_path):
    """Patch config and credentials so client can be built."""
    monkeypatch.setenv("AIM_API_KEY", "test-token-12345678")
    monkeypatch.setattr("aim_cli.core.config._config_dir", lambda: tmp_path)
    # Set default config values
    monkeypatch.setattr(
        "aim_cli.api.client.load_config",
        lambda: {
            "api_url": "https://api.aimsecurity.io",
            "timeout": 30,
            "proxy": "",
            "ca_bundle": "",
        },
    )


def test_request_success(patched_client):
    """Successful request returns response."""
    from aim_cli.api.client import request

    with respx.mock(base_url="https://api.aimsecurity.io") as router:
        router.get("/api/user").mock(
            return_value=httpx.Response(200, json={"id": 1, "name": "Test"})
        )
        resp = request("GET", "/api/user")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test"


def test_request_401_raises_auth_error(patched_client):
    """401 responses should raise AuthenticationError."""
    from aim_cli.api.client import request

    with respx.mock(base_url="https://api.aimsecurity.io") as router:
        router.get("/api/user").mock(
            return_value=httpx.Response(401, json={"message": "Unauthenticated."})
        )
        with pytest.raises(AuthenticationError):
            request("GET", "/api/user")


def test_request_403_raises_forbidden(patched_client):
    """403 responses should raise ForbiddenError."""
    from aim_cli.api.client import request

    with respx.mock(base_url="https://api.aimsecurity.io") as router:
        router.get("/api/sites").mock(
            return_value=httpx.Response(403, json={"message": "Forbidden."})
        )
        with pytest.raises(ForbiddenError):
            request("GET", "/api/sites")


def test_request_404_raises_not_found(patched_client):
    """404 responses should raise NotFoundError."""
    from aim_cli.api.client import request

    with respx.mock(base_url="https://api.aimsecurity.io") as router:
        router.get("/api/scans/999/status").mock(
            return_value=httpx.Response(404, json={"message": "Scan not found."})
        )
        with pytest.raises(NotFoundError):
            request("GET", "/api/scans/999/status")


def test_request_422_raises_validation(patched_client):
    """422 responses should raise ValidationError."""
    from aim_cli.api.client import request

    with respx.mock(base_url="https://api.aimsecurity.io") as router:
        router.post("/api/sites").mock(
            return_value=httpx.Response(422, json={"message": "URL is required."})
        )
        with pytest.raises(ValidationError):
            request("POST", "/api/sites", json={"url": ""})


def test_request_500_raises_server_error(patched_client):
    """Non-retryable 5xx responses should raise ServerError."""
    from aim_cli.api.client import request

    with respx.mock(base_url="https://api.aimsecurity.io") as router:
        router.get("/api/user").mock(
            return_value=httpx.Response(500, json={"message": "Internal error"})
        )
        with pytest.raises(ServerError):
            request("GET", "/api/user")
