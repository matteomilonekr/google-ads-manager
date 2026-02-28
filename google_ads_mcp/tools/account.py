"""Account overview tool for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.tool_inputs import GetAccountOverviewInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int
from google_ads_mcp.utils.formatting import (
    format_response,
    micros_to_currency,
)


def _build_account_performance_query(params: GetAccountOverviewInput) -> str:
    """Build GAQL query for account-level performance."""
    return (
        "SELECT metrics.impressions, metrics.clicks, metrics.cost_micros, "
        "metrics.conversions, metrics.ctr, metrics.average_cpc, "
        "metrics.conversions_from_interactions_rate, metrics.all_conversions, "
        "metrics.interaction_rate "
        "FROM customer "
        f"WHERE segments.date BETWEEN '{params.start_date}' AND '{params.end_date}'"
    )


def _build_campaign_count_query() -> str:
    """Build GAQL query to count campaigns by status."""
    return (
        "SELECT campaign.status, metrics.impressions "
        "FROM campaign "
        "WHERE campaign.status != 'REMOVED'"
    )


@mcp.tool()
def get_account_overview(
    customer_id: str,
    start_date: str = "",
    end_date: str = "",
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get a high-level overview of the Google Ads account with key metrics.

    Args:
        customer_id: Google Ads customer ID.
        start_date: Start date YYYY-MM-DD (default: 30 days ago).
        end_date: End date YYYY-MM-DD (default: today).
        response_format: markdown or json.
    """
    kwargs: dict[str, Any] = {
        "customer_id": customer_id,
        "response_format": response_format,
    }
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date

    params = GetAccountOverviewInput(**kwargs)
    client = get_client(ctx)

    # Fetch account-level metrics
    perf_query = _build_account_performance_query(params)
    perf_rows = client.query(params.customer_id, perf_query)

    # Aggregate metrics across date segments
    total_impressions = 0
    total_clicks = 0
    total_cost_micros = 0
    total_conversions = 0.0

    for row in perf_rows:
        m = row.metrics
        total_impressions += safe_int(m.impressions)
        total_clicks += safe_int(m.clicks)
        total_cost_micros += safe_int(m.cost_micros)
        total_conversions += float(m.conversions or 0)

    # Compute derived metrics
    ctr = (total_clicks / total_impressions * 100) if total_impressions else 0.0
    avg_cpc_micros = (total_cost_micros // total_clicks) if total_clicks else 0
    conv_rate = (total_conversions / total_clicks * 100) if total_clicks else 0.0

    # Fetch campaign counts
    camp_query = _build_campaign_count_query()
    camp_rows = client.query(params.customer_id, camp_query)

    enabled_count = 0
    paused_count = 0
    for row in camp_rows:
        status = str(row.campaign.status)
        if "ENABLED" in status:
            enabled_count += 1
        elif "PAUSED" in status:
            paused_count += 1

    overview = {
        "period": f"{params.start_date} → {params.end_date}",
        "campaigns": {
            "active": enabled_count,
            "paused": paused_count,
            "total": enabled_count + paused_count,
        },
        "metrics": {
            "impressions": f"{total_impressions:,}",
            "clicks": f"{total_clicks:,}",
            "cost": micros_to_currency(total_cost_micros),
            "conversions": round(total_conversions, 2),
            "ctr": f"{ctr:.2f}%",
            "avg_cpc": micros_to_currency(avg_cpc_micros),
            "conversion_rate": f"{conv_rate:.2f}%",
        },
    }

    if params.response_format.value == "json":
        return json.dumps(overview, indent=2, ensure_ascii=False)

    return format_response(overview, "markdown", "Account Overview")
