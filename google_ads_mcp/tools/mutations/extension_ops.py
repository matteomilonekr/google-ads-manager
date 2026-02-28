"""Ad extension mutation tools."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from google_ads_mcp.builders.operations import build_create_extension_operation
from google_ads_mcp.models.creation_inputs import CreateAdExtensionInput
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


@mcp.tool()
def gads_create_ad_extension(
    customer_id: str,
    campaign_id: str,
    extension_type: str,
    link_text: str | None = None,
    final_urls: list[str] | None = None,
    description1: str | None = None,
    description2: str | None = None,
    callout_text: str | None = None,
    phone_number: str | None = None,
    country_code: str | None = None,
    snippet_header: str | None = None,
    snippet_values: list[str] | None = None,
    ctx: Context = None,
) -> str:
    """Create an ad extension (sitelink, callout, call, or structured snippet).

    Args:
        customer_id: Google Ads customer ID.
        campaign_id: Campaign ID.
        extension_type: Type — SITELINK, CALLOUT, CALL, or STRUCTURED_SNIPPET.
        link_text: Sitelink text (required for SITELINK).
        final_urls: Sitelink URLs (required for SITELINK).
        description1: Sitelink description line 1 (optional).
        description2: Sitelink description line 2 (optional).
        callout_text: Callout text (required for CALLOUT).
        phone_number: Phone number (required for CALL).
        country_code: Country code (required for CALL, e.g. IT, US).
        snippet_header: Snippet header (required for STRUCTURED_SNIPPET).
        snippet_values: Snippet values (required for STRUCTURED_SNIPPET).
    """
    params = CreateAdExtensionInput(
        customer_id=customer_id, campaign_id=campaign_id,
        extension_type=extension_type, link_text=link_text,
        final_urls=final_urls, description1=description1, description2=description2,
        callout_text=callout_text, phone_number=phone_number, country_code=country_code,
        snippet_header=snippet_header, snippet_values=snippet_values,
    )
    client = get_client(ctx)
    operation = build_create_extension_operation(
        client.client, params.customer_id, params.campaign_id,
        extension_type=params.extension_type.value,
        link_text=params.link_text, final_urls=params.final_urls,
        description1=params.description1, description2=params.description2,
        callout_text=params.callout_text, phone_number=params.phone_number,
        country_code=params.country_code,
        snippet_header=params.snippet_header, snippet_values=params.snippet_values,
    )
    client.mutate(params.customer_id, [operation])
    return f"{params.extension_type.value} extension created for campaign {params.campaign_id}."
