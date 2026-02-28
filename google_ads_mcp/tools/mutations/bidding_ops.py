"""Bidding strategy mutation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import build_bidding_strategy_operation
from google_ads_mcp.models.creation_inputs import SetBiddingStrategyInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_set_bidding_strategy(
    customer_id: str,
    campaign_id: str,
    strategy_type: str,
    target_cpa_micros: int | None = None,
    target_roas: float | None = None,
    ctx: Context = None,
) -> str:
    """Set or change a campaign's bidding strategy.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        strategy_type: Strategy — MANUAL_CPC, TARGET_CPA, TARGET_ROAS, MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE, or MAXIMIZE_CLICKS.
        target_cpa_micros: Target CPA in micros (required for TARGET_CPA).
        target_roas: Target ROAS (required for TARGET_ROAS, e.g. 3.0 = 300%).
    """
    params = SetBiddingStrategyInput(
        customer_id=customer_id, campaign_id=campaign_id,
        strategy_type=strategy_type,
        target_cpa_micros=target_cpa_micros, target_roas=target_roas,
    )
    client = get_client(ctx)
    operation = build_bidding_strategy_operation(
        client.client, params.customer_id, params.campaign_id,
        strategy_type=params.strategy_type.value,
        target_cpa_micros=params.target_cpa_micros,
        target_roas=params.target_roas,
    )
    client.mutate(params.customer_id, [operation])
    return f"Campaign {params.campaign_id} bidding strategy set to {params.strategy_type.value}."
