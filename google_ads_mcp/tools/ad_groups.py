"""Ad group tools for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.tool_inputs import (
    GetAdGroupPerformanceInput,
    ListAdGroupsInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import (
    AD_GROUP_STATUS_MAP,
    get_client,
    safe_int,
    safe_str,
)
from google_ads_mcp.utils.formatting import (
    format_table_markdown,
    micros_to_currency,
)
from google_ads_mcp.utils.pagination import paginate_results


def _build_list_ad_groups_query(params: ListAdGroupsInput) -> str:
    """Build GAQL query for listing ad groups."""
    query = (
        "SELECT ad_group.id, ad_group.name, ad_group.status, "
        "ad_group.type, campaign.id, campaign.name "
        "FROM ad_group"
    )
    where: list[str] = []

    if params.campaign_id:
        where.append(f"campaign.id = {params.campaign_id}")

    if params.status.value != "all":
        gaql_status = AD_GROUP_STATUS_MAP[params.status.value]
        where.append(f"ad_group.status = '{gaql_status}'")

    if where:
        query += " WHERE " + " AND ".join(where)

    query += " ORDER BY ad_group.name"
    return query


def _parse_ad_group_row(row: Any) -> dict[str, Any]:
    """Extract ad group fields from a GAQL result row."""
    ag = row.ad_group
    camp = row.campaign
    return {
        "id": safe_str(ag.id),
        "name": safe_str(ag.name),
        "status": safe_str(ag.status).replace("AdGroupStatus.", ""),
        "type": safe_str(ag.type_).replace("AdGroupType.", ""),
        "campaign_id": safe_str(camp.id),
        "campaign_name": safe_str(camp.name),
    }


@mcp.tool()
def list_ad_groups(
    customer_id: str,
    campaign_id: str | None = None,
    status: str = "all",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List ad groups with optional campaign and status filters.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Filter by campaign ID (optional).
        status: Filter by status: all, enabled, paused, removed.
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

    params = ListAdGroupsInput(**kwargs)
    client = get_client(ctx)
    query = _build_list_ad_groups_query(params)
    rows = client.query(params.customer_id, query)

    ad_groups = [_parse_ad_group_row(row) for row in rows]
    page, pagination = paginate_results(ad_groups, params.limit, params.offset)

    if params.response_format.value == "json":
        return json.dumps(
            {"ad_groups": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["id", "name", "status", "type", "campaign_name"]
    headers = {
        "id": "ID",
        "name": "Ad Group",
        "status": "Status",
        "type": "Type",
        "campaign_name": "Campaign",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Ad Groups ({pagination.count}/{pagination.total})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} ad groups"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


def _build_ad_group_performance_query(
    params: GetAdGroupPerformanceInput,
) -> str:
    """Build GAQL query for ad group performance metrics."""
    query = (
        "SELECT ad_group.id, ad_group.name, ad_group.status, "
        "campaign.name, "
        "metrics.impressions, metrics.clicks, metrics.cost_micros, "
        "metrics.conversions, metrics.ctr, metrics.average_cpc, "
        "metrics.conversions_from_interactions_rate "
        "FROM ad_group"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{params.start_date}' AND '{params.end_date}'"
    ]

    if params.campaign_id:
        where.append(f"campaign.id = {params.campaign_id}")

    if params.ad_group_id:
        where.append(f"ad_group.id = {params.ad_group_id}")

    if params.status.value != "all":
        gaql_status = AD_GROUP_STATUS_MAP[params.status.value]
        where.append(f"ad_group.status = '{gaql_status}'")

    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.cost_micros DESC"
    return query


def _parse_ad_group_performance_row(row: Any) -> dict[str, Any]:
    """Extract ad group performance fields from a GAQL result row."""
    ag = row.ad_group
    m = row.metrics
    return {
        "id": safe_str(ag.id),
        "name": safe_str(ag.name),
        "campaign": safe_str(row.campaign.name),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
        "ctr": f"{float(m.ctr or 0) * 100:.2f}%",
        "avg_cpc": micros_to_currency(safe_int(m.average_cpc)),
        "conv_rate": f"{float(m.conversions_from_interactions_rate or 0) * 100:.2f}%",
    }


@mcp.tool()
def get_ad_group_performance(
    customer_id: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    status: str = "enabled",
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get performance metrics for ad groups over a date range.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Filter by campaign ID (optional).
        ad_group_id: Specific ad group ID (optional).
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
    if ad_group_id:
        kwargs["ad_group_id"] = ad_group_id
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date

    params = GetAdGroupPerformanceInput(**kwargs)
    client = get_client(ctx)
    query = _build_ad_group_performance_query(params)
    rows = client.query(params.customer_id, query)

    perf = [_parse_ad_group_performance_row(row) for row in rows]
    page, pagination = paginate_results(perf, params.limit, params.offset)

    if params.response_format.value == "json":
        return json.dumps(
            {"performance": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "name", "campaign", "impressions", "clicks",
        "cost", "conversions", "ctr", "avg_cpc",
    ]
    headers = {
        "name": "Ad Group",
        "campaign": "Campaign",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
        "ctr": "CTR",
        "avg_cpc": "Avg CPC",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Ad Group Performance ({params.start_date} → {params.end_date})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} ad groups_"
    )
