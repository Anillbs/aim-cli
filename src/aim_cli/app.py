"""AIM CLI — Typer application factory, global options, and error handler.

This is the single entry point.  It registers all sub-command groups,
applies the global exception handler, and provides top-level commands
(version, doctor).
"""

from __future__ import annotations

import platform
import sys
from typing import Optional

import typer

from aim_cli.commands.auth import auth_app
from aim_cli.commands.config_cmd import config_app
from aim_cli.commands.reports import reports_app
from aim_cli.commands.scan import scan_app
from aim_cli.commands.sites import sites_app
from aim_cli.commands.vulns import vulns_app
from aim_cli.core.constants import VERSION
from aim_cli.core.errors import AIMCLIError
from aim_cli.output.console import console, err_console, error, info, print_banner, success, warning

# ── Typer Application ─────────────────────────────────────────────────────────
app = typer.Typer(
    name="aim",
    help="AIM Security DAST — Command-Line Interface",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    add_completion=True,
)

# ── Register sub-command groups ───────────────────────────────────────────────
app.add_typer(auth_app)
app.add_typer(scan_app)
app.add_typer(sites_app)
app.add_typer(vulns_app)
app.add_typer(reports_app)
app.add_typer(config_app)


# ── Top-level commands ────────────────────────────────────────────────────────
@app.command()
def version() -> None:
    """Show AIM CLI version and check for updates."""
    print_banner(VERSION)

    from aim_cli.core.updater import check_for_update

    latest = check_for_update()
    if latest:
        warning(f"Update available: v{latest}. Run: pip install --upgrade aim-cli")


@app.command()
def doctor(
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Run environment diagnostics."""
    from aim_cli.core.config import load_config
    from aim_cli.core.credentials import has_token, resolve_token, mask_token
    from aim_cli.output.tables import doctor_table

    checks: list[tuple[bool, str, str]] = []

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append((sys.version_info >= (3, 11), "Python", py_ver))

    # CLI version
    checks.append((True, "aim-cli", VERSION))

    # HTTPX version
    try:
        import httpx
        checks.append((True, "HTTPX", httpx.__version__))
    except ImportError:
        checks.append((False, "HTTPX", "not installed"))

    # Keyring backend
    try:
        import keyring
        backend = type(keyring.get_keyring()).__name__
        checks.append((True, "Keyring backend", backend))
    except Exception as e:
        checks.append((False, "Keyring backend", str(e)))

    # Config
    cfg = load_config()
    api_url = cfg.get("api_url", "—")
    checks.append((True, "API URL", str(api_url)))

    # Proxy
    proxy = cfg.get("proxy", "")
    checks.append((True, "Proxy", str(proxy) if proxy else "none"))

    # CA Bundle
    ca = cfg.get("ca_bundle", "")
    checks.append((True, "CA Bundle", str(ca) if ca else "system default"))

    # Token check
    token_available = has_token() or bool(api_key)
    if token_available:
        try:
            token = resolve_token(api_key)
            checks.append((True, "Token", f"present ({mask_token(token)})"))
        except Exception:
            checks.append((False, "Token", "error reading token"))
    else:
        checks.append((False, "Token", "not configured"))

    # API reachability
    try:
        import httpx as _httpx
        base = str(api_url).rstrip("/")
        r = _httpx.get(f"{base}/api/login", timeout=10, follow_redirects=True)
        checks.append((r.status_code < 500, "API reachable", f"HTTP {r.status_code}"))
    except Exception as e:
        checks.append((False, "API reachable", f"failed ({type(e).__name__})"))

    # Token validity
    if token_available:
        try:
            from aim_cli.api import auth_api
            user = auth_api.me(api_key=api_key)
            email = user.get("email", "unknown")
            role = user.get("role_display", "")
            checks.append((True, "Token valid", f"{email} ({role})"))
        except Exception as e:
            checks.append((False, "Token valid", str(e)))

    console.print()
    console.print(doctor_table(checks))
    console.print()


# ── Global Error Handler ─────────────────────────────────────────────────────
def main() -> None:
    """Entry point with top-level exception handling."""
    try:
        # Update check (non-blocking, suppressed in CI)
        if sys.stdout.isatty():
            try:
                from aim_cli.core.updater import check_for_update

                latest = check_for_update()
                if latest:
                    err_console.print(
                        f"  [status.warning]⚠[/] AIM CLI v{latest} available "
                        f"(current: v{VERSION}). "
                        f"Update: pip install --upgrade aim-cli\n"
                    )
            except Exception:
                pass

        app()

    except KeyboardInterrupt:
        err_console.print("\n  [aim.subtle]Cancelled.[/]")
        sys.exit(130)

    except typer.Exit as e:
        sys.exit(e.exit_code)

    except AIMCLIError as e:
        error(str(e), hint=e.hint, request_id=e.request_id)
        sys.exit(e.exit_code)

    except Exception as e:
        error(
            "Unexpected error occurred.",
            hint="Run with --verbose for details or report this issue.",
        )
        if "--verbose" in sys.argv:
            import traceback
            err_console.print_exception()
        sys.exit(1)
