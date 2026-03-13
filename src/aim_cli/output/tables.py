"""Table builder functions for structured terminal output.

Each function takes data dicts and returns a Rich Table ready for printing.
No data fetching — pure formatting.
"""

from __future__ import annotations

from typing import Any

from rich.table import Table

from aim_cli.output.console import severity_style


def scan_results_table(summary: dict[str, Any], scan_id: int) -> Table:
    """Build the scan results summary table shown after --wait completes."""
    table = Table(
        title=f"SCAN RESULTS — #{scan_id}",
        title_style="bold bright_magenta",
        box=__import__("rich.box", fromlist=["ROUNDED"]).ROUNDED,
        pad_edge=True,
        show_lines=False,
    )
    table.add_column("Metric", style="bold white", min_width=18)
    table.add_column("Value", min_width=12)

    score = summary.get("score", 0)
    score_style = "status.success" if score >= 70 else "status.warning" if score >= 40 else "status.error"
    table.add_row("Security Score", f"[{score_style}]{score}/100[/]")

    vuln_counts = summary.get("vulnerabilities", {})
    for sev in ("critical", "high", "medium", "low"):
        count = vuln_counts.get(sev, 0)
        style = severity_style(sev)
        label = sev.capitalize()
        table.add_row(label, f"[{style}]{count}[/]")

    total = summary.get("total_vulns", 0)
    table.add_row("Total", str(total))

    return table


def vuln_list_table(vulns: list[dict[str, Any]]) -> Table:
    """Build a vulnerability list table."""
    table = Table(
        box=__import__("rich.box", fromlist=["ROUNDED"]).ROUNDED,
        pad_edge=True,
        show_lines=False,
    )
    table.add_column("ID", style="dim", width=6)
    table.add_column("Type", min_width=24)
    table.add_column("Severity", min_width=10)
    table.add_column("URL", max_width=40, overflow="ellipsis")
    table.add_column("Status", min_width=8)

    for v in vulns:
        vid = str(v.get("id", ""))
        vtype = v.get("vuln_type", v.get("title", v.get("code", "—")))
        sev = v.get("severity", v.get("risk", "info")).lower()
        url = v.get("url", "—")
        status = v.get("status", "open")
        style = severity_style(sev)
        table.add_row(vid, vtype, f"[{style}]{sev.upper()}[/]", url, status)

    return table


def vuln_detail_table(vuln: dict[str, Any]) -> Table:
    """Build a single vulnerability detail table."""
    sev = vuln.get("severity", vuln.get("risk", "info")).lower()
    style = severity_style(sev)
    title = vuln.get("vuln_type", vuln.get("title", "Vulnerability"))

    table = Table(
        title=f"{title} — [{style}]{sev.upper()}[/]",
        title_style="bold",
        box=__import__("rich.box", fromlist=["ROUNDED"]).ROUNDED,
        pad_edge=True,
        show_lines=True,
    )
    table.add_column("Field", style="bold white", min_width=12)
    table.add_column("Value", min_width=30)

    table.add_row("ID", str(vuln.get("id", "")))
    table.add_row("URL", vuln.get("url", "—"))
    table.add_row("Severity", f"[{style}]{sev.upper()}[/]")
    table.add_row("Status", vuln.get("status", "open"))

    details = vuln.get("details", {})
    if isinstance(details, dict):
        if details.get("owasp_id"):
            table.add_row("OWASP", details["owasp_id"])
        if details.get("cvss"):
            table.add_row("CVSS", str(details["cvss"]))
        if details.get("recommendation"):
            table.add_row("Recommendation", details["recommendation"][:200])

    return table


def site_list_table(sites: list[dict[str, Any]]) -> Table:
    """Build a sites list table."""
    table = Table(
        box=__import__("rich.box", fromlist=["ROUNDED"]).ROUNDED,
        pad_edge=True,
        show_lines=False,
    )
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name", min_width=16)
    table.add_column("Domain", min_width=24)
    table.add_column("Score", min_width=6)
    table.add_column("Status", min_width=10)

    for s in sites:
        sid = str(s.get("id", ""))
        name = s.get("name", "—")
        domain = s.get("domain", s.get("url", "—"))
        score = s.get("last_score", "—")
        status = s.get("status", "active")
        table.add_row(sid, name, domain, str(score), status)

    return table


def report_list_table(reports: list[dict[str, Any]]) -> Table:
    """Build a reports list table."""
    table = Table(
        box=__import__("rich.box", fromlist=["ROUNDED"]).ROUNDED,
        pad_edge=True,
        show_lines=False,
    )
    table.add_column("ID", style="dim", width=6)
    table.add_column("Scan ID", width=8)
    table.add_column("Type", min_width=12)
    table.add_column("Status", min_width=10)
    table.add_column("Created", min_width=16)

    for r in reports:
        table.add_row(
            str(r.get("id", "")),
            str(r.get("scan_id", "")),
            r.get("type", r.get("template", "—")),
            r.get("status", "—"),
            r.get("created_at", "—")[:19] if r.get("created_at") else "—",
        )

    return table


def doctor_table(checks: list[tuple[bool, str, str]]) -> Table:
    """Build the `aim doctor` diagnostics table.

    checks: list of (passed, label, value) tuples.
    """
    table = Table(
        title="AIM CLI Diagnostics",
        title_style="bold bright_magenta",
        box=__import__("rich.box", fromlist=["ROUNDED"]).ROUNDED,
        pad_edge=True,
        show_lines=False,
    )
    table.add_column("", width=3)
    table.add_column("Check", min_width=24)
    table.add_column("Result", min_width=30)

    for passed, label, value in checks:
        icon = "[status.success]✔[/]" if passed else "[status.error]✖[/]"
        table.add_row(icon, label, value)

    return table
