"""Credential management — OS Keyring with environment variable fallback.

Token resolution chain (highest priority first):
  1. Explicit --api-key CLI argument (testing only)
  2. AIM_API_KEY environment variable (CI/CD)
  3. OS Keyring (interactive users)
  4. None → raises TokenNotFoundError
"""

from __future__ import annotations

import os

import keyring
import keyring.errors

from aim_cli.core.constants import KEYRING_ACCOUNT, KEYRING_SERVICE
from aim_cli.core.errors import TokenNotFoundError


def resolve_token(cli_token: str | None = None) -> str:
    """Resolve API token from the priority chain.

    Returns the first available token or raises TokenNotFoundError.
    """
    # 1. Explicit CLI argument
    if cli_token:
        return cli_token

    # 2. Environment variable
    env_token = os.environ.get("AIM_API_KEY")
    if env_token:
        return env_token

    # 3. OS Keyring
    try:
        stored = keyring.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
        if stored:
            return stored
    except keyring.errors.KeyringError:
        pass

    raise TokenNotFoundError()


def store_token(token: str) -> None:
    """Save token to OS Keyring."""
    keyring.set_password(KEYRING_SERVICE, KEYRING_ACCOUNT, token)


def delete_token() -> None:
    """Remove token from OS Keyring."""
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
    except keyring.errors.PasswordDeleteError:
        pass


def has_token() -> bool:
    """Check whether any token is available (without exposing it)."""
    try:
        resolve_token()
        return True
    except TokenNotFoundError:
        return False


def mask_token(token: str) -> str:
    """Return a masked representation for display (never log full token)."""
    if len(token) <= 8:
        return "***"
    return token[:4] + "***" + token[-4:]
