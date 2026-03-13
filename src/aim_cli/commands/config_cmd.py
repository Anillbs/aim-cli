"""aim config — configuration management commands.

  aim config set <KEY> <VALUE>  — Set a configuration value
  aim config get <KEY>          — Read a configuration value
  aim config reset              — Restore defaults
  aim config show               — Show all effective settings
"""

from __future__ import annotations

from typing import Optional

import typer

from aim_cli.core.config import config_path, get_value, reset_config, set_value, show_config
from aim_cli.output.console import console, info, success

config_app = typer.Typer(name="config", help="Configuration management.", no_args_is_help=True)

_VALID_KEYS = {
    "api_url", "timeout", "default_format", "default_profile",
    "auto_update", "telemetry", "proxy", "ca_bundle",
}


@config_app.command("set")
def set_cmd(
    key: str = typer.Argument(..., help="Configuration key."),
    value: str = typer.Argument(..., help="Value to set."),
) -> None:
    """Set a configuration value."""
    if key not in _VALID_KEYS and not key.startswith("_"):
        console.print(f"  [status.warning]⚠[/] Unknown key: {key}")
        console.print(f"  Valid keys: {', '.join(sorted(_VALID_KEYS))}")
        raise typer.Exit(1)

    set_value(key, value)
    success(f"{key} = {value}")


@config_app.command("get")
def get_cmd(
    key: str = typer.Argument(..., help="Configuration key to read."),
) -> None:
    """Read a configuration value."""
    val = get_value(key)
    if val is None:
        info(f"{key} is not set (using default).")
    else:
        console.print(f"  {key} = {val}")


@config_app.command("reset")
def reset(
    force: bool = typer.Option(False, "--force", help="Skip confirmation."),
) -> None:
    """Restore configuration to defaults."""
    if not force:
        confirm = typer.confirm("Reset all settings to defaults?")
        if not confirm:
            info("Cancelled.")
            return

    path = reset_config()
    success(f"Configuration reset → {path}")


@config_app.command("show")
def show(
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json."),
) -> None:
    """Show all effective settings."""
    cfg = show_config()
    path = config_path()

    if format == "json":
        console.print_json(data=cfg)
        return

    console.print(f"\n  [aim.subtle]Config file: {path}[/]\n")
    for key, val in sorted(cfg.items()):
        if key.startswith("_"):
            continue
        console.print(f"  [bold white]{key}[/] = {val}")
    console.print()
