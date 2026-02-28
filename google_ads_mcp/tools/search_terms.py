"""Search terms report tool for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.tool_inputs import SearchTermsReportInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int, safe_str
from google_ads_mcp.utils.formatting import (
    format_table_markdown,
    micros_to_currency,
)
from google_ads_mcp.utils.pagination import paginate_results


def _build_search_terms_query(params: SearchTermsReportInput) -> str:
    """Build GAQL query for search terms report."""
    query = (
        "SELECT search_term_view.search_term, "
        "search_term_view.status, "
        "campaign.name, ad_group.name, "
        "metrics.impressions, metrics.clicks, metrics.cost_micros, "
        "metrics.conversions, metrics.ctr, metrics.average_cpc "
        "FROM search_term_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{params.start_date}' AND '{params.end_date}'"
    ]

    if params.campaign_id:
        where.append(f"campaign.id = {params.campaign_id}")

    if params.ad_group_id:
        where.append(f"ad_group.id = {params.ad_group_id}")

    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_search_term_row(row: Any) -> dict[str, Any]:
    """Extract search term fields from a GAQL result row."""
    st = row.search_term_view
    m = row.metrics
    return {
        "search_term": safe_str(st.search_term),
        "status": safe_str(st.status).replace(
            "SearchTermTargetingStatus.", ""
        ),
        "campaign": safe_str(row.campaign.name),
        "ad_group": safe_str(row.ad_group.name),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
        "ctr": f"{float(m.ctr or 0) * 100:.2f}%",
        "avg_cpc": micros_to_currency(safe_int(m.average_cpc)),
    }


@mcp.tool()
def search_terms_report(
    customer_id: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 100,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get search terms report showing actual queries that triggered ads.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Filter by campaign ID (optional).
        ad_group_id: Filter by ad group ID (optional).
        start_date: Start date YYYY-MM-DD (default: 30 days ago).
        end_date: End date YYYY-MM-DD (default: today).
        limit: Max results (1-5000, default 100).
        offset: Starting offset.
        response_format: markdown or json.
    """
    kwargs: dict[str, Any] = {
        "customer_id": customer_id,
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

    params = SearchTermsReportInput(**kwargs)
    client = get_client(ctx)
    query = _build_search_terms_query(params)
    rows = client.query(params.customer_id, query)

    terms = [_parse_search_term_row(row) for row in rows]
    page, pagination = paginate_results(terms, params.limit, params.offset)

    if params.response_format.value == "json":
        return json.dumps(
            {"search_terms": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "search_term", "campaign", "impressions", "clicks",
        "cost", "conversions", "ctr",
    ]
    headers = {
        "search_term": "Search Term",
        "campaign": "Campaign",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
        "ctr": "CTR",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Search Terms Report ({params.start_date} → {params.end_date})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} search terms"
        f"{' (more available)' if pagination.has_more else ''}_"
    )
