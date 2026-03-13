"""aim reports — report generation and download commands.

  aim reports generate <SCAN_ID>   — Generate a report
  aim reports download <REPORT_ID> — Download a report
  aim reports list                 — List available reports
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from aim_cli.api import reports_api
from aim_cli.core.errors import AIMCLIError
from aim_cli.output.console import console, error, info, success
from aim_cli.output.spinners import spinner
from aim_cli.output.tables import report_list_table

reports_app = typer.Typer(name="reports", help="Report management.", no_args_is_help=True)


@reports_app.command("generate")
def generate(
    scan_id: int = typer.Argument(..., help="Scan ID to generate report for."),
    template: str = typer.Option("technical", "--template", "-t", help="Template: executive, technical, compliance."),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Generate a report for a completed scan."""
    with spinner("Generating report..."):
        try:
            result = reports_api.generate(scan_id, template=template, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint, request_id=e.request_id)
            raise typer.Exit(e.exit_code)

    if format == "json":
        console.print_json(data=result)
        return

    report_id = result.get("id", result.get("report_id", ""))
    success(f"Report generated (ID: {report_id})")
    info(f"Download: aim reports download {report_id}")


@reports_app.command("download")
def download(
    report_id: int = typer.Argument(..., help="Report ID to download."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Download a generated report."""
    with spinner("Downloading report..."):
        try:
            data = reports_api.download(report_id, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    filepath = output or Path(f"aim_report_{report_id}.pdf")
    filepath.write_bytes(data)
    success(f"Report saved to {filepath}")


@reports_app.command("list")
def list_cmd(
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """List available reports."""
    with spinner("Fetching reports..."):
        try:
            reports = reports_api.list_reports(api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    if format == "json":
        console.print_json(data=reports)
        return

    if not reports:
        info("No reports found.")
        return

    console.print()
    console.print(report_list_table(reports))
    console.print()
