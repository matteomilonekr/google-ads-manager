"""Label management tools for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_str
from google_ads_mcp.utils.formatting import format_table_markdown
from google_ads_mcp.utils.pagination import paginate_results


# ---------------------------------------------------------------------------
# 1. gads_list_labels
# ---------------------------------------------------------------------------

def _build_list_labels_query() -> str:
    """Build GAQL query for listing all labels."""
    return (
        "SELECT label.id, label.name, label.status, "
        "label.text_label.background_color, label.text_label.description "
        "FROM label "
        "ORDER BY label.name"
    )


def _parse_label_row(row: Any) -> dict[str, Any]:
    """Extract label fields from a GAQL result row."""
    label = row.label
    return {
        "id": safe_str(label.id),
        "name": safe_str(label.name),
        "status": safe_str(label.status).replace("LabelStatus.", ""),
        "background_color": safe_str(label.text_label.background_color),
        "description": safe_str(label.text_label.description),
    }


@mcp.tool()
def gads_list_labels(
    customer_id: str,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List all labels in the Google Ads account.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_list_labels_query()
    rows = client.query(clean_id, query)

    labels = [_parse_label_row(row) for row in rows]
    page, pagination = paginate_results(labels, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"labels": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["id", "name", "status", "background_color", "description"]
    headers = {
        "id": "ID",
        "name": "Name",
        "status": "Status",
        "background_color": "Color",
        "description": "Description",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Labels ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} labels"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# 2. gads_list_campaign_labels
# ---------------------------------------------------------------------------

def _build_campaign_labels_query(
    campaign_id: str | None = None,
    label_id: str | None = None,
) -> str:
    """Build GAQL query for campaign-label associations."""
    query = (
        "SELECT campaign.id, campaign.name, label.id, label.name "
        "FROM campaign_label"
    )
    where: list[str] = []

    if campaign_id:
        where.append(f"campaign.id = {campaign_id}")
    if label_id:
        where.append(f"label.id = {label_id}")

    if where:
        query += " WHERE " + " AND ".join(where)

    return query


def _parse_campaign_label_row(row: Any) -> dict[str, Any]:
    """Extract campaign-label fields from a GAQL result row."""
    return {
        "campaign_id": safe_str(row.campaign.id),
        "campaign_name": safe_str(row.campaign.name),
        "label_id": safe_str(row.label.id),
        "label_name": safe_str(row.label.name),
    }


@mcp.tool()
def gads_list_campaign_labels(
    customer_id: str,
    campaign_id: str | None = None,
    label_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List campaign-label associations.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        campaign_id: Optional campaign ID to filter by.
        label_id: Optional label ID to filter by.
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_campaign_labels_query(campaign_id, label_id)
    rows = client.query(clean_id, query)

    associations = [_parse_campaign_label_row(row) for row in rows]
    page, pagination = paginate_results(associations, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"campaign_labels": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["campaign_id", "campaign_name", "label_id", "label_name"]
    headers = {
        "campaign_id": "Campaign ID",
        "campaign_name": "Campaign",
        "label_id": "Label ID",
        "label_name": "Label",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Campaign Labels ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} associations"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# 3. gads_list_ad_group_labels
# ---------------------------------------------------------------------------

def _build_ad_group_labels_query(
    ad_group_id: str | None = None,
    label_id: str | None = None,
) -> str:
    """Build GAQL query for ad group-label associations."""
    query = (
        "SELECT ad_group.id, ad_group.name, label.id, label.name "
        "FROM ad_group_label"
    )
    where: list[str] = []

    if ad_group_id:
        where.append(f"ad_group.id = {ad_group_id}")
    if label_id:
        where.append(f"label.id = {label_id}")

    if where:
        query += " WHERE " + " AND ".join(where)

    return query


def _parse_ad_group_label_row(row: Any) -> dict[str, Any]:
    """Extract ad group-label fields from a GAQL result row."""
    return {
        "ad_group_id": safe_str(row.ad_group.id),
        "ad_group_name": safe_str(row.ad_group.name),
        "label_id": safe_str(row.label.id),
        "label_name": safe_str(row.label.name),
    }


@mcp.tool()
def gads_list_ad_group_labels(
    customer_id: str,
    ad_group_id: str | None = None,
    label_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List ad group-label associations.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        ad_group_id: Optional ad group ID to filter by.
        label_id: Optional label ID to filter by.
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_ad_group_labels_query(ad_group_id, label_id)
    rows = client.query(clean_id, query)

    associations = [_parse_ad_group_label_row(row) for row in rows]
    page, pagination = paginate_results(associations, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"ad_group_labels": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["ad_group_id", "ad_group_name", "label_id", "label_name"]
    headers = {
        "ad_group_id": "Ad Group ID",
        "ad_group_name": "Ad Group",
        "label_id": "Label ID",
        "label_name": "Label",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Ad Group Labels ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} associations"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# 4. gads_list_ad_group_ad_labels
# ---------------------------------------------------------------------------

def _build_ad_group_ad_labels_query(
    label_id: str | None = None,
) -> str:
    """Build GAQL query for ad-label associations."""
    query = (
        "SELECT ad_group_ad.ad.id, ad_group_ad.ad.name, "
        "label.id, label.name "
        "FROM ad_group_ad_label"
    )
    where: list[str] = []

    if label_id:
        where.append(f"label.id = {label_id}")

    if where:
        query += " WHERE " + " AND ".join(where)

    return query


def _parse_ad_group_ad_label_row(row: Any) -> dict[str, Any]:
    """Extract ad-label fields from a GAQL result row."""
    return {
        "ad_id": safe_str(row.ad_group_ad.ad.id),
        "ad_name": safe_str(row.ad_group_ad.ad.name),
        "label_id": safe_str(row.label.id),
        "label_name": safe_str(row.label.name),
    }


@mcp.tool()
def gads_list_ad_group_ad_labels(
    customer_id: str,
    label_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List ad-label associations.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        label_id: Optional label ID to filter by.
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_ad_group_ad_labels_query(label_id)
    rows = client.query(clean_id, query)

    associations = [_parse_ad_group_ad_label_row(row) for row in rows]
    page, pagination = paginate_results(associations, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"ad_labels": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["ad_id", "ad_name", "label_id", "label_name"]
    headers = {
        "ad_id": "Ad ID",
        "ad_name": "Ad Name",
        "label_id": "Label ID",
        "label_name": "Label",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Ad Labels ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} associations"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# 5. gads_list_ad_group_criterion_labels
# ---------------------------------------------------------------------------

def _build_ad_group_criterion_labels_query(
    label_id: str | None = None,
) -> str:
    """Build GAQL query for criterion-label associations."""
    query = (
        "SELECT ad_group_criterion.criterion_id, "
        "label.id, label.name "
        "FROM ad_group_criterion_label"
    )
    where: list[str] = []

    if label_id:
        where.append(f"label.id = {label_id}")

    if where:
        query += " WHERE " + " AND ".join(where)

    return query


def _parse_ad_group_criterion_label_row(row: Any) -> dict[str, Any]:
    """Extract criterion-label fields from a GAQL result row."""
    return {
        "criterion_id": safe_str(row.ad_group_criterion.criterion_id),
        "label_id": safe_str(row.label.id),
        "label_name": safe_str(row.label.name),
    }


@mcp.tool()
def gads_list_ad_group_criterion_labels(
    customer_id: str,
    label_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List criterion-label associations.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        label_id: Optional label ID to filter by.
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_ad_group_criterion_labels_query(label_id)
    rows = client.query(clean_id, query)

    associations = [_parse_ad_group_criterion_label_row(row) for row in rows]
    page, pagination = paginate_results(associations, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"criterion_labels": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["criterion_id", "label_id", "label_name"]
    headers = {
        "criterion_id": "Criterion ID",
        "label_id": "Label ID",
        "label_name": "Label",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Criterion Labels ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} associations"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# 6. gads_list_customer_labels
# ---------------------------------------------------------------------------

def _build_customer_labels_query() -> str:
    """Build GAQL query for customer-label associations."""
    return (
        "SELECT customer.id, label.id, label.name "
        "FROM customer_label"
    )


def _parse_customer_label_row(row: Any) -> dict[str, Any]:
    """Extract customer-label fields from a GAQL result row."""
    return {
        "customer_id": safe_str(row.customer.id),
        "label_id": safe_str(row.label.id),
        "label_name": safe_str(row.label.name),
    }


@mcp.tool()
def gads_list_customer_labels(
    customer_id: str,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List customer-label associations.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_customer_labels_query()
    rows = client.query(clean_id, query)

    associations = [_parse_customer_label_row(row) for row in rows]
    page, pagination = paginate_results(associations, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"customer_labels": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["customer_id", "label_id", "label_name"]
    headers = {
        "customer_id": "Customer ID",
        "label_id": "Label ID",
        "label_name": "Label",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Customer Labels ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} associations"
        f"{' (more available)' if info['has_more'] else ''}_"
    )
