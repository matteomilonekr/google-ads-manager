"""Google Ads MCP tools — importing this module registers all tools with the server."""

from google_ads_mcp.tools import (  # noqa: F401
    account,
    ad_groups,
    ads,
    audiences,
    budgets,
    campaigns,
    gaql,
    hierarchy,
    keyword_planner,
    keywords,
    labels,
    search_terms,
    views,
)
from google_ads_mcp.tools.mutations import (  # noqa: F401
    campaign_ops,
    ad_group_ops,
    ad_ops,
    budget_ops,
    keyword_ops,
    targeting_ops,
    creation_ops,
    bidding_ops,
    extension_ops,
    asset_ops,
    video_ops,
    shopping_ops,
    conversion_ops,
    customer_list_ops,
)
