"""Conversion upload mutation tools for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_upload_click_conversions(
    customer_id: str,
    conversion_action_id: str,
    gclid: str,
    conversion_date_time: str,
    conversion_value: float = 0.0,
    currency_code: str = "USD",
    ctx: Context = None,
) -> str:
    """Upload an offline click conversion to Google Ads.

    Associates a conversion event with a previous ad click identified
    by the Google Click ID (GCLID).

    Args:
        customer_id: Google Ads customer ID.
        conversion_action_id: The conversion action resource ID.
        gclid: The Google Click ID from the original ad click.
        conversion_date_time: Conversion datetime (YYYY-MM-DD HH:MM:SS+TZ, e.g. '2026-01-15 12:00:00+00:00').
        conversion_value: Optional monetary value of the conversion.
        currency_code: Currency code (default USD).
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    service = client.get_service("ConversionUploadService")

    click_conversion = client.client.get_type("ClickConversion")
    click_conversion.conversion_action = (
        f"customers/{cid}/conversionActions/{conversion_action_id}"
    )
    click_conversion.gclid = gclid
    click_conversion.conversion_date_time = conversion_date_time
    click_conversion.conversion_value = conversion_value
    click_conversion.currency_code = currency_code

    request = client.client.get_type("UploadClickConversionsRequest")
    request.customer_id = cid
    request.conversions.append(click_conversion)
    request.partial_failure = True

    response = service.upload_click_conversions(request=request)

    results: list[dict[str, Any]] = []
    for result in response.results:
        results.append({
            "gclid": str(result.gclid) if hasattr(result, "gclid") else "",
            "conversion_action": (
                str(result.conversion_action)
                if hasattr(result, "conversion_action")
                else ""
            ),
            "conversion_date_time": (
                str(result.conversion_date_time)
                if hasattr(result, "conversion_date_time")
                else ""
            ),
        })

    return json.dumps(
        {"uploaded": len(results), "results": results},
        indent=2,
        ensure_ascii=False,
        default=str,
    )
