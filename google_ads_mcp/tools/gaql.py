"""Custom GAQL query tool for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client
from google_ads_mcp.utils.formatting import format_table_markdown


def _flatten_dict(d: dict, out: dict, prefix: str = "") -> None:
    """Recursively flatten a nested dict into a single-level dict.

    Keys are joined with dots (e.g. 'campaign.name').

    Args:
        d: Source dictionary (possibly nested).
        out: Target dictionary to populate.
        prefix: Current key prefix.
    """
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            _flatten_dict(v, out, key)
        else:
            out[key] = v


@mcp.tool()
def gads_execute_gaql(
    customer_id: str,
    query: str,
    limit: int = 100,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Execute a custom Google Ads Query Language (GAQL) query.

    Only SELECT queries are allowed for safety. This is a powerful tool
    that lets you run any valid GAQL SELECT query against the Google Ads API.

    Args:
        customer_id: Google Ads customer ID.
        query: GAQL SELECT query string.
        limit: Max rows to return (default 100).
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)

    stripped = query.strip()
    if not stripped.upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    client = get_client(ctx)
    rows = client.query(cid, stripped)

    results: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        if i >= limit:
            break
        try:
            row_dict = type(row).to_dict(row)
            results.append(row_dict)
        except Exception:
            results.append({"raw": str(row)})

    if response_format == "json":
        return json.dumps(
            {"results": results, "count": len(results)},
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    if not results:
        return "No results found."

    flat_results: list[dict[str, Any]] = []
    for r in results:
        flat: dict[str, Any] = {}
        _flatten_dict(r, flat)
        flat_results.append(flat)

    if flat_results:
        columns = list(flat_results[0].keys())[:10]
        headers = {c: c for c in columns}
        table = format_table_markdown(flat_results, columns, headers)
        return f"## GAQL Results ({len(results)} rows)\n\n{table}"

    return (
        f"## GAQL Results\n\n"
        f"{len(results)} rows returned. Use json format for full data."
    )
