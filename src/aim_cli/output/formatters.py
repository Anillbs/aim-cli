"""Output format dispatcher — JSON, SARIF, CSV, Markdown.

When --format is specified, the CLI writes machine-readable output to stdout
instead of Rich tables.  This module handles the conversion.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any


def to_json(data: Any) -> str:
    """Pretty-print JSON to stdout."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def to_csv(rows: list[dict[str, Any]], fields: list[str] | None = None) -> str:
    """Convert list of dicts to CSV string."""
    if not rows:
        return ""
    if fields is None:
        fields = list(rows[0].keys())

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def to_markdown(rows: list[dict[str, Any]], fields: list[str] | None = None) -> str:
    """Convert list of dicts to a Markdown table."""
    if not rows:
        return ""
    if fields is None:
        fields = list(rows[0].keys())

    header = "| " + " | ".join(fields) + " |"
    sep = "| " + " | ".join("---" for _ in fields) + " |"
    lines = [header, sep]
    for row in rows:
        vals = [str(row.get(f, "")) for f in fields]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def format_output(
    data: Any,
    fmt: str,
    *,
    fields: list[str] | None = None,
) -> str:
    """Dispatch to the appropriate formatter.

    fmt: "json", "csv", "markdown"
    """
    if fmt == "json":
        return to_json(data)
    if fmt == "csv":
        rows = data if isinstance(data, list) else [data]
        return to_csv(rows, fields)
    if fmt == "markdown":
        rows = data if isinstance(data, list) else [data]
        return to_markdown(rows, fields)
    return to_json(data)
