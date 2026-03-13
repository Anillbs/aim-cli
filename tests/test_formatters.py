"""Tests for output/formatters.py — JSON, CSV, Markdown output."""

from __future__ import annotations

from aim_cli.output.formatters import format_output, to_csv, to_json, to_markdown


def test_to_json_formats_dict():
    """to_json should produce valid indented JSON."""
    result = to_json({"name": "test", "value": 42})
    assert '"name": "test"' in result
    assert '"value": 42' in result


def test_to_csv_produces_header_and_rows():
    """to_csv should produce a valid CSV with header."""
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    result = to_csv(rows)
    lines = [l.rstrip("\r") for l in result.strip().split("\n")]
    assert lines[0] == "id,name"
    assert "1,Alice" in lines[1]
    assert "2,Bob" in lines[2]


def test_to_csv_empty_list():
    """to_csv with empty list returns empty string."""
    assert to_csv([]) == ""


def test_to_markdown_produces_table():
    """to_markdown should produce a pipe-delimited table."""
    rows = [{"id": 1, "severity": "high"}]
    result = to_markdown(rows)
    assert "| id | severity |" in result
    assert "| --- | --- |" in result
    assert "| 1 | high |" in result


def test_format_output_dispatches_json():
    """format_output with fmt='json' should call to_json."""
    result = format_output({"key": "value"}, "json")
    assert '"key": "value"' in result


def test_format_output_dispatches_csv():
    """format_output with fmt='csv' wraps single dict in list."""
    result = format_output({"id": 1, "name": "x"}, "csv")
    assert "id,name" in result


def test_format_output_dispatches_markdown():
    """format_output with fmt='markdown' wraps single dict in list."""
    result = format_output({"id": 1}, "markdown")
    assert "| id |" in result
