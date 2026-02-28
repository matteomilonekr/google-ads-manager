"""Campaign, ad group, and ad creation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import (
    build_create_campaign_operations,
    build_create_ad_group_operation,
    build_create_rsa_operation,
    build_responsive_display_ad_operation,
    build_demand_gen_ad_operation,
)
from google_ads_mcp.models.creation_inputs import (
    CreateCampaignInput,
    CreateAdGroupInput,
    CreateResponsiveSearchAdInput,
)
from google_ads_mcp.models.asset_inputs import (
    CreateResponsiveDisplayAdInput,
    CreateDemandGenAdInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client
from google_ads_mcp.utils.formatting import micros_to_currency


@mcp.tool()
def gads_create_campaign(
    customer_id: str,
    name: str,
    campaign_type: str,
    bidding_strategy_type: str,
    budget_amount_micros: int,
    start_date: str | None = None,
    end_date: str | None = None,
    target_cpa_micros: int | None = None,
    target_roas: float | None = None,
    ctx: Context = None,
) -> str:
    """Create a new campaign with budget and bidding strategy.

    The campaign is created in PAUSED status for safety. Enable it with gads_set_campaign_status.

    Args:
        customer_id: Google Ads customer ID.
        name: Campaign name.
        campaign_type: Type — SEARCH, DISPLAY, SHOPPING, VIDEO, PERFORMANCE_MAX, or DEMAND_GEN.
        bidding_strategy_type: Bidding — MANUAL_CPC, TARGET_CPA, TARGET_ROAS, MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE, or MAXIMIZE_CLICKS.
        budget_amount_micros: Daily budget in micros (1 unit = 1,000,000 micros).
        start_date: Start date YYYY-MM-DD (optional).
        end_date: End date YYYY-MM-DD (optional).
        target_cpa_micros: Target CPA in micros (required for TARGET_CPA).
        target_roas: Target ROAS (required for TARGET_ROAS, e.g. 3.0 = 300%).
    """
    params = CreateCampaignInput(
        customer_id=customer_id,
        name=name,
        campaign_type=campaign_type,
        bidding_strategy_type=bidding_strategy_type,
        budget_amount_micros=budget_amount_micros,
        start_date=start_date,
        end_date=end_date,
        target_cpa_micros=target_cpa_micros,
        target_roas=target_roas,
    )
    client = get_client(ctx)
    operations = build_create_campaign_operations(
        client.client,
        params.customer_id,
        name=params.name,
        campaign_type=params.campaign_type.value,
        bidding_strategy_type=params.bidding_strategy_type.value,
        budget_amount_micros=params.budget_amount_micros,
        start_date=params.start_date,
        end_date=params.end_date,
        target_cpa_micros=params.target_cpa_micros,
        target_roas=params.target_roas,
    )
    response = client.mutate(params.customer_id, operations)
    budget_rn = response.mutate_operation_responses[0].campaign_budget_result.resource_name
    campaign_rn = response.mutate_operation_responses[1].campaign_result.resource_name
    budget_id = budget_rn.split("/")[-1]
    campaign_id = campaign_rn.split("/")[-1]
    formatted_budget = micros_to_currency(params.budget_amount_micros)
    return (
        f"Campaign '{params.name}' created (PAUSED). "
        f"Type: {params.campaign_type.value}, Bidding: {params.bidding_strategy_type.value}, "
        f"Budget: {formatted_budget}/day. "
        f"Campaign ID: {campaign_id}, Budget ID: {budget_id}."
    )


@mcp.tool()
def gads_create_ad_group(
    customer_id: str,
    campaign_id: str,
    name: str,
    ad_group_type: str,
    cpc_bid_micros: int | None = None,
    ctx: Context = None,
) -> str:
    """Create a new ad group in a campaign.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID to add the ad group to.
        name: Ad group name.
        ad_group_type: Type — SEARCH_STANDARD, DISPLAY_STANDARD, SHOPPING_PRODUCT, or VIDEO_RESPONSIVE.
        cpc_bid_micros: Default CPC bid in micros (optional).
    """
    params = CreateAdGroupInput(
        customer_id=customer_id,
        campaign_id=campaign_id,
        name=name,
        ad_group_type=ad_group_type,
        cpc_bid_micros=cpc_bid_micros,
    )
    client = get_client(ctx)
    operation = build_create_ad_group_operation(
        client.client,
        params.customer_id,
        params.campaign_id,
        name=params.name,
        ad_group_type=params.ad_group_type.value,
        cpc_bid_micros=params.cpc_bid_micros,
    )
    response = client.mutate(params.customer_id, [operation])
    ad_group_rn = response.mutate_operation_responses[0].ad_group_result.resource_name
    ad_group_id = ad_group_rn.split("/")[-1]
    return f"Ad group '{params.name}' created. Type: {params.ad_group_type.value}. ID: {ad_group_id}."


@mcp.tool()
def gads_create_responsive_search_ad(
    customer_id: str,
    ad_group_id: str,
    headlines: list[str] = [],
    descriptions: list[str] = [],
    final_urls: list[str] = [],
    path1: str | None = None,
    path2: str | None = None,
    ctx: Context = None,
) -> str:
    """Create a Responsive Search Ad (RSA) in an ad group.

    Args:
        customer_id: Google Ads customer ID.
        ad_group_id: Ad group ID.
        headlines: 3-15 headlines (max 30 chars each).
        descriptions: 2-4 descriptions (max 90 chars each).
        final_urls: Landing page URLs.
        path1: Display URL path 1 (optional, max 15 chars).
        path2: Display URL path 2 (optional, max 15 chars).
    """
    params = CreateResponsiveSearchAdInput(
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        headlines=headlines,
        descriptions=descriptions,
        final_urls=final_urls,
        path1=path1,
        path2=path2,
    )
    client = get_client(ctx)
    operation = build_create_rsa_operation(
        client.client,
        params.customer_id,
        params.ad_group_id,
        headlines=params.headlines,
        descriptions=params.descriptions,
        final_urls=params.final_urls,
        path1=params.path1,
        path2=params.path2,
    )
    response = client.mutate(params.customer_id, [operation])
    ad_rn = response.mutate_operation_responses[0].ad_group_ad_result.resource_name
    ad_id = ad_rn.split("/")[-1]
    return (
        f"RSA created with {len(params.headlines)} headlines, "
        f"{len(params.descriptions)} descriptions. Ad ID: {ad_id}."
    )


@mcp.tool()
def gads_create_responsive_display_ad(
    customer_id: str,
    ad_group_id: str,
    marketing_image_asset_ids: list[str] = [],
    headlines: list[str] = [],
    long_headline: str = "",
    descriptions: list[str] = [],
    business_name: str = "",
    final_urls: list[str] = [],
    logo_asset_ids: list[str] | None = None,
    square_image_asset_ids: list[str] | None = None,
    ctx: Context = None,
) -> str:
    """Create a Responsive Display Ad in an ad group.

    Requires pre-created image assets (use gads_create_asset first).

    Args:
        customer_id: Google Ads customer ID.
        ad_group_id: Ad group ID (must be DISPLAY_STANDARD type).
        marketing_image_asset_ids: Marketing image asset IDs (min 1).
        headlines: Headlines (min 1, max 5).
        long_headline: Long headline.
        descriptions: Descriptions (min 1, max 5).
        business_name: Business name.
        final_urls: Landing page URLs.
        logo_asset_ids: Logo asset IDs (optional).
        square_image_asset_ids: Square image asset IDs (optional).
    """
    params = CreateResponsiveDisplayAdInput(
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        marketing_image_asset_ids=marketing_image_asset_ids,
        headlines=headlines,
        long_headline=long_headline,
        descriptions=descriptions,
        business_name=business_name,
        final_urls=final_urls,
        logo_asset_ids=logo_asset_ids,
        square_image_asset_ids=square_image_asset_ids,
    )
    client = get_client(ctx)
    operation = build_responsive_display_ad_operation(
        client.client,
        params.customer_id,
        ad_group_id=params.ad_group_id,
        marketing_image_asset_ids=params.marketing_image_asset_ids,
        headlines=params.headlines,
        long_headline=params.long_headline,
        descriptions=params.descriptions,
        business_name=params.business_name,
        final_urls=params.final_urls,
        logo_asset_ids=params.logo_asset_ids,
        square_image_asset_ids=params.square_image_asset_ids,
    )
    response = client.mutate(params.customer_id, [operation])
    ad_rn = response.mutate_operation_responses[0].ad_group_ad_result.resource_name
    ad_id = ad_rn.split("/")[-1]
    return (
        f"Responsive Display Ad created with {len(params.headlines)} headlines, "
        f"{len(params.marketing_image_asset_ids)} images. Ad ID: {ad_id}."
    )


@mcp.tool()
def gads_create_demand_gen_ad(
    customer_id: str,
    ad_group_id: str,
    headlines: list[str] = [],
    descriptions: list[str] = [],
    marketing_image_asset_ids: list[str] = [],
    logo_asset_id: str = "",
    business_name: str = "",
    final_urls: list[str] = [],
    call_to_action: str | None = None,
    ctx: Context = None,
) -> str:
    """Create a Demand Gen multi-asset ad.

    Requires pre-created image assets (use gads_create_asset first).

    Args:
        customer_id: Google Ads customer ID.
        ad_group_id: Ad group ID.
        headlines: Headlines (min 1, max 5).
        descriptions: Descriptions (min 1, max 5).
        marketing_image_asset_ids: Marketing image asset IDs (min 1).
        logo_asset_id: Logo asset ID.
        business_name: Business name.
        final_urls: Landing page URLs.
        call_to_action: CTA type (optional, e.g. SHOP_NOW, LEARN_MORE).
    """
    params = CreateDemandGenAdInput(
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        headlines=headlines,
        descriptions=descriptions,
        marketing_image_asset_ids=marketing_image_asset_ids,
        logo_asset_id=logo_asset_id,
        business_name=business_name,
        final_urls=final_urls,
        call_to_action=call_to_action,
    )
    client = get_client(ctx)
    operation = build_demand_gen_ad_operation(
        client.client,
        params.customer_id,
        ad_group_id=params.ad_group_id,
        headlines=params.headlines,
        descriptions=params.descriptions,
        marketing_image_asset_ids=params.marketing_image_asset_ids,
        logo_asset_id=params.logo_asset_id,
        business_name=params.business_name,
        final_urls=params.final_urls,
        call_to_action=params.call_to_action,
    )
    response = client.mutate(params.customer_id, [operation])
    ad_rn = response.mutate_operation_responses[0].ad_group_ad_result.resource_name
    ad_id = ad_rn.split("/")[-1]
    return (
        f"Demand Gen ad created with {len(params.headlines)} headlines, "
        f"{len(params.marketing_image_asset_ids)} images. Ad ID: {ad_id}."
    )
