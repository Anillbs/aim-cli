"""Tests for core/credentials.py — token resolution chain."""

from __future__ import annotations

import pytest

from aim_cli.core.credentials import mask_token, resolve_token
from aim_cli.core.errors import TokenNotFoundError


def test_resolve_token_cli_arg_highest_priority(monkeypatch):
    """Explicit CLI argument should take priority over everything."""
    monkeypatch.setenv("AIM_API_KEY", "env-token")
    assert resolve_token("cli-token") == "cli-token"


def test_resolve_token_env_var(monkeypatch):
    """Environment variable should be used when no CLI arg given."""
    monkeypatch.setenv("AIM_API_KEY", "env-token-123")
    # Patch keyring to ensure we're not reading from it
    monkeypatch.setattr("aim_cli.core.credentials.keyring.get_password", lambda s, a: None)
    assert resolve_token() == "env-token-123"


def test_resolve_token_raises_when_nothing_available(monkeypatch):
    """Should raise TokenNotFoundError when no token source exists."""
    monkeypatch.delenv("AIM_API_KEY", raising=False)
    monkeypatch.setattr("aim_cli.core.credentials.keyring.get_password", lambda s, a: None)
    with pytest.raises(TokenNotFoundError):
        resolve_token()


def test_mask_token_long():
    """Long tokens show first 4 and last 4 chars."""
    assert mask_token("abcdefghijklmnop") == "abcd***mnop"


def test_mask_token_short():
    """Short tokens are fully masked."""
    assert mask_token("abc") == "***"
    assert mask_token("12345678") == "***"
