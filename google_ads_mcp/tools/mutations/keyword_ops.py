"""Keyword mutation tools (negative, positive, update)."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import (
    build_add_keywords_operations,
    build_negative_keyword_operations,
    build_update_keyword_operation,
)
from google_ads_mcp.models.creation_inputs import AddKeywordsInput, UpdateKeywordInput
from google_ads_mcp.models.mutation_inputs import AddNegativeKeywordsInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_add_negative_keywords(
    customer_id: str,
    level: str,
    campaign_id: str | None = None,
    ad_group_id: str | None = None,
    keywords: list[str] = [],
    match_type: str = "exact",
    ctx: Context = None,
) -> str:
    """Add negative keywords to a campaign or ad group.

    Args:
        customer_id: Google Ads customer ID.
        level: Level to add negatives — campaign or ad_group.
        campaign_id: Campaign ID (required if level=campaign).
        ad_group_id: Ad group ID (required if level=ad_group).
        keywords: List of keyword texts to add as negatives (max 20).
        match_type: Match type — exact, phrase, or broad.
    """
    params = AddNegativeKeywordsInput(
        customer_id=customer_id,
        level=level,
        campaign_id=campaign_id,
        ad_group_id=ad_group_id,
        keywords=keywords,
        match_type=match_type,
    )
    client = get_client(ctx)
    parent_id = (
        params.campaign_id
        if params.level.value == "campaign"
        else params.ad_group_id
    )
    operations = build_negative_keyword_operations(
        client.client,
        params.customer_id,
        params.level.value,
        parent_id,
        params.keywords,
        params.match_type.value,
    )
    client.mutate(params.customer_id, operations, partial_failure=True)
    count = len(params.keywords)
    return (
        f"Added {count} negative keyword(s) at {params.level.value} level "
        f"({params.match_type.value} match): {', '.join(params.keywords)}"
    )


@mcp.tool()
def gads_add_keywords(
    customer_id: str,
    ad_group_id: str,
    keywords: list[str] = [],
    match_type: str = "broad",
    cpc_bid_micros: int | None = None,
    ctx: Context = None,
) -> str:
    """Add positive keywords to an ad group.

    Args:
        customer_id: Google Ads customer ID.
        ad_group_id: Ad group ID.
        keywords: Keywords to add (max 20 per call).
        match_type: Match type — exact, phrase, or broad.
        cpc_bid_micros: Keyword-level CPC bid in micros (optional).
    """
    params = AddKeywordsInput(
        customer_id=customer_id, ad_group_id=ad_group_id,
        keywords=keywords, match_type=match_type, cpc_bid_micros=cpc_bid_micros,
    )
    client = get_client(ctx)
    operations = build_add_keywords_operations(
        client.client, params.customer_id, params.ad_group_id,
        params.keywords, params.match_type.value,
        cpc_bid_micros=params.cpc_bid_micros,
    )
    client.mutate(params.customer_id, operations, partial_failure=True)
    count = len(params.keywords)
    return (
        f"Added {count} keyword(s) to ad group {params.ad_group_id} "
        f"({params.match_type.value} match): {', '.join(params.keywords)}"
    )


@mcp.tool()
def gads_update_keyword(
    customer_id: str,
    ad_group_id: str,
    criterion_id: str,
    cpc_bid_micros: int | None = None,
    status: str | None = None,
    ctx: Context = None,
) -> str:
    """Update a keyword's bid or status.

    WARNING: status='remove' permanently removes the keyword.

    Args:
        customer_id: Google Ads customer ID.
        ad_group_id: Ad group ID.
        criterion_id: Keyword criterion ID.
        cpc_bid_micros: New CPC bid in micros (optional).
        status: New status — enable, pause, or remove (optional).
    """
    params = UpdateKeywordInput(
        customer_id=customer_id, ad_group_id=ad_group_id,
        criterion_id=criterion_id, cpc_bid_micros=cpc_bid_micros, status=status,
    )
    client = get_client(ctx)
    operation = build_update_keyword_operation(
        client.client, params.customer_id, params.ad_group_id,
        params.criterion_id, cpc_bid_micros=params.cpc_bid_micros,
        status=params.status.value if params.status else None,
    )
    client.mutate(params.customer_id, [operation])
    changes = []
    if params.cpc_bid_micros is not None:
        changes.append(f"bid={params.cpc_bid_micros}")
    if params.status is not None:
        changes.append(f"status={params.status.value}")
    return f"Keyword {params.criterion_id} updated: {', '.join(changes)}."
