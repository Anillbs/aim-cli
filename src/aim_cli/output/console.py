"""Singleton Rich Console, theme, and the AIM ASCII art banner."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

# ── AIM Security brand theme ─────────────────────────────────────────────────
AIM_THEME = Theme(
    {
        "aim.brand": "bold bright_magenta",
        "aim.accent": "bold white",
        "aim.subtle": "dim white",
        "severity.critical": "bold white on red",
        "severity.high": "bold red",
        "severity.medium": "bold yellow",
        "severity.low": "bold blue",
        "severity.info": "dim white",
        "status.success": "bold green",
        "status.warning": "bold yellow",
        "status.error": "bold red",
        "status.pending": "bold cyan",
    }
)

# ── Singleton consoles ────────────────────────────────────────────────────────
console = Console(theme=AIM_THEME, highlight=False)
err_console = Console(theme=AIM_THEME, stderr=True, highlight=False)


# ── ASCII Art Banner ─────────────────────────────────────────────────────────
_BANNER = r"""
[bright_magenta]
     █████╗    ██╗   ███╗   ███╗
    ██╔══██╗   ██║   ████╗ ████║
    ███████║   ██║   ██╔████╔██║
    ██╔══██║   ██║   ██║╚██╔╝██║
    ██║  ██║██╗██║██╗██║ ╚═╝ ██║
    ╚═╝  ╚═╝╚═╝╚═╝╚═╝╚═╝     ╚═╝[/]
[bold white]     ░▒▓ S E C U R I T Y ▓▒░[/]
"""


def print_banner(version: str) -> None:
    """Display the AIM Security ASCII art logo with version."""
    console.print(_BANNER)
    console.print(
        f"  [aim.subtle]DAST Command-Line Interface v{version}[/]\n",
        justify="center",
    )


def success(msg: str) -> None:
    console.print(f"  [status.success]✔[/] {msg}")


def warning(msg: str) -> None:
    console.print(f"  [status.warning]⚠[/] {msg}")


def error(msg: str, *, hint: str | None = None, request_id: str | None = None) -> None:
    err_console.print(f"\n  [status.error]✖ Error:[/] {msg}")
    if hint:
        err_console.print(f"  [aim.subtle]  Hint: {hint}[/]")
    if request_id:
        err_console.print(f"  [aim.subtle]  Request ID: {request_id}[/]")
    err_console.print()


def info(msg: str) -> None:
    console.print(f"  [aim.subtle]ℹ[/] {msg}")


def severity_style(level: str) -> str:
    """Return the Rich style name for a severity level."""
    return f"severity.{level.lower()}" if level.lower() in (
        "critical", "high", "medium", "low", "info"
    ) else "dim"
