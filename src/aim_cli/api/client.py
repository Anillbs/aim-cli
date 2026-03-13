"""HTTPX client factory with retry, timeout, proxy, and auth header management.

Creates a single HTTPX Client per CLI invocation.  All API modules import
`get_client()` to obtain the shared instance.
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Any, Generator

import httpx

from aim_cli.core.config import load_config
from aim_cli.core.constants import (
    DEFAULT_TIMEOUT,
    RETRY_BACKOFF_SECONDS,
    RETRY_MAX_ATTEMPTS,
    RETRYABLE_STATUS_CODES,
    USER_AGENT,
)
from aim_cli.core.credentials import resolve_token
from aim_cli.core.errors import (
    AuthenticationError,
    ConnectionFailedError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    RequestTimeoutError,
    SSLCertError,
    ServerError,
    ValidationError,
)

_client: httpx.Client | None = None


def _build_client(api_key: str | None = None) -> httpx.Client:
    """Build a configured HTTPX client."""
    cfg = load_config()
    base_url = str(cfg.get("api_url", "")).rstrip("/")
    timeout = int(cfg.get("timeout", DEFAULT_TIMEOUT))
    proxy = str(cfg.get("proxy", "")) or None
    ca_bundle = str(cfg.get("ca_bundle", "")) or None

    token = resolve_token(api_key)

    transport_kwargs: dict[str, Any] = {}
    if proxy:
        transport_kwargs["proxy"] = proxy

    return httpx.Client(
        base_url=base_url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        timeout=httpx.Timeout(connect=10, read=timeout, write=timeout, pool=10),
        verify=ca_bundle if ca_bundle else True,
        follow_redirects=True,
        **transport_kwargs,
    )


@contextmanager
def api_client(api_key: str | None = None) -> Generator[httpx.Client, None, None]:
    """Context manager that yields a configured HTTPX client."""
    client = _build_client(api_key)
    try:
        yield client
    finally:
        client.close()


def request(
    method: str,
    path: str,
    *,
    api_key: str | None = None,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    stream: bool = False,
) -> httpx.Response:
    """Make an API request with retry logic and error mapping.

    Returns the httpx.Response on success.
    Raises descriptive AIMCLIError subclasses on failure.
    """
    with api_client(api_key) as client:
        request_id = str(uuid.uuid4())

        for attempt in range(RETRY_MAX_ATTEMPTS):
            try:
                resp = client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                    headers={"X-Request-ID": request_id},
                )
            except httpx.ConnectError:
                raise ConnectionFailedError()
            except httpx.TimeoutException:
                raise RequestTimeoutError(int(client.timeout.read or DEFAULT_TIMEOUT))  # type: ignore[arg-type]
            except httpx.NetworkError:
                raise ConnectionFailedError()

            # Retryable server errors
            if resp.status_code in RETRYABLE_STATUS_CODES:
                if attempt < RETRY_MAX_ATTEMPTS - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS[attempt])
                    continue
                raise ServerError(
                    f"Server error (HTTP {resp.status_code}).",
                    hint="Try again later or contact support.",
                    request_id=request_id,
                )

            # Rate limiting
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                raise RateLimitError(retry_after)

            # Auth errors — never retry
            if resp.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed.",
                    hint="Run 'aim auth login' or check your API key.",
                    request_id=request_id,
                )

            if resp.status_code == 403:
                body = _safe_json(resp)
                msg = body.get("message", "Access denied.")
                raise ForbiddenError(msg, request_id=request_id)

            if resp.status_code == 404:
                body = _safe_json(resp)
                msg = body.get("message", "Resource not found.")
                raise NotFoundError(msg, hint="Check the ID and try again.", request_id=request_id)

            if resp.status_code == 422:
                body = _safe_json(resp)
                msg = body.get("message", "Validation failed.")
                raise ValidationError(msg, request_id=request_id)

            if resp.status_code >= 500:
                raise ServerError(
                    f"Server error (HTTP {resp.status_code}).",
                    hint="Try again later.",
                    request_id=request_id,
                )

            return resp

    # Should not reach here, but satisfy type checker
    raise ServerError("Max retries exceeded.", request_id=request_id)


def _safe_json(resp: httpx.Response) -> dict[str, Any]:
    """Parse JSON response body, returning empty dict on failure."""
    try:
        return resp.json()  # type: ignore[no-any-return]
    except Exception:
        return {}
