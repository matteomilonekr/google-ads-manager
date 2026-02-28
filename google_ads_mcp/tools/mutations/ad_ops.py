"""Ad mutation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import build_ad_status_operation
from google_ads_mcp.models.mutation_inputs import SetAdStatusInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_set_ad_status(
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    status: str,
    ctx: Context = None,
) -> str:
    """Change an ad's status (enable, pause, or remove).

    WARNING: status='remove' permanently removes the ad.

    Args:
        customer_id: Google Ads customer ID.
        ad_group_id: Ad group ID containing the ad.
        ad_id: Ad ID to update.
        status: New status — enable, pause, or remove.
    """
    params = SetAdStatusInput(
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        ad_id=ad_id,
        status=status,
    )
    client = get_client(ctx)
    operation = build_ad_status_operation(
        client.client,
        params.customer_id,
        params.ad_group_id,
        params.ad_id,
        params.status.value,
    )
    client.mutate(params.customer_id, [operation])
    action_map = {"enable": "ENABLED", "pause": "PAUSED", "remove": "REMOVED"}
    return f"Ad {params.ad_id} status changed to {action_map[params.status.value]}."
