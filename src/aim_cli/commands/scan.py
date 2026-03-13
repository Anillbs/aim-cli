"""aim scan — scan management commands.

  aim scan start <SITE_ID|URL>   — Start a new scan
  aim scan status <SCAN_ID>      — Check scan status
  aim scan list                  — List recent scans
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

import typer

from aim_cli.api import scan_api
from aim_cli.core.constants import POLL_INTERVAL, POLL_MAX_WAIT, POLL_TIMEOUT_BY_PROFILE, SEVERITY_ORDER
from aim_cli.core.errors import AIMCLIError, QualityGateError, ScanTimeoutError
from aim_cli.output.console import console, error, info, success, warning
from aim_cli.output.formatters import format_output
from aim_cli.output.spinners import scan_progress, spinner
from aim_cli.output.tables import scan_results_table

scan_app = typer.Typer(name="scan", help="Scan management.", no_args_is_help=True)


@scan_app.command("start")
def start(
    target: str = typer.Argument(..., help="Site ID (integer) or domain URL."),
    profile: str = typer.Option("standard", "--profile", "-p", help="Scan profile: quick, standard, deep."),
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for scan to complete (CI/CD mode)."),
    fail_on: Optional[str] = typer.Option(None, "--fail-on", help="Quality gate: critical, high, medium, low."),
    incremental: bool = typer.Option(False, "--incremental", help="Incremental scan (changed endpoints only)."),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json, sarif, csv."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write output to file."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Start a new security scan."""
    # Determine if target is a site_id or domain
    site_id: int | None = None
    domain: str | None = None
    try:
        site_id = int(target)
    except ValueError:
        domain = target

    # Trigger the scan
    with spinner("Starting scan..."):
        try:
            result = scan_api.trigger(
                site_id=site_id, domain=domain, profile=profile, api_key=api_key
            )
        except AIMCLIError as e:
            error(str(e), hint=e.hint, request_id=e.request_id)
            raise typer.Exit(e.exit_code)

    scan_id = result.get("scan_id")
    scan_domain = result.get("site", {}).get("domain", domain or str(site_id))

    console.print(f"\n  [aim.brand]✦[/] Scan [bold]#{scan_id}[/] started ({profile} profile) → {scan_domain}")

    if not wait:
        info(f"Track progress: aim scan status {scan_id}")
        if format == "json":
            _write_output(format_output(result, "json"), output)
        return

    # ── Polling loop (--wait mode) ────────────────────────────────────────────
    _poll_until_complete(scan_id, fail_on=fail_on, fmt=format, output=output, api_key=api_key, profile=profile)


def _poll_until_complete(
    scan_id: int,
    *,
    fail_on: str | None = None,
    fmt: str | None = None,
    output: Path | None = None,
    api_key: str | None = None,
    profile: str = "standard",
) -> None:
    """Poll scan status until completed/failed, showing progress."""
    start_time = time.time()
    max_wait = POLL_TIMEOUT_BY_PROFILE.get(profile, POLL_MAX_WAIT)

    with scan_progress() as progress:
        task = progress.add_task("Scanning...", total=100)

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                raise ScanTimeoutError(scan_id)

            try:
                data = scan_api.status(scan_id, api_key=api_key)
            except AIMCLIError as e:
                error(str(e), hint=e.hint, request_id=e.request_id)
                raise typer.Exit(e.exit_code)

            status = data.get("status", "unknown")
            pct = data.get("progress", 0)
            step = data.get("progress_step", "")

            progress.update(task, completed=pct, description=step or status.capitalize())

            if status == "completed":
                progress.update(task, completed=100, description="Completed")
                break

            if status == "failed":
                error(f"Scan #{scan_id} failed.")
                raise typer.Exit(3)

            time.sleep(POLL_INTERVAL)

    # ── Show results ──────────────────────────────────────────────────────────
    data = scan_api.status(scan_id, api_key=api_key)
    summary = data.get("summary", {})

    elapsed_sec = int(time.time() - start_time)
    elapsed_str = f"{elapsed_sec // 60}m {elapsed_sec % 60}s"

    console.print()
    console.print(scan_results_table(summary, scan_id))
    console.print(f"\n  [aim.subtle]Duration: {elapsed_str}[/]")
    info(f"Details: aim vulns list --scan {scan_id}")
    console.print()

    # ── Export if format requested ────────────────────────────────────────────
    if fmt and fmt in ("sarif", "json", "csv"):
        _export_results(scan_id, fmt, output, api_key=api_key)

    # ── Quality gate check ────────────────────────────────────────────────────
    if fail_on:
        _check_quality_gate(summary, fail_on)


def _export_results(
    scan_id: int, fmt: str, output: Path | None, *, api_key: str | None = None
) -> None:
    """Download and write export data."""
    with spinner(f"Exporting {fmt.upper()}..."):
        try:
            data = scan_api.export(scan_id, fmt=fmt, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            return

    content = data.decode("utf-8") if isinstance(data, bytes) else str(data)
    _write_output(content, output)
    if output:
        success(f"Report written to {output}")


def _check_quality_gate(summary: dict, fail_on: str) -> None:
    """Raise QualityGateError if severity threshold is exceeded."""
    threshold = SEVERITY_ORDER.get(fail_on.lower(), 0)
    vulns = summary.get("vulnerabilities", {})

    failing: dict[str, int] = {}
    for sev, weight in SEVERITY_ORDER.items():
        if weight >= threshold:
            count = vulns.get(sev, 0)
            if count > 0:
                failing[sev] = count

    if failing:
        raise QualityGateError(failing)


def _write_output(content: str, output: Path | None) -> None:
    """Write content to file or stdout."""
    if output:
        output.write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")


@scan_app.command("status")
def status_cmd(
    scan_id: int = typer.Argument(..., help="Scan ID to check."),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """Check the status of a scan."""
    with spinner("Fetching status..."):
        try:
            data = scan_api.status(scan_id, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint, request_id=e.request_id)
            raise typer.Exit(e.exit_code)

    if format == "json":
        console.print_json(data=data)
        return

    st = data.get("status", "unknown")
    pct = data.get("progress", 0)
    step = data.get("progress_step", "")
    score = data.get("score", "—")

    status_style = {
        "pending": "status.pending",
        "processing": "status.warning",
        "completed": "status.success",
        "failed": "status.error",
    }.get(st, "dim")

    console.print(f"\n  [bold]Scan #{scan_id}[/]")
    console.print(f"  Status:   [{status_style}]{st.upper()}[/]")
    console.print(f"  Progress: {pct}% {f'({step})' if step else ''}")
    console.print(f"  Score:    {score}")
    console.print(f"  Source:   {data.get('source', '—')}")
    console.print()

    if st == "completed" and data.get("summary"):
        console.print(scan_results_table(data["summary"], scan_id))
        console.print()


@scan_app.command("list")
def list_cmd(
    site: Optional[int] = typer.Option(None, "--site", "-s", help="Filter by site ID."),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results."),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="AIM_API_KEY", hidden=True),
) -> None:
    """List recent scans."""
    with spinner("Fetching scans..."):
        try:
            data = scan_api.list_scans(site_id=site, limit=limit, api_key=api_key)
        except AIMCLIError as e:
            error(str(e), hint=e.hint)
            raise typer.Exit(e.exit_code)

    if format == "json":
        console.print_json(data=data)
        return

    scans = data if isinstance(data, list) else data.get("data", data.get("history", []))
    if not scans:
        info("No scans found.")
        return

    from rich.table import Table
    import rich.box

    table = Table(box=rich.box.ROUNDED, pad_edge=True, show_lines=False)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Domain", min_width=20)
    table.add_column("Status", min_width=10)
    table.add_column("Score", width=6)
    table.add_column("Created", min_width=16)

    for s in scans[:limit]:
        st = s.get("status", "—")
        style = {"completed": "status.success", "failed": "status.error"}.get(st, "dim")
        table.add_row(
            str(s.get("id", "")),
            s.get("domain", "—"),
            f"[{style}]{st}[/]",
            str(s.get("score", "—")),
            (s.get("created_at", "—") or "—")[:19],
        )

    console.print()
    console.print(table)
    console.print()
