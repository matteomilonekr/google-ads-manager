"""Location, language, device, demographic, and audience targeting mutation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import (
    build_location_criterion_operations,
    build_language_criterion_operations,
    build_device_targeting_operation,
    build_demographic_targeting_operations,
    build_audience_segment_operation,
)
from google_ads_mcp.models.mutation_inputs import (
    SetLocationTargetingInput,
    SetLanguageTargetingInput,
)
from google_ads_mcp.models.creation_inputs import (
    SetDeviceTargetingInput,
    SetDemographicTargetingInput,
    CreateAudienceSegmentInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_set_location_targeting(
    customer_id: str,
    campaign_id: str,
    location_ids: list[int] = [],
    exclude: bool = False,
    ctx: Context = None,
) -> str:
    """Set location targeting for a campaign.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        location_ids: Geo target constant IDs (e.g. 2380=Italy, 2826=UK, 2840=US).
        exclude: If true, exclude these locations instead of targeting them.
    """
    params = SetLocationTargetingInput(
        customer_id=customer_id,
        campaign_id=campaign_id,
        location_ids=location_ids,
        exclude=exclude,
    )
    client = get_client(ctx)
    operations = build_location_criterion_operations(
        client.client,
        params.customer_id,
        params.campaign_id,
        params.location_ids,
        params.exclude,
    )
    client.mutate(params.customer_id, operations, partial_failure=True)
    action = "excluded from" if params.exclude else "targeted in"
    count = len(params.location_ids)
    return f"{count} location(s) {action} campaign {params.campaign_id}."


@mcp.tool()
def gads_set_language_targeting(
    customer_id: str,
    campaign_id: str,
    language_ids: list[int] = [],
    ctx: Context = None,
) -> str:
    """Set language targeting for a campaign.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        language_ids: Language criterion IDs (e.g. 1000=English, 1004=Italian, 1001=French).
    """
    params = SetLanguageTargetingInput(
        customer_id=customer_id,
        campaign_id=campaign_id,
        language_ids=language_ids,
    )
    client = get_client(ctx)
    operations = build_language_criterion_operations(
        client.client,
        params.customer_id,
        params.campaign_id,
        params.language_ids,
    )
    client.mutate(params.customer_id, operations, partial_failure=True)
    count = len(params.language_ids)
    return f"{count} language(s) set for campaign {params.campaign_id}."


@mcp.tool()
def gads_set_device_targeting(
    customer_id: str,
    campaign_id: str,
    device: str,
    bid_modifier: float,
    ctx: Context = None,
) -> str:
    """Set device bid adjustment for a campaign.

    WARNING: bid_modifier=0.0 effectively excludes the device.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        device: Device — MOBILE, DESKTOP, or TABLET.
        bid_modifier: Bid modifier (0.0=exclude, 1.0=no change, 1.5=+50%).
    """
    params = SetDeviceTargetingInput(
        customer_id=customer_id, campaign_id=campaign_id,
        device=device, bid_modifier=bid_modifier,
    )
    client = get_client(ctx)
    operation = build_device_targeting_operation(
        client.client, params.customer_id, params.campaign_id,
        device=params.device.value, bid_modifier=params.bid_modifier,
    )
    client.mutate(params.customer_id, [operation])
    pct = int((params.bid_modifier - 1.0) * 100)
    modifier_str = f"+{pct}%" if pct > 0 else f"{pct}%" if pct < 0 else "no change"
    if params.bid_modifier == 0.0:
        modifier_str = "excluded"
    return f"{params.device.value} targeting set for campaign {params.campaign_id}: {modifier_str}."


@mcp.tool()
def gads_set_demographic_targeting(
    customer_id: str,
    campaign_id: str,
    dimension: str,
    values: list[str] = [],
    bid_modifier: float | None = None,
    ctx: Context = None,
) -> str:
    """Set demographic targeting for a campaign.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        dimension: Dimension — AGE, GENDER, PARENTAL_STATUS, or INCOME.
        values: Demographic values to target.
        bid_modifier: Bid modifier (optional).
    """
    params = SetDemographicTargetingInput(
        customer_id=customer_id, campaign_id=campaign_id,
        dimension=dimension, values=values, bid_modifier=bid_modifier,
    )
    client = get_client(ctx)
    operations = build_demographic_targeting_operations(
        client.client, params.customer_id, params.campaign_id,
        dimension=params.dimension.value, values=params.values,
        bid_modifier=params.bid_modifier,
    )
    client.mutate(params.customer_id, operations, partial_failure=True)
    count = len(params.values)
    return f"{count} {params.dimension.value} target(s) set for campaign {params.campaign_id}."


@mcp.tool()
def gads_create_audience_segment(
    customer_id: str,
    campaign_id: str,
    audience_type: str,
    audience_id: str,
    bid_modifier: float | None = None,
    ctx: Context = None,
) -> str:
    """Add an audience segment to a campaign.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        audience_type: Type — IN_MARKET, AFFINITY, CUSTOM_INTENT, or REMARKETING.
        audience_id: Audience segment ID.
        bid_modifier: Bid modifier (optional).
    """
    params = CreateAudienceSegmentInput(
        customer_id=customer_id, campaign_id=campaign_id,
        audience_type=audience_type, audience_id=audience_id,
        bid_modifier=bid_modifier,
    )
    client = get_client(ctx)
    operation = build_audience_segment_operation(
        client.client, params.customer_id, params.campaign_id,
        audience_type=params.audience_type.value,
        audience_id=params.audience_id, bid_modifier=params.bid_modifier,
    )
    client.mutate(params.customer_id, [operation])
    return f"{params.audience_type.value} audience {params.audience_id} added to campaign {params.campaign_id}."
