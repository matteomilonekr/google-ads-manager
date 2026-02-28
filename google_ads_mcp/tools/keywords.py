"""Keyword tools for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.tool_inputs import (
    GetKeywordPerformanceInput,
    ListKeywordsInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int, safe_str
from google_ads_mcp.utils.formatting import (
    format_table_markdown,
    micros_to_currency,
)
from google_ads_mcp.utils.pagination import paginate_results


def _build_list_keywords_query(params: ListKeywordsInput) -> str:
    """Build GAQL query for listing keywords."""
    query = (
        "SELECT ad_group_criterion.criterion_id, "
        "ad_group_criterion.keyword.text, "
        "ad_group_criterion.keyword.match_type, "
        "ad_group_criterion.status, "
        "ad_group.id, ad_group.name, "
        "campaign.id, campaign.name "
        "FROM keyword_view"
    )
    where: list[str] = []

    if params.campaign_id:
        where.append(f"campaign.id = {params.campaign_id}")

    if params.ad_group_id:
        where.append(f"ad_group.id = {params.ad_group_id}")

    if where:
        query += " WHERE " + " AND ".join(where)

    query += " ORDER BY ad_group_criterion.keyword.text"
    return query


def _parse_keyword_row(row: Any) -> dict[str, Any]:
    """Extract keyword fields from a GAQL result row."""
    kw = row.ad_group_criterion
    return {
        "id": safe_str(kw.criterion_id),
        "keyword": safe_str(kw.keyword.text),
        "match_type": safe_str(kw.keyword.match_type).replace(
            "KeywordMatchType.", ""
        ),
        "status": safe_str(kw.status).replace(
            "AdGroupCriterionStatus.", ""
        ),
        "ad_group": safe_str(row.ad_group.name),
        "campaign": safe_str(row.campaign.name),
    }


@mcp.tool()
def list_keywords(
    customer_id: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List keywords with optional campaign and ad group filters.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Filter by campaign ID (optional).
        ad_group_id: Filter by ad group ID (optional).
        limit: Max results (1-1000).
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

    params = ListKeywordsInput(**kwargs)
    client = get_client(ctx)
    query = _build_list_keywords_query(params)
    rows = client.query(params.customer_id, query)

    keywords = [_parse_keyword_row(row) for row in rows]
    page, pagination = paginate_results(keywords, params.limit, params.offset)

    if params.response_format.value == "json":
        return json.dumps(
            {"keywords": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["keyword", "match_type", "status", "ad_group", "campaign"]
    headers = {
        "keyword": "Keyword",
        "match_type": "Match",
        "status": "Status",
        "ad_group": "Ad Group",
        "campaign": "Campaign",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Keywords ({pagination.count}/{pagination.total})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} keywords"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


def _build_keyword_performance_query(
    params: GetKeywordPerformanceInput,
) -> str:
    """Build GAQL query for keyword performance metrics."""
    query = (
        "SELECT ad_group_criterion.criterion_id, "
        "ad_group_criterion.keyword.text, "
        "ad_group_criterion.keyword.match_type, "
        "ad_group.name, campaign.name, "
        "metrics.impressions, metrics.clicks, metrics.cost_micros, "
        "metrics.conversions, metrics.ctr, metrics.average_cpc, "
        "metrics.conversions_from_interactions_rate "
        "FROM keyword_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{params.start_date}' AND '{params.end_date}'"
    ]

    if params.campaign_id:
        where.append(f"campaign.id = {params.campaign_id}")

    if params.ad_group_id:
        where.append(f"ad_group.id = {params.ad_group_id}")

    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.cost_micros DESC"
    return query


def _parse_keyword_performance_row(row: Any) -> dict[str, Any]:
    """Extract keyword performance fields from a GAQL result row."""
    kw = row.ad_group_criterion
    m = row.metrics
    return {
        "keyword": safe_str(kw.keyword.text),
        "match_type": safe_str(kw.keyword.match_type).replace(
            "KeywordMatchType.", ""
        ),
        "ad_group": safe_str(row.ad_group.name),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
        "ctr": f"{float(m.ctr or 0) * 100:.2f}%",
        "avg_cpc": micros_to_currency(safe_int(m.average_cpc)),
        "conv_rate": f"{float(m.conversions_from_interactions_rate or 0) * 100:.2f}%",
    }


@mcp.tool()
def get_keyword_performance(
    customer_id: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get performance metrics for keywords over a date range.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Filter by campaign ID (optional).
        ad_group_id: Filter by ad group ID (optional).
        start_date: Start date YYYY-MM-DD (default: 30 days ago).
        end_date: End date YYYY-MM-DD (default: today).
        limit: Max results (1-1000).
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

    params = GetKeywordPerformanceInput(**kwargs)
    client = get_client(ctx)
    query = _build_keyword_performance_query(params)
    rows = client.query(params.customer_id, query)

    perf = [_parse_keyword_performance_row(row) for row in rows]
    page, pagination = paginate_results(perf, params.limit, params.offset)

    if params.response_format.value == "json":
        return json.dumps(
            {"performance": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "keyword", "match_type", "impressions", "clicks",
        "cost", "conversions", "ctr", "avg_cpc",
    ]
    headers = {
        "keyword": "Keyword",
        "match_type": "Match",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
        "ctr": "CTR",
        "avg_cpc": "Avg CPC",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Keyword Performance ({params.start_date} → {params.end_date})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} keywords_"
    )
