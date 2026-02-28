"""Audience tools for Google Ads MCP server."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int, safe_str
from google_ads_mcp.utils.formatting import (
    format_table_markdown,
    micros_to_currency,
)
from google_ads_mcp.utils.pagination import paginate_results


def _default_dates() -> tuple[str, str]:
    """Return default (start_date, end_date) covering the last 30 days."""
    end = date.today()
    start = end - timedelta(days=30)
    return start.isoformat(), end.isoformat()


def _build_list_audiences_query(
    cid: str,
    campaign_id: str | None,
    start_date: str,
    end_date: str,
) -> str:
    """Build GAQL query for listing audience segments."""
    query = (
        "SELECT campaign_audience_view.resource_name, "
        "campaign.name, "
        "campaign_criterion.criterion_id, "
        "metrics.impressions, metrics.clicks, "
        "metrics.cost_micros, metrics.conversions "
        "FROM campaign_audience_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start_date}' AND '{end_date}'"
    ]

    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")

    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_audience_row(row: Any) -> dict[str, Any]:
    """Extract audience fields from a GAQL result row."""
    m = row.metrics
    return {
        "resource_name": safe_str(row.campaign_audience_view.resource_name),
        "campaign": safe_str(row.campaign.name),
        "criterion_id": safe_str(row.campaign_criterion.criterion_id),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
    }


@mcp.tool()
def gads_list_audiences(
    customer_id: str,
    campaign_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List audience segments with targeting info and performance metrics.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        campaign_id: Filter by campaign ID (optional).
        start_date: Start date YYYY-MM-DD (default: 30 days ago).
        end_date: End date YYYY-MM-DD (default: today).
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    default_start, default_end = _default_dates()
    start = start_date or default_start
    end = end_date or default_end

    client = get_client(ctx)
    query = _build_list_audiences_query(cid, campaign_id, start, end)
    rows = client.query(cid, query)

    audiences = [_parse_audience_row(row) for row in rows]
    page, pagination = paginate_results(audiences, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"audiences": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    columns = [
        "criterion_id", "campaign", "impressions", "clicks",
        "cost", "conversions",
    ]
    headers = {
        "criterion_id": "Criterion ID",
        "campaign": "Campaign",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Audience Segments ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} audiences"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


def _build_list_user_interests_query(
    taxonomy_type: str | None,
) -> str:
    """Build GAQL query for listing user interest categories."""
    query = (
        "SELECT user_interest.user_interest_id, "
        "user_interest.name, "
        "user_interest.taxonomy_type, "
        "user_interest.availabilities "
        "FROM user_interest"
    )
    where: list[str] = []

    if taxonomy_type:
        upper = taxonomy_type.upper()
        where.append(f"user_interest.taxonomy_type = '{upper}'")

    if where:
        query += " WHERE " + " AND ".join(where)

    query += " ORDER BY user_interest.name"
    return query


def _parse_user_interest_row(row: Any) -> dict[str, Any]:
    """Extract user interest fields from a GAQL result row."""
    ui = row.user_interest
    return {
        "id": safe_str(ui.user_interest_id),
        "name": safe_str(ui.name),
        "taxonomy_type": safe_str(ui.taxonomy_type).replace(
            "UserInterestTaxonomyType.", ""
        ),
        "availabilities": safe_str(ui.availabilities),
    }


@mcp.tool()
def gads_list_user_interests(
    customer_id: str,
    taxonomy_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List available user interest categories for audience targeting.

    Args:
        customer_id: Google Ads customer ID.
        taxonomy_type: Filter by type: AFFINITY or IN_MARKET (optional, returns all if omitted).
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_list_user_interests_query(taxonomy_type)
    rows = client.query(cid, query)

    interests = [_parse_user_interest_row(row) for row in rows]
    page, pagination = paginate_results(interests, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"user_interests": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    columns = ["id", "name", "taxonomy_type"]
    headers = {
        "id": "ID",
        "name": "Name",
        "taxonomy_type": "Type",
    }
    table = format_table_markdown(page, columns, headers)
    filter_label = f" ({taxonomy_type.upper()})" if taxonomy_type else ""
    return (
        f"## User Interests{filter_label}\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} interests"
        f"{' (more available)' if pagination.has_more else ''}_"
    )
