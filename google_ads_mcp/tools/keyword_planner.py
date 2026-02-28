"""Keyword Planner tools for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int, safe_str
from google_ads_mcp.utils.formatting import (
    format_table_markdown,
    micros_to_currency,
)
from google_ads_mcp.utils.pagination import paginate_results


@mcp.tool()
def gads_generate_keyword_ideas(
    customer_id: str,
    keywords: str,
    language_id: str = "1000",
    geo_target_id: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """Generate keyword suggestions using Google Ads Keyword Planner.

    Uses the KeywordPlanIdeaService to generate keyword ideas based on
    seed keywords.

    Args:
        customer_id: Google Ads customer ID.
        keywords: Comma-separated seed keywords (e.g. 'running shoes, sneakers').
        language_id: Language constant ID (default '1000' for English).
        geo_target_id: Geo target constant ID (optional, e.g. '2840' for US).
        limit: Max results to return (default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    service = client.get_service("KeywordPlanIdeaService")

    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    if not keyword_list:
        return json.dumps(
            {"error": "No valid keywords provided."},
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    request = client.client.get_type("GenerateKeywordIdeaRequest")
    request.customer_id = cid
    request.language = f"languageConstants/{language_id}"
    request.keyword_seed.keywords.extend(keyword_list)

    if geo_target_id:
        request.geo_target_constants.append(
            f"geoTargetConstants/{geo_target_id}"
        )

    response = service.generate_keyword_ideas(request=request)

    ideas: list[dict[str, Any]] = []
    for idea in response:
        metrics = idea.keyword_idea_metrics
        ideas.append({
            "keyword": safe_str(idea.text),
            "avg_monthly_searches": safe_int(metrics.avg_monthly_searches),
            "competition": safe_str(metrics.competition).replace(
                "KeywordPlanCompetitionLevel.", ""
            ),
            "low_cpc": micros_to_currency(
                safe_int(metrics.low_top_of_page_bid_micros)
            ),
            "high_cpc": micros_to_currency(
                safe_int(metrics.high_top_of_page_bid_micros)
            ),
        })

    page, pagination = paginate_results(ideas, limit, offset)

    if response_format == "json":
        return json.dumps(
            {
                "keyword_ideas": page,
                "seed_keywords": keyword_list,
                "pagination": pagination.to_dict(),
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    columns = [
        "keyword", "avg_monthly_searches", "competition",
        "low_cpc", "high_cpc",
    ]
    headers = {
        "keyword": "Keyword",
        "avg_monthly_searches": "Avg Searches/mo",
        "competition": "Competition",
        "low_cpc": "Low CPC",
        "high_cpc": "High CPC",
    }
    table = format_table_markdown(page, columns, headers)
    seeds = ", ".join(keyword_list)
    return (
        f"## Keyword Ideas for: {seeds}\n\n"
        f"{table}\n\n"
        f"_Showing {pagination.count} of {pagination.total} keyword ideas"
        f"{' (more available)' if pagination.has_more else ''}_"
    )
