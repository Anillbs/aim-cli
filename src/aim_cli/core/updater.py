"""Auto-update checker — notification only (no auto-install in v1.0).

Checks PyPI for the latest version at most once per 24 hours.
In CI/CD mode (no TTY or AIM_CI=true), the check is silently skipped.
"""

from __future__ import annotations

import os
import sys
import time

import httpx

from aim_cli.core.config import get_value, set_value
from aim_cli.core.constants import VERSION

_PYPI_URL = "https://pypi.org/pypi/aim-cli/json"
_CHECK_INTERVAL = 86400  # 24 hours


def _is_ci() -> bool:
    """Detect CI/CD environment."""
    return os.environ.get("AIM_CI", "").lower() in ("true", "1") or not sys.stdout.isatty()


def check_for_update() -> str | None:
    """Return latest version string if an update is available, else None.

    Never raises — silently returns None on any failure.
    """
    if _is_ci():
        return None

    # Throttle: check at most once per 24h
    last_check = get_value("_last_update_check") or 0
    if isinstance(last_check, str):
        try:
            last_check = float(last_check)
        except ValueError:
            last_check = 0
    if time.time() - float(last_check) < _CHECK_INTERVAL:
        return None

    try:
        resp = httpx.get(_PYPI_URL, timeout=5, follow_redirects=True)
        if resp.status_code == 200:
            latest = resp.json().get("info", {}).get("version", VERSION)
            set_value("_last_update_check", int(time.time()))
            if latest != VERSION:
                return latest
    except Exception:
        pass

    return None
