"""Budget mutation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import build_budget_update_operation
from google_ads_mcp.models.mutation_inputs import UpdateBudgetInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client
from google_ads_mcp.utils.formatting import micros_to_currency


@mcp.tool()
def gads_update_budget(
    customer_id: str,
    budget_id: str,
    amount_micros: int,
    ctx: Context = None,
) -> str:
    """Update a campaign's daily budget.

    Args:
        customer_id: Google Ads customer ID.
        budget_id: Campaign budget ID.
        amount_micros: New daily budget in micros (1 unit = 1,000,000 micros).
    """
    params = UpdateBudgetInput(
        customer_id=customer_id,
        budget_id=budget_id,
        amount_micros=amount_micros,
    )
    client = get_client(ctx)
    operation = build_budget_update_operation(
        client.client,
        params.customer_id,
        params.budget_id,
        params.amount_micros,
    )
    client.mutate(params.customer_id, [operation])
    formatted = micros_to_currency(params.amount_micros)
    return f"Budget {params.budget_id} updated to {formatted}/day."
