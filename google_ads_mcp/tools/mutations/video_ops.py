"""Video ad creation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import build_video_ad_operation
from google_ads_mcp.models.asset_inputs import CreateVideoAdInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_create_video_ad(
    customer_id: str,
    ad_group_id: str,
    video_asset_id: str,
    ad_format: str,
    headline: str | None = None,
    description: str | None = None,
    final_url: str | None = None,
    display_url: str | None = None,
    companion_banner_asset_id: str | None = None,
    ctx: Context = None,
) -> str:
    """Create a video ad in an ad group.

    Requires a pre-created YouTube video asset (use gads_create_asset first).
    For BUMPER ads (6-second), headline/description/final_url are not required.

    Args:
        customer_id: Google Ads customer ID.
        ad_group_id: Ad group ID (must be VIDEO_RESPONSIVE type).
        video_asset_id: YouTube video asset ID.
        ad_format: Format — IN_STREAM_SKIPPABLE, IN_STREAM_NON_SKIPPABLE, BUMPER, or VIDEO_RESPONSIVE.
        headline: Headline (required for IN_STREAM formats).
        description: Description (optional).
        final_url: Landing page URL (required for IN_STREAM formats).
        display_url: Display URL (optional).
        companion_banner_asset_id: Companion banner asset ID (optional).
    """
    params = CreateVideoAdInput(
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        video_asset_id=video_asset_id,
        ad_format=ad_format,
        headline=headline,
        description=description,
        final_url=final_url,
        display_url=display_url,
        companion_banner_asset_id=companion_banner_asset_id,
    )
    client = get_client(ctx)
    operation = build_video_ad_operation(
        client.client,
        params.customer_id,
        ad_group_id=params.ad_group_id,
        video_asset_id=params.video_asset_id,
        ad_format=params.ad_format.value,
        headline=params.headline,
        description=params.description,
        final_url=params.final_url,
        display_url=params.display_url,
        companion_banner_asset_id=params.companion_banner_asset_id,
    )
    response = client.mutate(params.customer_id, [operation])
    ad_rn = response.mutate_operation_responses[0].ad_group_ad_result.resource_name
    ad_id = ad_rn.split("/")[-1]
    return f"{params.ad_format.value} video ad created. Ad ID: {ad_id}."
