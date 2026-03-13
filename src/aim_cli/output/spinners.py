"""Spinner and progress bar context managers for long operations.

Only shown in TTY mode — silently suppressed in pipe/CI.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Generator

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from aim_cli.output.console import console


@contextmanager
def spinner(message: str) -> Generator[None, None, None]:
    """Show a spinner while work is in progress."""
    if not sys.stdout.isatty():
        yield
        return

    with console.status(f"  {message}", spinner="dots"):
        yield


@contextmanager
def scan_progress() -> Generator[Progress, None, None]:
    """Show a multi-step progress bar for scan --wait polling."""
    if not sys.stdout.isatty():
        progress = Progress(disable=True)
        with progress:
            yield progress
        return

    progress = Progress(
        SpinnerColumn("dots"),
        TextColumn("[aim.subtle]{task.description}"),
        BarColumn(bar_width=30, style="bright_magenta", complete_style="bold bright_magenta"),
        TaskProgressColumn(),
        console=console,
    )
    with progress:
        yield progress
