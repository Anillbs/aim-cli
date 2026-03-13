"""TOML configuration manager.

Config location follows platform conventions:
  Linux:   ~/.config/aim/config.toml
  macOS:   ~/Library/Application Support/aim/config.toml
  Windows: %APPDATA%\\aim\\config.toml
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from aim_cli.core.constants import APP_NAME, CONFIG_FILENAME, DEFAULT_API_URL, DEFAULT_TIMEOUT

# ── Default values ────────────────────────────────────────────────────────────
DEFAULTS: dict[str, Any] = {
    "api_url": DEFAULT_API_URL,
    "timeout": DEFAULT_TIMEOUT,
    "default_format": "table",
    "default_profile": "standard",
    "auto_update": True,
    "telemetry": False,
    "proxy": "",
    "ca_bundle": "",
}

_CONFIG_TEMPLATE = """\
# AIM CLI Configuration
# Location: {path}

# API server address (change for on-premise installations)
# api_url = "https://api.aimsecurity.io"

# HTTP proxy address (for corporate networks)
# proxy = "https://proxy.corp.com:8080"

# Custom CA certificate path
# ca_bundle = "/path/to/ca-bundle.crt"

# Default output format: table, json, sarif, csv
# default_format = "table"

# Automatic update check
# auto_update = true

# Default scan profile
# default_profile = "standard"

# API request timeout (seconds)
# timeout = 30

# Anonymous usage telemetry (default: off)
# telemetry = false
"""


def _config_dir() -> Path:
    """Return the platform-specific config directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_NAME


import os  # noqa: E402 (used in _config_dir)


def config_path() -> Path:
    """Return full path to the config file."""
    return _config_dir() / CONFIG_FILENAME


def load_config() -> dict[str, Any]:
    """Load config from disk, merged with defaults."""
    path = config_path()
    data: dict[str, Any] = {}

    if path.exists():
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError):
            pass

    merged = {**DEFAULTS, **data}
    return merged


def save_config(data: dict[str, Any]) -> None:
    """Write config dict to TOML file."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tomli_w.dumps(data).encode("utf-8"))


def get_value(key: str) -> Any:
    """Read a single config value."""
    cfg = load_config()
    return cfg.get(key)


def set_value(key: str, value: Any) -> None:
    """Set a single config value."""
    cfg = load_config()
    # Type coercion for known fields
    if key in ("timeout",) and isinstance(value, str):
        value = int(value)
    if key in ("auto_update", "telemetry") and isinstance(value, str):
        value = value.lower() in ("true", "1", "yes")
    cfg[key] = value
    save_config(cfg)


def reset_config() -> Path:
    """Reset config to defaults (writes a template file)."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_CONFIG_TEMPLATE.format(path=path), encoding="utf-8")
    return path


def show_config() -> dict[str, Any]:
    """Return the effective config (defaults + overrides)."""
    return load_config()
