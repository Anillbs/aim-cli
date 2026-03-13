"""aim auth — authentication commands.

  aim auth login     — Authenticate with API token
  aim auth logout    — Remove stored token
  aim auth whoami    — Show current user info
  aim auth status    — Check token validity
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.prompt import Prompt

from aim_cli.api import auth_api
from aim_cli.core.credentials import delete_token, has_token, mask_token, resolve_token, store_token
from aim_cli.core.errors import AIMCLIError
from aim_cli.output.console import console, error, info, print_banner, success
from aim_cli.output.spinners import spinner

auth_app = typer.Typer(name="auth", help="Authentication management.", no_args_is_help=True)


@auth_app.command()
def login(
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key (prefer env var for CI/CD)."),
) -> None:
    """Authenticate with your AIM Security API token."""
    from aim_cli.core.constants import VERSION

    print_banner(VERSION)

    if api_key:
        token = api_key
    else:
        token = Prompt.ask("  [bold white]? API Key[/]", password=True, console=console)

    if not token or not token.strip():
        error("No token provided.")
        raise typer.Exit(1)

    token = token.strip()

    # Validate token against the API
    with spinner("Validating token..."):
        try:
            user = auth_api.me(api_key=token)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    store_token(token)

    email = user.get("email", "unknown")
    name = user.get("name", "")
    plan = user.get("role_display", user.get("tenant_role", ""))

    display = f"{email}"
    if name:
        display = f"{name} ({email})"

    success(f"Login successful — Welcome, {display}")
    if plan:
        info(f"Plan: {plan}")


@auth_app.command()
def logout() -> None:
    """Remove the stored API token."""
    delete_token()
    success("Token removed. You are logged out.")


@auth_app.command()
def whoami(
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Show current authenticated user info."""
    with spinner("Checking identity..."):
        try:
            user = auth_api.me(api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    console.print()
    console.print(f"  [bold white]User:[/]   {user.get('name', '—')} ({user.get('email', '—')})")
    console.print(f"  [bold white]Role:[/]   {user.get('role_display', user.get('tenant_role', '—'))}")
    console.print(f"  [bold white]Tenant:[/] {user.get('tenant_id', '—')}")

    perms = user.get("permissions", [])
    if perms:
        console.print(f"  [bold white]Perms:[/]  {', '.join(perms[:5])}")
    console.print()


@auth_app.command()
def status(
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Check if the current token is valid."""
    if not has_token() and not api_key:
        error("No token found.", hint="Run 'aim auth login' to authenticate.")
        raise typer.Exit(4)

    try:
        token = resolve_token(api_key)
    except AIMCLIError as e:
        error(str(e), hint=e.hint)
        raise typer.Exit(e.exit_code)

    with spinner("Validating token..."):
        try:
            user = auth_api.me(api_key=api_key)
        except AIMCLIError as e:
            error(f"Token invalid: {e}", hint=e.hint)
            raise typer.Exit(e.exit_code)

    success(f"Token valid — {user.get('email', 'unknown')} ({mask_token(token)})")
