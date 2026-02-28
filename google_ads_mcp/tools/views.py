"""Performance view tools for Google Ads MCP server (Phase 3)."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int, safe_str, safe_float
from google_ads_mcp.utils.formatting import format_table_markdown, micros_to_currency
from google_ads_mcp.utils.pagination import paginate_results


def _default_dates(start: str, end: str) -> tuple[str, str]:
    """Return validated date range, defaulting to last 30 days."""
    if not end:
        end = date.today().isoformat()
    if not start:
        start = (date.today() - timedelta(days=30)).isoformat()
    return start, end


# ---------------------------------------------------------------------------
# Geographic View
# ---------------------------------------------------------------------------

def _build_geographic_view_query(
    cid: str,
    start: str,
    end: str,
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for geographic view."""
    query = (
        "SELECT geographic_view.country_criterion_id, "
        "geographic_view.location_type, "
        "campaign.name, "
        "metrics.impressions, metrics.clicks, "
        "metrics.cost_micros, metrics.conversions "
        "FROM geographic_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start}' AND '{end}'"
    ]
    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")
    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_geographic_row(row: Any) -> dict[str, Any]:
    """Extract geographic view fields from a GAQL result row."""
    geo = row.geographic_view
    m = row.metrics
    return {
        "country_criterion_id": safe_str(geo.country_criterion_id),
        "location_type": safe_str(geo.location_type),
        "campaign": safe_str(row.campaign.name),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
    }


@mcp.tool()
def gads_geographic_view(
    customer_id: str,
    campaign_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get location-based performance data from geographic view.

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
    start, end = _default_dates(start_date, end_date)
    client = get_client(ctx)
    query = _build_geographic_view_query(cid, start, end, campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_geographic_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"geographic_data": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "country_criterion_id", "location_type", "campaign",
        "impressions", "clicks", "cost", "conversions",
    ]
    headers = {
        "country_criterion_id": "Country ID",
        "location_type": "Location Type",
        "campaign": "Campaign",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Geographic View ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} locations"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


# ---------------------------------------------------------------------------
# Shopping Performance View
# ---------------------------------------------------------------------------

def _build_shopping_performance_query(
    cid: str,
    start: str,
    end: str,
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for shopping performance view."""
    query = (
        "SELECT segments.product_item_id, "
        "segments.product_title, "
        "segments.product_brand, "
        "segments.product_category_level1, "
        "metrics.impressions, metrics.clicks, "
        "metrics.cost_micros, metrics.conversions "
        "FROM shopping_performance_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start}' AND '{end}'"
    ]
    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")
    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_shopping_performance_row(row: Any) -> dict[str, Any]:
    """Extract shopping performance fields from a GAQL result row."""
    seg = row.segments
    m = row.metrics
    return {
        "product_item_id": safe_str(seg.product_item_id),
        "product_title": safe_str(seg.product_title),
        "product_brand": safe_str(seg.product_brand),
        "product_category_l1": safe_str(seg.product_category_level1),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
    }


@mcp.tool()
def gads_shopping_performance_view(
    customer_id: str,
    campaign_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get product-level shopping performance data.

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
    start, end = _default_dates(start_date, end_date)
    client = get_client(ctx)
    query = _build_shopping_performance_query(cid, start, end, campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_shopping_performance_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"shopping_performance": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "product_item_id", "product_title", "product_brand",
        "impressions", "clicks", "cost", "conversions",
    ]
    headers = {
        "product_item_id": "Item ID",
        "product_title": "Title",
        "product_brand": "Brand",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Shopping Performance ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} products"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


# ---------------------------------------------------------------------------
# Display Keyword View
# ---------------------------------------------------------------------------

def _build_display_keyword_view_query(
    cid: str,
    start: str,
    end: str,
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for display keyword view."""
    query = (
        "SELECT display_keyword_view.resource_name, "
        "ad_group_criterion.display_name, "
        "ad_group_criterion.keyword.text, "
        "metrics.impressions, metrics.clicks, "
        "metrics.cost_micros, metrics.conversions "
        "FROM display_keyword_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start}' AND '{end}'"
    ]
    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")
    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_display_keyword_row(row: Any) -> dict[str, Any]:
    """Extract display keyword view fields from a GAQL result row."""
    dkv = row.display_keyword_view
    agc = row.ad_group_criterion
    m = row.metrics
    return {
        "resource_name": safe_str(dkv.resource_name),
        "display_name": safe_str(agc.display_name),
        "keyword_text": safe_str(agc.keyword.text),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
    }


@mcp.tool()
def gads_display_keyword_view(
    customer_id: str,
    campaign_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get display keyword performance data.

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
    start, end = _default_dates(start_date, end_date)
    client = get_client(ctx)
    query = _build_display_keyword_view_query(cid, start, end, campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_display_keyword_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"display_keywords": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "display_name", "keyword_text",
        "impressions", "clicks", "cost", "conversions",
    ]
    headers = {
        "display_name": "Display Name",
        "keyword_text": "Keyword",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Display Keyword View ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} keywords"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


# ---------------------------------------------------------------------------
# Topic View
# ---------------------------------------------------------------------------

def _build_topic_view_query(
    cid: str,
    start: str,
    end: str,
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for topic view."""
    query = (
        "SELECT topic_view.resource_name, "
        "ad_group_criterion.topic.path, "
        "metrics.impressions, metrics.clicks, "
        "metrics.cost_micros, metrics.conversions "
        "FROM topic_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start}' AND '{end}'"
    ]
    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")
    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_topic_row(row: Any) -> dict[str, Any]:
    """Extract topic view fields from a GAQL result row."""
    tv = row.topic_view
    agc = row.ad_group_criterion
    m = row.metrics
    topic_path = agc.topic.path
    # Path may be a list of path components; join them
    if isinstance(topic_path, (list, tuple)):
        path_str = " > ".join(safe_str(p) for p in topic_path)
    else:
        path_str = safe_str(topic_path)
    return {
        "resource_name": safe_str(tv.resource_name),
        "topic_path": path_str,
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
    }


@mcp.tool()
def gads_topic_view(
    customer_id: str,
    campaign_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get topic targeting performance data.

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
    start, end = _default_dates(start_date, end_date)
    client = get_client(ctx)
    query = _build_topic_view_query(cid, start, end, campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_topic_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"topics": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "topic_path", "impressions", "clicks", "cost", "conversions",
    ]
    headers = {
        "topic_path": "Topic Path",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Topic View ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} topics"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


# ---------------------------------------------------------------------------
# User Location View
# ---------------------------------------------------------------------------

def _build_user_location_view_query(
    cid: str,
    start: str,
    end: str,
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for user location view."""
    query = (
        "SELECT user_location_view.country_criterion_id, "
        "user_location_view.targeting_location, "
        "metrics.impressions, metrics.clicks, "
        "metrics.cost_micros, metrics.conversions "
        "FROM user_location_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start}' AND '{end}'"
    ]
    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")
    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.impressions DESC"
    return query


def _parse_user_location_row(row: Any) -> dict[str, Any]:
    """Extract user location view fields from a GAQL result row."""
    ulv = row.user_location_view
    m = row.metrics
    return {
        "country_criterion_id": safe_str(ulv.country_criterion_id),
        "targeting_location": safe_str(ulv.targeting_location),
        "impressions": safe_int(m.impressions),
        "clicks": safe_int(m.clicks),
        "cost": micros_to_currency(safe_int(m.cost_micros)),
        "conversions": round(float(m.conversions or 0), 2),
    }


@mcp.tool()
def gads_user_location_view(
    customer_id: str,
    campaign_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get user location performance data showing where users are physically located.

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
    start, end = _default_dates(start_date, end_date)
    client = get_client(ctx)
    query = _build_user_location_view_query(cid, start, end, campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_user_location_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"user_locations": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "country_criterion_id", "targeting_location",
        "impressions", "clicks", "cost", "conversions",
    ]
    headers = {
        "country_criterion_id": "Country ID",
        "targeting_location": "Targeting Location",
        "impressions": "Impr.",
        "clicks": "Clicks",
        "cost": "Cost",
        "conversions": "Conv.",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## User Location View ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} user locations"
        f"{' (more available)' if pagination.has_more else ''}_"
    )


# ---------------------------------------------------------------------------
# Click View
# ---------------------------------------------------------------------------

def _build_click_view_query(
    cid: str,
    start: str,
    end: str,
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for click view."""
    query = (
        "SELECT click_view.gclid, "
        "click_view.area_of_interest.city, "
        "click_view.area_of_interest.country, "
        "click_view.campaign_location_target, "
        "segments.ad_network_type, "
        "segments.device, "
        "metrics.clicks "
        "FROM click_view"
    )
    where: list[str] = [
        f"segments.date BETWEEN '{start}' AND '{end}'"
    ]
    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")
    query += " WHERE " + " AND ".join(where)
    query += " ORDER BY metrics.clicks DESC"
    return query


def _parse_click_row(row: Any) -> dict[str, Any]:
    """Extract click view fields from a GAQL result row."""
    cv = row.click_view
    seg = row.segments
    m = row.metrics
    return {
        "gclid": safe_str(cv.gclid),
        "city": safe_str(cv.area_of_interest.city),
        "country": safe_str(cv.area_of_interest.country),
        "campaign_location_target": safe_str(cv.campaign_location_target),
        "ad_network_type": safe_str(seg.ad_network_type),
        "device": safe_str(seg.device),
        "clicks": safe_int(m.clicks),
    }


@mcp.tool()
def gads_click_view(
    customer_id: str,
    campaign_id: str | None = None,
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get click-level data including GCLID, location, and device info.

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
    start, end = _default_dates(start_date, end_date)
    client = get_client(ctx)
    query = _build_click_view_query(cid, start, end, campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_click_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"clicks": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "gclid", "city", "country", "ad_network_type", "device", "clicks",
    ]
    headers = {
        "gclid": "GCLID",
        "city": "City",
        "country": "Country",
        "ad_network_type": "Network",
        "device": "Device",
        "clicks": "Clicks",
    }
    table = format_table_markdown(page, columns, headers)
    return (
        f"## Click View ({start} \u2192 {end})\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} clicks"
        f"{' (more available)' if pagination.has_more else ''}_"
    )
