"""Tests for core/config.py — TOML configuration management."""

from __future__ import annotations

from aim_cli.core.config import DEFAULTS, load_config, set_value, get_value, reset_config


def test_defaults():
    """DEFAULTS dict should have all required keys."""
    assert "api_url" in DEFAULTS
    assert "timeout" in DEFAULTS
    assert DEFAULTS["telemetry"] is False


def test_load_config_returns_defaults_when_no_file(tmp_path, monkeypatch):
    """When no config file exists, load_config should return defaults."""
    monkeypatch.setattr("aim_cli.core.config._config_dir", lambda: tmp_path)
    cfg = load_config()
    assert cfg["api_url"] == DEFAULTS["api_url"]
    assert cfg["timeout"] == DEFAULTS["timeout"]


def test_set_and_get_value(tmp_path, monkeypatch):
    """set_value / get_value round-trip."""
    monkeypatch.setattr("aim_cli.core.config._config_dir", lambda: tmp_path)
    set_value("api_url", "https://custom.api.com")
    assert get_value("api_url") == "https://custom.api.com"


def test_reset_creates_template(tmp_path, monkeypatch):
    """reset_config should create a template file."""
    monkeypatch.setattr("aim_cli.core.config._config_dir", lambda: tmp_path)
    path = reset_config()
    assert path.exists()
    content = path.read_text()
    assert "AIM CLI" in content
