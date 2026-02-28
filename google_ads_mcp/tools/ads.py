"""Ad group ad tools for Google Ads MCP server."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import (
    AD_GROUP_STATUS_MAP,
    get_client,
    safe_int,
    safe_str,
)
from google_ads_mcp.utils.formatting import format_table_markdown, micros_to_currency
from google_ads_mcp.utils.pagination import paginate_results


def _default_dates(start: str, end: str) -> tuple[str, str]:
    """Return validated date range, defaulting to last 30 days."""
    if not end:
        end = date.today().isoformat()
    if not start:
        start = (date.today() - timedelta(days=30)).isoformat()
    return start, end


def _build_list_ads_query(
    cid: str,
    start: str,
    end: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    status: str = "all",
) -> str:
    """Build GAQL query for listing ad group ads with metrics."""
    query = (
        "SELECT ad_group_ad.ad.id, ad_group_ad.ad.name, "
        "ad_group_ad.ad.type, ad_group_ad.status, "
        "ad_group_ad.policy_summary.approval_status, "
        "ad_group_ad.policy_summary.review_status, "
        "ad_group.id, ad_group.name, campaign.name, "
        "metrics.impressions, metrics.clicks, "
        "metrics.cost_micros, metrics.conversions, metrics.ctr "
        "FROM ad_group_ad"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start}' AND '{end}'"
    ]

    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")

    if ad_group_id:
        where.append(f"ad_group.id = {ad_group_id}")

    if status != "all":
        gaql_status = AD_GROUP_STATUS_MAP[status]
        where.append(f"ad_group_ad.status = '{gaql_status}'")

    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_ad_row(row: Any) -> dict[str, Any]:
    """Extract ad group ad fields from a GAQL result row."""
    ad = row.ad_group_ad.ad
    aga = row.ad_group_ad
    ag = row.ad_group
    m = row.metrics
    return {
        "ad_id": safe_str(ad.id),
        "ad_name": safe_str(ad.name),
        "ad_type": safe_str(ad.type_).replace("AdType.", ""),
        "status": safe_str(aga.status).replace("AdGroupAdStatus.", ""),
        "approval_status": safe_str(aga.policy_summary.approval_status),
        "review_status": safe_str(aga.policy_summary.review_status),
        "ad_group_id": safe_str(ag.id),
        "ad_group_name": safe_str(ag.name),
        "campaign_name": safe_str(row.campaign.name),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
        "ctr": f"{float(m.ctr or 0) * 100:.2f}%",
    }


@mcp.tool()
def gads_list_ad_group_ads(
    customer_id: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    status: str = "all",
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List ads within ad groups with creative details, performance metrics, and policy status.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        campaign_id: Filter by campaign ID (optional).
        ad_group_id: Filter by ad group ID (optional).
        status: Filter by status: all, enabled, paused, removed.
        start_date: Start date YYYY-MM-DD (default: 30 days ago).
        end_date: End date YYYY-MM-DD (default: today).
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    start, end = _default_dates(start_date, end_date)
    client = get_client(ctx)
    query = _build_list_ads_query(cid, start, end, campaign_id, ad_group_id, status)
    rows = client.query(cid, query)

    parsed = [_parse_ad_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"ad_group_ads": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "ad_id", "ad_name", "ad_type", "status", "approval_status",
        "ad_group_name", "campaign_name",
        "impressions", "clicks", "cost", "conversions", "ctr",
    ]
    headers = {
        "ad_id": "Ad ID",
        "ad_name": "Ad Name",
        "ad_type": "Type",
        "status": "Status",
        "approval_status": "Approval",
        "ad_group_name": "Ad Group",
        "campaign_name": "Campaign",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
        "ctr": "CTR",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Ad Group Ads ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} ads"
        f"{' (more available)' if pagination.has_more else ''}_"
    )
