"""Campaign mutation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import (
    build_campaign_status_operation,
    build_campaign_update_operation,
)
from google_ads_mcp.models.mutation_inputs import (
    SetCampaignStatusInput,
    UpdateCampaignInput,
)
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_set_campaign_status(
    customer_id: str,
    campaign_id: str,
    status: str,
    ctx: Context = None,
) -> str:
    """Change a campaign's status (enable, pause, or remove).

    WARNING: status='remove' permanently removes the campaign.

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID to update.
        status: New status — enable, pause, or remove.
    """
    params = SetCampaignStatusInput(
        customer_id=customer_id,
        campaign_id=campaign_id,
        status=status,
    )
    client = get_client(ctx)
    operation = build_campaign_status_operation(
        client.client,
        params.customer_id,
        params.campaign_id,
        params.status.value,
    )
    client.mutate(params.customer_id, [operation])
    action_map = {"enable": "ENABLED", "pause": "PAUSED", "remove": "REMOVED"}
    new_status = action_map[params.status.value]
    return f"Campaign {params.campaign_id} status changed to {new_status}."


@mcp.tool()
def gads_update_campaign(
    customer_id: str,
    campaign_id: str,
    name: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    ctx: Context = None,
) -> str:
    """Update campaign settings (name, start/end dates).

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID to update.
        name: New campaign name (optional).
        start_date: New start date YYYY-MM-DD (optional).
        end_date: New end date YYYY-MM-DD (optional).
    """
    params = UpdateCampaignInput(
        customer_id=customer_id,
        campaign_id=campaign_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
    )
    client = get_client(ctx)
    operation = build_campaign_update_operation(
        client.client,
        params.customer_id,
        params.campaign_id,
        name=params.name,
        start_date=params.start_date,
        end_date=params.end_date,
    )
    client.mutate(params.customer_id, [operation])
    updated = [
        f for f in ["name", "start_date", "end_date"]
        if getattr(params, f) is not None
    ]
    return f"Campaign {params.campaign_id} updated: {', '.join(updated)}."
