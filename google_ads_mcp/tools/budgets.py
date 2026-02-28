"""Strategy and budget read tools for Google Ads MCP server (Phase 4)."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int, safe_str, safe_float
from google_ads_mcp.utils.formatting import format_table_markdown, micros_to_currency
from google_ads_mcp.utils.pagination import paginate_results


# ---------------------------------------------------------------------------
# Campaign Budgets
# ---------------------------------------------------------------------------

def _build_list_campaign_budgets_query() -> str:
    """Build GAQL query for listing campaign budgets."""
    return (
        "SELECT campaign_budget.id, "
        "campaign_budget.name, "
        "campaign_budget.amount_micros, "
        "campaign_budget.delivery_method, "
        "campaign_budget.status, "
        "campaign_budget.type, "
        "campaign_budget.explicitly_shared, "
        "campaign_budget.total_amount_micros, "
        "campaign_budget.recommended_budget_amount_micros "
        "FROM campaign_budget"
    )


def _parse_budget_row(row: Any) -> dict[str, Any]:
    """Extract campaign budget fields from a GAQL result row."""
    b = row.campaign_budget
    return {
        "id": safe_str(b.id),
        "name": safe_str(b.name),
        "amount": micros_to_currency(safe_int(b.amount_micros)),
        "amount_micros": safe_int(b.amount_micros),
        "delivery_method": safe_str(b.delivery_method),
        "status": safe_str(b.status),
        "type": safe_str(b.type),
        "explicitly_shared": safe_str(b.explicitly_shared),
        "total_amount": micros_to_currency(safe_int(b.total_amount_micros)),
        "recommended_amount": micros_to_currency(
            safe_int(b.recommended_budget_amount_micros)
        ),
    }


@mcp.tool()
def gads_list_campaign_budgets(
    customer_id: str,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List campaign budgets with detailed configuration.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_list_campaign_budgets_query()
    rows = client.query(cid, query)

    parsed = [_parse_budget_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"budgets": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "id", "name", "amount", "delivery_method",
        "status", "type", "recommended_amount",
    ]
    headers = {
        "id": "ID",
        "name": "Name",
        "amount": "Daily Budget",
        "delivery_method": "Delivery",
        "status": "Status",
        "type": "Type",
        "recommended_amount": "Recommended",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Campaign Budgets ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} budgets"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# Campaign Bidding Strategies
# ---------------------------------------------------------------------------

def _build_bidding_strategies_query(
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for campaign-level bidding strategies."""
    query = (
        "SELECT campaign.id, campaign.name, "
        "campaign.bidding_strategy_type, "
        "campaign.bidding_strategy, "
        "campaign.target_cpa.target_cpa_micros, "
        "campaign.maximize_conversions.target_cpa_micros, "
        "campaign.target_roas.target_roas, "
        "campaign.maximize_conversion_value.target_roas "
        "FROM campaign "
        "WHERE campaign.status != 'REMOVED'"
    )
    if campaign_id:
        query += f" AND campaign.id = {campaign_id}"
    query += " ORDER BY campaign.name"
    return query


def _parse_bidding_strategy_row(row: Any) -> dict[str, Any]:
    """Extract bidding strategy fields from a GAQL result row."""
    c = row.campaign
    target_cpa_micros = safe_int(
        getattr(c.target_cpa, "target_cpa_micros", 0) or 0
    )
    max_conv_cpa_micros = safe_int(
        getattr(c.maximize_conversions, "target_cpa_micros", 0) or 0
    )
    target_roas_val = safe_float(
        getattr(c.target_roas, "target_roas", 0) or 0
    )
    max_conv_value_roas = safe_float(
        getattr(c.maximize_conversion_value, "target_roas", 0) or 0
    )

    # Determine the effective CPA target
    effective_cpa_micros = target_cpa_micros or max_conv_cpa_micros
    # Determine the effective ROAS target
    effective_roas = target_roas_val or max_conv_value_roas

    return {
        "id": safe_str(c.id),
        "name": safe_str(c.name),
        "bidding_strategy_type": safe_str(c.bidding_strategy_type).replace(
            "BiddingStrategyType.", ""
        ),
        "bidding_strategy": safe_str(c.bidding_strategy),
        "target_cpa": micros_to_currency(effective_cpa_micros) if effective_cpa_micros else "-",
        "target_roas": f"{effective_roas:.2f}" if effective_roas else "-",
    }


@mcp.tool()
def gads_get_bidding_strategies(
    customer_id: str,
    campaign_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get campaign-level bidding strategy configuration.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        campaign_id: Filter by specific campaign ID (optional).
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_bidding_strategies_query(campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_bidding_strategy_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"bidding_strategies": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "id", "name", "bidding_strategy_type", "target_cpa", "target_roas",
    ]
    headers = {
        "id": "ID",
        "name": "Campaign",
        "bidding_strategy_type": "Strategy",
        "target_cpa": "Target CPA",
        "target_roas": "Target ROAS",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Bidding Strategies ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} campaigns"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# Ad Group Bidding Strategies
# ---------------------------------------------------------------------------

def _build_ad_group_bidding_query(
    campaign_id: str | None = None,
) -> str:
    """Build GAQL query for ad group-level bidding info."""
    query = (
        "SELECT ad_group.id, ad_group.name, "
        "ad_group.cpc_bid_micros, "
        "ad_group.target_cpa_micros, "
        "ad_group.effective_target_cpa_micros, "
        "ad_group.effective_target_roas "
        "FROM ad_group "
        "WHERE ad_group.status != 'REMOVED'"
    )
    if campaign_id:
        query += f" AND campaign.id = {campaign_id}"
    query += " ORDER BY ad_group.name"
    return query


def _parse_ad_group_bidding_row(row: Any) -> dict[str, Any]:
    """Extract ad group bidding fields from a GAQL result row."""
    ag = row.ad_group
    return {
        "id": safe_str(ag.id),
        "name": safe_str(ag.name),
        "cpc_bid": micros_to_currency(safe_int(ag.cpc_bid_micros)),
        "target_cpa": micros_to_currency(safe_int(ag.target_cpa_micros)),
        "effective_target_cpa": micros_to_currency(
            safe_int(ag.effective_target_cpa_micros)
        ),
        "effective_target_roas": f"{safe_float(ag.effective_target_roas):.2f}",
    }


@mcp.tool()
def gads_get_ad_group_bidding_strategies(
    customer_id: str,
    campaign_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Get ad group-level bidding information including CPC bids and targets.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        campaign_id: Filter by campaign ID (optional).
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_ad_group_bidding_query(campaign_id)
    rows = client.query(cid, query)

    parsed = [_parse_ad_group_bidding_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"ad_group_bidding": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "id", "name", "cpc_bid", "target_cpa",
        "effective_target_cpa", "effective_target_roas",
    ]
    headers = {
        "id": "ID",
        "name": "Ad Group",
        "cpc_bid": "CPC Bid",
        "target_cpa": "Target CPA",
        "effective_target_cpa": "Eff. CPA",
        "effective_target_roas": "Eff. ROAS",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Ad Group Bidding ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} ad groups"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# Change History
# ---------------------------------------------------------------------------

def _build_change_history_query(
    resource_type: str | None = None,
) -> str:
    """Build GAQL query for change history."""
    query = (
        "SELECT change_status.resource_name, "
        "change_status.resource_type, "
        "change_status.resource_status, "
        "change_status.last_change_date_time "
        "FROM change_status"
    )
    where: list[str] = []
    if resource_type:
        where.append(f"change_status.resource_type = '{resource_type}'")
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY change_status.last_change_date_time DESC"
    return query


def _parse_change_history_row(row: Any) -> dict[str, Any]:
    """Extract change history fields from a GAQL result row."""
    cs = row.change_status
    return {
        "resource_name": safe_str(cs.resource_name),
        "resource_type": safe_str(cs.resource_type),
        "resource_status": safe_str(cs.resource_status),
        "last_change_date_time": safe_str(cs.last_change_date_time),
    }


@mcp.tool()
def gads_list_change_history(
    customer_id: str,
    resource_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List change history for account entities showing recent modifications.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        resource_type: Filter by type: CAMPAIGN, AD_GROUP, AD, CRITERION, etc. (optional).
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_change_history_query(resource_type)
    rows = client.query(cid, query)

    parsed = [_parse_change_history_row(r) for r in rows]
    page, pagination = paginate_results(parsed, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"change_history": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "resource_type", "resource_status",
        "last_change_date_time", "resource_name",
    ]
    headers = {
        "resource_type": "Type",
        "resource_status": "Status",
        "last_change_date_time": "Changed At",
        "resource_name": "Resource",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Change History ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} changes"
        f"{' (more available)' if info['has_more'] else ''}_"
    )
