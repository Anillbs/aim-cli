"""aim vulns — vulnerability results commands.

  aim vulns list              — List vulnerabilities
  aim vulns show <VULN_ID>    — Vulnerability detail (evidence, cURL, recommendation)
  aim vulns export            — Export vulnerabilities (SARIF/JSON/CSV)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer

from aim_cli.api import scan_api, vulns_api
from aim_cli.core.errors import AIMCLIError
from aim_cli.output.console import console, error, info, success
from aim_cli.output.formatters import format_output
from aim_cli.output.spinners import spinner
from aim_cli.output.tables import vuln_detail_table, vuln_list_table

vulns_app = typer.Typer(name="vulns", help="Vulnerability results.", no_args_is_help=True)


@vulns_app.command("list")
def list_cmd(
    scan: Optional[int] = typer.Option(None, "--scan", "-s", help="Filter by scan ID."),
    site: Optional[int] = typer.Option(None, "--site", help="Filter by site ID."),
    severity: Optional[str] = typer.Option(None, "--severity", help="Filter: critical,high,medium,low,info."),
    status: Optional[str] = typer.Option(None, "--status", help="Filter: open,fixed,accepted,false_positive."),
    limit: int = typer.Option(50, "--limit", "-n", help="Max results."),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json, csv, markdown."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """List vulnerabilities with optional filters."""
    with spinner("Fetching vulnerabilities..."):
        try:
            vulns = vulns_api.list_vulns(
                scan_id=scan, site_id=site, severity=severity,
                status=status, limit=limit, api_key=api_key,
            )
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    if format:
        console.print(format_output(vulns, format))
        return

    if not vulns:
        info("No vulnerabilities found.")
        return

    console.print()
    console.print(vuln_list_table(vulns))
    console.print(f"\n  [aim.subtle]{len(vulns)} vulnerabilities shown[/]\n")


@vulns_app.command("show")
def show(
    vuln_id: int = typer.Argument(..., help="Vulnerability ID."),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Show detailed vulnerability information."""
    with spinner("Fetching vulnerability details..."):
        try:
            vuln = vulns_api.show_vuln(vuln_id, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    if format == "json":
        console.print_json(data=vuln)
        return

    console.print()
    console.print(vuln_detail_table(vuln))

    # Show cURL reproduction command if available
    try:
        curl = vulns_api.get_curl(vuln_id, api_key=api_key)
        if curl:
            console.print("\n  [bold white]Evidence cURL:[/]")
            from rich.syntax import Syntax
            console.print(Syntax(curl, "bash", theme="monokai", padding=1))
    except AIMCLIError:
        pass

    console.print()


@vulns_app.command("export")
def export(
    scan: Optional[int] = typer.Option(None, "--scan", "-s", help="Scan ID to export."),
    format: str = typer.Option("sarif", "--format", "-f", help="Format: json, sarif, csv, markdown."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Export vulnerability data in various formats."""
    if not scan:
        error("--scan is required for export.", hint="Example: aim vulns export --scan 42 --format sarif")
        raise typer.Exit(1)

    if format == "sarif":
        # Use the server-side SARIF exporter
        with spinner("Generating SARIF report..."):
            try:
                data = scan_api.export(scan, fmt="sarif", api_key=api_key)
            except AIMCLIError as e:
                error(str(e), hint=e.hint)
                raise typer.Exit(e.exit_code)

        content = data.decode("utf-8") if isinstance(data, bytes) else str(data)
    else:
        # Fetch vulns and format locally
        with spinner("Fetching vulnerabilities..."):
            try:
                vulns = vulns_api.list_vulns(scan_id=scan, limit=9999, api_key=api_key)
            except AIMCLIError as e:
                error(str(e), hint=e.hint)
                raise typer.Exit(e.exit_code)

        fields = ["id", "vuln_type", "severity", "url", "status"]
        content = format_output(vulns, format, fields=fields)

    if output:
        output.write_text(content, encoding="utf-8")
        success(f"{len(content)} bytes written to {output}")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
