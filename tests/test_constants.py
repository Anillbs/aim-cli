"""Tests for core/constants.py — immutable constants."""

from __future__ import annotations

from aim_cli.core.constants import (
    DEFAULT_API_URL,
    DEFAULT_TIMEOUT,
    EXIT_AUTH_ERROR,
    EXIT_QUALITY_GATE,
    EXIT_SUCCESS,
    RETRY_MAX_ATTEMPTS,
    SEVERITY_ORDER,
    USER_AGENT,
    VERSION,
)


def test_version_is_semver():
    """VERSION should be a valid semver string."""
    parts = VERSION.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


def test_default_api_url_is_https():
    """API URL must use HTTPS."""
    assert DEFAULT_API_URL.startswith("https://")


def test_exit_codes_are_unique():
    """Exit codes should be distinct integers."""
    codes = [EXIT_SUCCESS, EXIT_AUTH_ERROR, EXIT_QUALITY_GATE]
    assert len(codes) == len(set(codes))


def test_severity_order_has_all_levels():
    """SEVERITY_ORDER should contain standard severity levels."""
    for level in ("critical", "high", "medium", "low", "info"):
        assert level in SEVERITY_ORDER


def test_user_agent_contains_version():
    """User-Agent string should include the CLI version."""
    assert VERSION in USER_AGENT


def test_retry_max_attempts_positive():
    """RETRY_MAX_ATTEMPTS should be a positive integer."""
    assert RETRY_MAX_ATTEMPTS > 0


def test_default_timeout_reasonable():
    """DEFAULT_TIMEOUT should be between 10-120 seconds."""
    assert 10 <= DEFAULT_TIMEOUT <= 120
