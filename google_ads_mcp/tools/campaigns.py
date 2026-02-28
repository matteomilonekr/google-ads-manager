"""Campaign tools for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.tool_inputs import (
    GetCampaignPerformanceInput,
    ListCampaignsInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import (
    CAMPAIGN_STATUS_MAP,
    CAMPAIGN_TYPE_MAP,
    get_client,
    safe_int,
    safe_str,
)
from google_ads_mcp.utils.formatting import (
    format_table_markdown,
    micros_to_currency,
)
from google_ads_mcp.utils.pagination import paginate_results


def _build_list_campaigns_query(params: ListCampaignsInput) -> str:
    """Build GAQL query for listing campaigns."""
    query = (
        "SELECT campaign.id, campaign.name, campaign.status, "
        "campaign.advertising_channel_type, campaign.bidding_strategy_type, "
        "campaign.campaign_budget "
        "FROM campaign"
    )
    where: list[str] = []

    if params.status.value != "all":
        gaql_status = CAMPAIGN_STATUS_MAP[params.status.value]
        where.append(f"campaign.status = '{gaql_status}'")

    if params.campaign_type.value != "all":
        gaql_type = CAMPAIGN_TYPE_MAP[params.campaign_type.value]
        where.append(f"campaign.advertising_channel_type = '{gaql_type}'")

    if where:
        query += " WHERE " + " AND ".join(where)

    query += " ORDER BY campaign.name"
    return query


def _parse_campaign_row(row: Any) -> dict[str, Any]:
    """Extract campaign fields from a GAQL result row."""
    campaign = row.campaign
    return {
        "id": safe_str(campaign.id),
        "name": safe_str(campaign.name),
        "status": safe_str(campaign.status).replace("CampaignStatus.", ""),
        "type": safe_str(campaign.advertising_channel_type).replace(
            "AdvertisingChannelType.", ""
        ),
        "bidding_strategy": safe_str(campaign.bidding_strategy_type).replace(
            "BiddingStrategyType.", ""
        ),
        "budget": safe_str(campaign.campaign_budget),
    }


@mcp.tool()
def list_campaigns(
    customer_id: str,
    status: str = "all",
    campaign_type: str = "all",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List Google Ads campaigns with optional status and type filters.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        status: Filter by status: all, enabled, paused, removed.
        campaign_type: Filter by type: all, search, display, shopping, video, performance_max, etc.
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    params = ListCampaignsInput(
        customer_id=customer_id,
        status=status,
        campaign_type=campaign_type,
        limit=limit,
        offset=offset,
        response_format=response_format,
    )
    client = get_client(ctx)
    query = _build_list_campaigns_query(params)
    rows = client.query(params.customer_id, query)

    campaigns = [_parse_campaign_row(row) for row in rows]
    page, pagination = paginate_results(campaigns, params.limit, params.offset)

    if params.response_format.value == "json":
        return json.dumps(
            {"campaigns": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["id", "name", "status", "type", "bidding_strategy"]
    headers = {
        "id": "ID",
        "name": "Name",
        "status": "Status",
        "type": "Type",
        "bidding_strategy": "Bidding",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Campaigns ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} campaigns"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


def _build_campaign_performance_query(
    params: GetCampaignPerformanceInput,
) -> str:
    """Build GAQL query for campaign performance metrics."""
    query = (
        "SELECT campaign.id, campaign.name, campaign.status, "
        "metrics.impressions, metrics.clicks, metrics.cost_micros, "
        "metrics.conversions, metrics.ctr, metrics.average_cpc, "
        "metrics.conversions_from_interactions_rate "
        "FROM campaign"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{params.start_date}' AND '{params.end_date}'"
    ]

    if params.campaign_id:
        where.append(f"campaign.id = {params.campaign_id}")

    if params.status.value != "all":
        gaql_status = CAMPAIGN_STATUS_MAP[params.status.value]
        where.append(f"campaign.status = '{gaql_status}'")

    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.cost_micros DESC"
    return query


def _parse_campaign_performance_row(row: Any) -> dict[str, Any]:
    """Extract performance fields from a GAQL result row."""
    campaign = row.campaign
    m = row.metrics
    return {
        "id": safe_str(campaign.id),
        "name": safe_str(campaign.name),
        "status": safe_str(campaign.status).replace("CampaignStatus.", ""),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
        "ctr": f"{float(m.ctr or 0) * 100:.2f}%",
        "avg_cpc": micros_to_currency(safe_int(m.average_cpc)),
        "conv_rate": f"{float(m.conversions_from_interactions_rate or 0) * 100:.2f}%",
    }


@mcp.tool()
def get_campaign_performance(
    customer_id: str,
    campaign_id: str | None = None,
    status: str = "enabled",
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get performance metrics for campaigns over a date range.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Specific campaign ID (optional, returns all if omitted).
        status: Filter by status: all, enabled, paused, removed.
        start_date: Start date YYYY-MM-DD (default: 30 days ago).
        end_date: End date YYYY-MM-DD (default: today).
        limit: Max results (1-1000).
        offset: Starting offset.
        response_format: markdown or json.
    """
    kwargs: dict[str, Any] = {
        "customer_id": customer_id,
        "status": status,
        "limit": limit,
        "offset": offset,
        "response_format": response_format,
    }
    if campaign_id:
        kwargs["campaign_id"] = campaign_id
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date

    params = GetCampaignPerformanceInput(**kwargs)
    client = get_client(ctx)
    query = _build_campaign_performance_query(params)
    rows = client.query(params.customer_id, query)

    perf = [_parse_campaign_performance_row(row) for row in rows]
    page, pagination = paginate_results(perf, params.limit, params.offset)

    if params.response_format.value == "json":
        return json.dumps(
            {"performance": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "name", "impressions", "clicks", "cost",
        "conversions", "ctr", "avg_cpc", "conv_rate",
    ]
    headers = {
        "name": "Campaign",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
        "ctr": "CTR",
        "avg_cpc": "Avg CPC",
        "conv_rate": "Conv Rate",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Campaign Performance ({params.start_date} → {params.end_date})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} campaigns_"
    )
