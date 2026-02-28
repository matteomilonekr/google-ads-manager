"""Asset management tools — create assets, asset groups, and link them."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import (
    build_create_asset_operation,
    build_create_asset_group_operation,
    build_asset_group_asset_operations,
)
from google_ads_mcp.models.asset_inputs import (
    CreateAssetInput,
    CreateAssetGroupInput,
    AddAssetGroupAssetsInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_create_asset(
    customer_id: str,
    asset_type: str,
    name: str,
    text_content: str | None = None,
    image_url: str | None = None,
    youtube_video_id: str | None = None,
    call_to_action_type: str | None = None,
    ctx: Context = None,
) -> str:
    """Create a reusable asset (text, image, video, or CTA).

    For IMAGE: provide a public HTTPS URL — the image is fetched server-side.
    For YOUTUBE_VIDEO: provide the 11-character YouTube video ID.

    Args:
        customer_id: Google Ads customer ID.
        asset_type: Type — TEXT, IMAGE, YOUTUBE_VIDEO, or CALL_TO_ACTION.
        name: Asset name for identification.
        text_content: Text content (required for TEXT).
        image_url: Public HTTPS image URL (required for IMAGE).
        youtube_video_id: YouTube video ID, 11 chars (required for YOUTUBE_VIDEO).
        call_to_action_type: CTA type e.g. LEARN_MORE, SHOP_NOW (required for CALL_TO_ACTION).
    """
    params = CreateAssetInput(
        customer_id=customer_id,
        asset_type=asset_type,
        name=name,
        text_content=text_content,
        image_url=image_url,
        youtube_video_id=youtube_video_id,
        call_to_action_type=call_to_action_type,
    )

    # For IMAGE assets, fetch the image data from URL
    image_data = None
    if params.asset_type.value == "IMAGE" and params.image_url:
        import httpx
        resp = httpx.get(params.image_url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        image_data = resp.content

    client = get_client(ctx)
    operation = build_create_asset_operation(
        client.client,
        params.customer_id,
        asset_type=params.asset_type.value,
        name=params.name,
        text_content=params.text_content,
        image_data=image_data,
        youtube_video_id=params.youtube_video_id,
        call_to_action_type=params.call_to_action_type,
    )
    response = client.mutate(params.customer_id, [operation])
    asset_rn = response.mutate_operation_responses[0].asset_result.resource_name
    asset_id = asset_rn.split("/")[-1]
    return f"{params.asset_type.value} asset '{params.name}' created. Asset ID: {asset_id}."


@mcp.tool()
def gads_create_asset_group(
    customer_id: str,
    campaign_id: str,
    name: str,
    final_urls: list[str] = [],
    final_mobile_urls: list[str] | None = None,
    path1: str | None = None,
    path2: str | None = None,
    ctx: Context = None,
) -> str:
    """Create an asset group for a Performance Max or Demand Gen campaign.

    After creating, use gads_add_asset_group_assets to link assets to it.
    PMax requires minimum: 1 headline, 1 description, 1 marketing image, 1 logo.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        name: Asset group name.
        final_urls: Landing page URLs (min 1).
        final_mobile_urls: Mobile-specific final URLs (optional).
        path1: Display URL path 1 (optional).
        path2: Display URL path 2 (optional).
    """
    params = CreateAssetGroupInput(
        customer_id=customer_id,
        campaign_id=campaign_id,
        name=name,
        final_urls=final_urls,
        final_mobile_urls=final_mobile_urls,
        path1=path1,
        path2=path2,
    )
    client = get_client(ctx)
    operation = build_create_asset_group_operation(
        client.client,
        params.customer_id,
        params.campaign_id,
        name=params.name,
        final_urls=params.final_urls,
        final_mobile_urls=params.final_mobile_urls,
        path1=params.path1,
        path2=params.path2,
    )
    response = client.mutate(params.customer_id, [operation])
    ag_rn = response.mutate_operation_responses[0].asset_group_result.resource_name
    ag_id = ag_rn.split("/")[-1]
    return f"Asset group '{params.name}' created. ID: {ag_id}."


@mcp.tool()
def gads_add_asset_group_assets(
    customer_id: str,
    asset_group_id: str,
    asset_ids: list[str] = [],
    field_types: list[str] = [],
    ctx: Context = None,
) -> str:
    """Link assets to an asset group (for PMax/DG campaigns).

    Provide parallel lists: asset_ids and field_types must have same length.

    Args:
        customer_id: Google Ads customer ID.
        asset_group_id: Asset group ID.
        asset_ids: Asset IDs to link (max 20).
        field_types: Field types for each asset (HEADLINE, DESCRIPTION, MARKETING_IMAGE, LOGO, etc.).
    """
    assets_list = [
        {"asset_id": aid, "field_type": ft}
        for aid, ft in zip(asset_ids, field_types)
    ]
    params = AddAssetGroupAssetsInput(
        customer_id=customer_id,
        asset_group_id=asset_group_id,
        assets=assets_list,
    )
    client = get_client(ctx)
    operations = build_asset_group_asset_operations(
        client.client,
        params.customer_id,
        params.asset_group_id,
        assets=[{"asset_id": a.asset_id, "field_type": a.field_type.value} for a in params.assets],
    )
    client.mutate(params.customer_id, operations, partial_failure=True)
    count = len(params.assets)
    return f"{count} asset(s) linked to asset group {params.asset_group_id}."
