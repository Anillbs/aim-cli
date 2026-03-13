"""Tests for core/errors.py — exception hierarchy."""

from __future__ import annotations

from aim_cli.core.constants import (
    EXIT_AUTH_ERROR,
    EXIT_GENERAL_ERROR,
    EXIT_NETWORK_ERROR,
    EXIT_QUALITY_GATE,
    EXIT_SCAN_TIMEOUT,
)
from aim_cli.core.errors import (
    AIMCLIError,
    AuthenticationError,
    ConnectionFailedError,
    QualityGateError,
    ScanTimeoutError,
    TokenNotFoundError,
)


def test_base_error_has_exit_code():
    """AIMCLIError should carry an exit_code."""
    err = AIMCLIError("boom")
    assert err.exit_code == EXIT_GENERAL_ERROR
    assert str(err) == "boom"


def test_auth_error_is_aimcli_error():
    """AuthenticationError should inherit from AIMCLIError."""
    err = AuthenticationError("bad token")
    assert isinstance(err, AIMCLIError)
    assert err.exit_code == EXIT_AUTH_ERROR


def test_token_not_found_has_hint():
    """TokenNotFoundError should include a helpful hint."""
    err = TokenNotFoundError()
    assert err.hint is not None
    assert "login" in err.hint.lower() or "AIM_API_KEY" in err.hint


def test_quality_gate_error():
    """QualityGateError should use EXIT_QUALITY_GATE."""
    err = QualityGateError({"critical": 1, "high": 2})
    assert err.exit_code == EXIT_QUALITY_GATE
    assert "critical" in str(err)


def test_scan_timeout_error():
    """ScanTimeoutError should use EXIT_SCAN_TIMEOUT."""
    err = ScanTimeoutError(1800)
    assert err.exit_code == EXIT_SCAN_TIMEOUT
    assert "1800" in str(err)


def test_network_error_exit_code():
    """Network errors should use EXIT_NETWORK_ERROR."""
    err = ConnectionFailedError()
    assert err.exit_code == EXIT_NETWORK_ERROR
