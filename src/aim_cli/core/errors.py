"""Custom exception hierarchy with exit code mapping.

Every AIMCLIError subclass carries a specific exit code so the top-level
handler in app.py can terminate with the correct code for CI/CD pipelines.
"""

from __future__ import annotations

from aim_cli.core.constants import (
    EXIT_AUTH_ERROR,
    EXIT_FORBIDDEN,
    EXIT_GENERAL_ERROR,
    EXIT_NETWORK_ERROR,
    EXIT_NOT_FOUND,
    EXIT_QUALITY_GATE,
    EXIT_SCAN_TIMEOUT,
)


class AIMCLIError(Exception):
    """Base exception for all AIM CLI errors."""

    exit_code: int = EXIT_GENERAL_ERROR

    def __init__(self, message: str, *, hint: str | None = None, request_id: str | None = None):
        self.hint = hint
        self.request_id = request_id
        super().__init__(message)


# ── Authentication ────────────────────────────────────────────────────────────
class AuthenticationError(AIMCLIError):
    exit_code = EXIT_AUTH_ERROR


class TokenNotFoundError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(
            "Token not found.",
            hint="Run 'aim auth login' or set AIM_API_KEY environment variable.",
        )


class TokenExpiredError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("Token expired.", hint="Run 'aim auth login' to re-authenticate.")


class TokenInvalidError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("Token is invalid.", hint="Check your API key and try again.")


# ── API Errors ────────────────────────────────────────────────────────────────
class APIError(AIMCLIError):
    exit_code = EXIT_NETWORK_ERROR


class NotFoundError(APIError):
    exit_code = EXIT_NOT_FOUND


class ForbiddenError(APIError):
    exit_code = EXIT_FORBIDDEN

    def __init__(self, message: str = "Insufficient permissions.", **kwargs: object):
        super().__init__(message, hint="Check your plan or role permissions.", **kwargs)  # type: ignore[arg-type]


class RateLimitError(APIError):
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after}s.",
            hint="Wait and try again or contact support.",
        )


class ValidationError(APIError):
    exit_code = EXIT_GENERAL_ERROR


class ServerError(APIError):
    pass


# ── Network ───────────────────────────────────────────────────────────────────
class NetworkError(AIMCLIError):
    exit_code = EXIT_NETWORK_ERROR


class ConnectionFailedError(NetworkError):
    def __init__(self) -> None:
        super().__init__(
            "Cannot connect to AIM API.",
            hint="Check your internet connection or API URL: aim config set api_url <URL>",
        )


class RequestTimeoutError(NetworkError):
    def __init__(self, timeout: int = 30):
        super().__init__(
            f"Request timed out ({timeout}s).",
            hint="Try: aim config set timeout 60",
        )


class SSLCertError(NetworkError):
    def __init__(self) -> None:
        super().__init__(
            "SSL certificate verification failed.",
            hint="Corporate proxy? Try: aim config set ca_bundle /path/to/cert.pem",
        )


# ── Config ────────────────────────────────────────────────────────────────────
class ConfigError(AIMCLIError):
    exit_code = EXIT_GENERAL_ERROR


class InvalidConfigError(ConfigError):
    def __init__(self) -> None:
        super().__init__(
            "Configuration file is corrupted.",
            hint="Run 'aim config reset' to restore defaults.",
        )


# ── Quality Gate ──────────────────────────────────────────────────────────────
class QualityGateError(AIMCLIError):
    exit_code = EXIT_QUALITY_GATE

    def __init__(self, counts: dict[str, int]):
        parts = [f"{v} {k}" for k, v in counts.items() if v > 0]
        detail = ", ".join(parts)
        super().__init__(f"Quality gate failed: {detail}.")


# ── Scan Timeout ──────────────────────────────────────────────────────────────
class ScanTimeoutError(AIMCLIError):
    exit_code = EXIT_SCAN_TIMEOUT

    def __init__(self, scan_id: int):
        super().__init__(
            f"Scan #{scan_id} did not complete within the timeout period.",
            hint="Check status manually: aim scan status {scan_id}",
        )
