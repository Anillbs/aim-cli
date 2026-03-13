"""Immutable constants used across the CLI."""

from __future__ import annotations

import platform
import sys

# ── Version ───────────────────────────────────────────────────────────────────
VERSION = "1.0.0"

# ── API Defaults ──────────────────────────────────────────────────────────────
DEFAULT_API_URL = "https://api.aimsecurity.io"
DEFAULT_TIMEOUT = 30          # seconds
POLL_INTERVAL = 5             # seconds between --wait polls
POLL_MAX_WAIT = 1800          # default 30 minutes max polling duration

# ── Per-profile poll timeouts (seconds) ──────────────────────────────────────
POLL_TIMEOUT_BY_PROFILE: dict[str, int] = {
    "quick":    600,       # 10 minutes
    "standard": 1800,      # 30 minutes
    "deep":     7200,      # 120 minutes
}

# ── User-Agent ────────────────────────────────────────────────────────────────
USER_AGENT = (
    f"aim-cli/{VERSION} "
    f"({platform.system()} {platform.release()}; "
    f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})"
)

# ── Keyring ───────────────────────────────────────────────────────────────────
KEYRING_SERVICE = "aim-cli"
KEYRING_ACCOUNT = "api-token"

# ── Config ────────────────────────────────────────────────────────────────────
APP_NAME = "aim"
CONFIG_FILENAME = "config.toml"

# ── Exit Codes ────────────────────────────────────────────────────────────────
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_QUALITY_GATE = 2
EXIT_NETWORK_ERROR = 3
EXIT_AUTH_ERROR = 4
EXIT_NOT_FOUND = 5
EXIT_FORBIDDEN = 6
EXIT_SCAN_TIMEOUT = 10

# ── Retry ─────────────────────────────────────────────────────────────────────
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = [1, 2, 4]
RETRYABLE_STATUS_CODES = {502, 503, 504}

# ── Severity Levels ──────────────────────────────────────────────────────────
SEVERITY_ORDER = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
