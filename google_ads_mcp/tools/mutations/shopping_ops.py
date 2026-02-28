"""Shopping and PMax listing group tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import (
    build_listing_group_filter_operation,
    build_merchant_center_link_operation,
)
from google_ads_mcp.models.asset_inputs import (
    SetListingGroupFilterInput,
    LinkMerchantCenterInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_set_listing_group_filter(
    customer_id: str,
    asset_group_id: str,
    filter_type: str,
    dimension: str,
    value: str | None = None,
    parent_filter_id: str | None = None,
    ctx: Context = None,
) -> str:
    """Set a listing group filter for a PMax or Shopping asset group.

    Used to define which products from Merchant Center to include/exclude.

    Args:
        customer_id: Google Ads customer ID.
        asset_group_id: Asset group ID.
        filter_type: Type — UNIT_INCLUDED, UNIT_EXCLUDED, or SUBDIVISION.
        dimension: Dimension — BRAND, CATEGORY_L1, PRODUCT_TYPE_L1, CUSTOM_LABEL_0, ITEM_ID, CONDITION, etc.
        value: Filter value (e.g. brand name). Not required for SUBDIVISION root.
        parent_filter_id: Parent filter ID for sub-filters.
    """
    params = SetListingGroupFilterInput(
        customer_id=customer_id,
        asset_group_id=asset_group_id,
        filter_type=filter_type,
        dimension=dimension,
        value=value,
        parent_filter_id=parent_filter_id,
    )
    client = get_client(ctx)
    operation = build_listing_group_filter_operation(
        client.client,
        params.customer_id,
        asset_group_id=params.asset_group_id,
        filter_type=params.filter_type,
        dimension=params.dimension.value,
        value=params.value,
        parent_filter_id=params.parent_filter_id,
    )
    response = client.mutate(params.customer_id, [operation])
    filter_rn = response.mutate_operation_responses[0].asset_group_listing_group_filter_result.resource_name
    filter_id = filter_rn.split("/")[-1]
    return f"{params.filter_type} filter on {params.dimension.value} set for asset group {params.asset_group_id}. Filter ID: {filter_id}."


@mcp.tool()
def gads_link_merchant_center(
    customer_id: str,
    campaign_id: str,
    merchant_id: str,
    feed_label: str | None = None,
    sales_country: str | None = None,
    ctx: Context = None,
) -> str:
    """Link a Merchant Center account to a Shopping or PMax campaign.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        merchant_id: Merchant Center account ID.
        feed_label: Feed label (optional).
        sales_country: Sales country code e.g. US, IT (optional).
    """
    params = LinkMerchantCenterInput(
        customer_id=customer_id,
        campaign_id=campaign_id,
        merchant_id=merchant_id,
        feed_label=feed_label,
        sales_country=sales_country,
    )
    client = get_client(ctx)
    operation = build_merchant_center_link_operation(
        client.client,
        params.customer_id,
        campaign_id=params.campaign_id,
        merchant_id=params.merchant_id,
        feed_label=params.feed_label,
        sales_country=params.sales_country,
    )
    client.mutate(params.customer_id, [operation])
    return f"Merchant Center {params.merchant_id} linked to campaign {params.campaign_id}."
