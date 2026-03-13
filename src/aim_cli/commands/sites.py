"""aim sites — site/domain management commands.

  aim sites add <URL>         — Add a new site
  aim sites list              — List all sites
  aim sites remove <SITE_ID>  — Remove a site
  aim sites verify <SITE_ID>  — Trigger domain verification
"""

from __future__ import annotations

from typing import Optional

import typer

from aim_cli.api import sites_api
from aim_cli.core.errors import AIMCLIError
from aim_cli.output.console import console, error, info, success
from aim_cli.output.formatters import format_output
from aim_cli.output.spinners import spinner
from aim_cli.output.tables import site_list_table

sites_app = typer.Typer(name="sites", help="Site and domain management.", no_args_is_help=True)


@sites_app.command("add")
def add(
    url: str = typer.Argument(..., help="Site URL (e.g. https://example.com)."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Friendly name for the site."),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Add a new site to your AIM account."""
    with spinner("Adding site..."):
        try:
            result = sites_api.add_site(url, name=name, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint, request_id=e.request_id)
            raise typer.Exit(e.exit_code)

    if format == "json":
        console.print_json(data=result)
        return

    site = result.get("site", result)
    site_id = site.get("id", "")
    success(f"Site added (ID: {site_id})")
    info(f"Domain verification required: aim sites verify {site_id}")


@sites_app.command("list")
def list_cmd(
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json, csv, markdown."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """List all sites."""
    with spinner("Fetching sites..."):
        try:
            sites = sites_api.list_sites(api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    if format:
        console.print(format_output(sites, format))
        return

    if not sites:
        info("No sites found. Add one: aim sites add https://example.com")
        return

    console.print()
    console.print(site_list_table(sites))
    console.print()


@sites_app.command("remove")
def remove(
    site_id: int = typer.Argument(..., help="Site ID to remove."),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Remove a site."""
    if not force:
        confirm = typer.confirm(f"Remove site #{site_id}? This cannot be undone")
        if not confirm:
            info("Cancelled.")
            return

    with spinner("Removing site..."):
        try:
            sites_api.remove_site(site_id, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    success(f"Site #{site_id} removed.")


@sites_app.command("verify")
def verify(
    site_id: int = typer.Argument(..., help="Site/domain ID to verify."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Trigger domain ownership verification."""
    with spinner("Verifying domain..."):
        try:
            result = sites_api.verify_site(site_id, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    msg = result.get("message", "Verification initiated.")
    success(msg)
