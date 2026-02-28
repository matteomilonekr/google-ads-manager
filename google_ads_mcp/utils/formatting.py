"""Response formatting utilities for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any


def micros_to_currency(
    micros: int | None,
    currency: str | None = None,
) -> str:
    """Convert micros (1/1,000,000) to human-readable currency string.

    Args:
        micros: Amount in micros. None returns '-'.
        currency: Optional currency code to append (e.g. 'EUR').

    Returns:
        Formatted currency string.
    """
    if micros is None:
        return "-"
    amount = micros / 1_000_000
    if currency:
        return f"{amount:,.2f} {currency}"
    return f"{amount:.2f}"


def format_percentage(value: float | None) -> str:
    """Format a ratio (0-1) as a percentage string.

    Args:
        value: Ratio value. None returns '-'.

    Returns:
        Formatted percentage string (e.g. '4.56%').
    """
    if value is None:
        return "-"
    return f"{value * 100:.2f}%"


def format_response(
    data: dict[str, Any],
    response_format: str = "markdown",
    title: str | None = None,
) -> str:
    """Format API response data as markdown or JSON.

    Args:
        data: Response data dictionary.
        response_format: 'markdown' or 'json'.
        title: Optional title for markdown output.

    Returns:
        Formatted string.
    """
    if response_format == "json":
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)

    lines: list[str] = []
    if title:
        lines.append(f"# {title}")
        lines.append("")
    lines.append(_dict_to_markdown(data))
    return "\n".join(lines)


def _dict_to_markdown(data: dict[str, Any], indent: int = 0) -> str:
    """Recursively convert a dict to markdown bullet list."""
    lines: list[str] = []
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{prefix}**{key}**:")
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        lines.append(f"{prefix}  - **{k}**: {v}")
                    lines.append("")
                else:
                    lines.append(f"{prefix}  - {item}")
        elif isinstance(value, dict):
            lines.append(f"{prefix}**{key}**:")
            lines.append(_dict_to_markdown(value, indent + 1))
        else:
            lines.append(f"{prefix}- **{key}**: {value}")
    return "\n".join(lines)


def format_table_markdown(
    rows: list[dict[str, Any]],
    columns: list[str],
    headers: dict[str, str] | None = None,
) -> str:
    """Format a list of dicts as a markdown table.

    Args:
        rows: List of row dicts.
        columns: Column keys to include.
        headers: Optional mapping of column key -> display header.

    Returns:
        Markdown table string.
    """
    if not rows:
        return "_Nessun risultato trovato._"

    display_headers = headers or {col: col for col in columns}
    header_row = " | ".join(display_headers.get(c, c) for c in columns)
    separator = " | ".join("---" for _ in columns)
    body_rows = []
    for row in rows:
        cells = [str(row.get(c, "-")) for c in columns]
        body_rows.append(" | ".join(cells))

    return "\n".join([
        f"| {header_row} |",
        f"| {separator} |",
        *[f"| {r} |" for r in body_rows],
    ])
