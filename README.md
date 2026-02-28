# Google Ads MCP Server

An MCP (Model Context Protocol) server that provides full Google Ads campaign management through Claude and other MCP-compatible AI assistants. Built with [FastMCP](https://github.com/jlowin/fastmcp) and the official [Google Ads API](https://developers.google.com/google-ads/api/docs/start).

## Features

**54 tools** covering the complete Google Ads workflow — read performance data, create campaigns, manage keywords, upload conversions, and more.

### Read Tools (28)

| Tool | Description |
|------|-------------|
| `get_account_overview` | Account-level performance summary |
| `list_campaigns` | List campaigns with status/type filters |
| `get_campaign_performance` | Campaign metrics over a date range |
| `list_ad_groups` | List ad groups with campaign/status filters |
| `get_ad_group_performance` | Ad group metrics over a date range |
| `gads_list_ad_group_ads` | List ads with creative details, performance, and policy status |
| `list_keywords` | List keywords with match types and bids |
| `get_keyword_performance` | Keyword metrics over a date range |
| `search_terms_report` | Search terms triggering your ads |
| `gads_list_labels` | Account labels |
| `gads_list_campaign_labels` | Campaign-label associations |
| `gads_list_ad_group_labels` | Ad group-label associations |
| `gads_list_ad_group_ad_labels` | Ad-label associations |
| `gads_list_ad_group_criterion_labels` | Criterion-label associations |
| `gads_list_customer_labels` | Customer-label associations |
| `gads_list_audiences` | Audience segments and performance |
| `gads_list_user_interests` | User interest categories |
| `gads_list_campaign_budgets` | Budget configuration and spend |
| `gads_get_bidding_strategies` | Campaign bidding strategies |
| `gads_get_ad_group_bidding_strategies` | Ad group bidding strategies |
| `gads_list_change_history` | Change history for account entities |
| `gads_list_customer_clients` | Customer client hierarchy |
| `gads_list_accessible_customers` | Accessible customer accounts |
| `gads_geographic_view` | Location-based performance data |
| `gads_shopping_performance_view` | Product-level shopping performance |
| `gads_display_keyword_view` | Display keyword targeting performance |
| `gads_topic_view` | Topic targeting performance |
| `gads_user_location_view` | User physical location performance |
| `gads_click_view` | Click-level data with GCLID and device info |
| `gads_generate_keyword_ideas` | Keyword ideas from seeds or URL |
| `gads_execute_gaql` | Execute custom GAQL queries |

### Write Tools (26)

| Tool | Description |
|------|-------------|
| `gads_create_campaign` | Create campaigns with budget and bidding |
| `gads_update_campaign` | Update campaign settings |
| `gads_set_campaign_status` | Enable, pause, or remove campaigns |
| `gads_create_ad_group` | Create ad groups within campaigns |
| `gads_set_ad_group_status` | Enable, pause, or remove ad groups |
| `gads_set_ad_status` | Enable, pause, or remove ads |
| `gads_add_keywords` | Add keywords with match types and bids |
| `gads_update_keyword` | Update keyword bids or status |
| `gads_add_negative_keywords` | Add negative keywords (campaign or ad group level) |
| `gads_create_responsive_search_ad` | Create RSAs with multiple headlines/descriptions |
| `gads_create_responsive_display_ad` | Create responsive display ads |
| `gads_create_demand_gen_ad` | Create Demand Gen campaign ads |
| `gads_create_video_ad` | Create video ads (YouTube) |
| `gads_update_budget` | Update campaign budget amounts |
| `gads_set_bidding_strategy` | Set or change bidding strategies |
| `gads_create_ad_extension` | Create sitelinks, callouts, call extensions |
| `gads_set_location_targeting` | Add geographic location targeting |
| `gads_set_language_targeting` | Set language targeting |
| `gads_set_device_targeting` | Set device bid modifiers |
| `gads_set_demographic_targeting` | Target by age, gender, income |
| `gads_create_audience_segment` | Create custom audience segments |
| `gads_create_asset` | Create reusable assets (images, text, video) |
| `gads_create_asset_group` | Create asset groups for Performance Max |
| `gads_add_asset_group_assets` | Link assets to asset groups |
| `gads_set_listing_group_filter` | Set product listing group filters (Shopping) |
| `gads_link_merchant_center` | Link Merchant Center account |
| `gads_upload_click_conversions` | Upload offline click conversions |
| `gads_upload_customer_list` | Upload customer match lists |
| `gads_remove_customer_list_members` | Remove members from customer lists |

## Prerequisites

- Python 3.12+
- A Google Ads developer account with API access
- OAuth2 credentials (client ID, client secret, refresh token)
- A Google Ads developer token

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd google-ads-manager

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Configuration

Set the following environment variables (or add them to a `.env` file):

```bash
# Required
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

# Optional — required for MCC (manager) accounts
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_account_id
```

## Usage

### Run the server

```bash
uv run python -m google_ads_mcp.server
```

### Claude Desktop / Claude Code configuration

Add to your MCP settings:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/google-ads-manager", "python", "-m", "google_ads_mcp.server"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "your_developer_token",
        "GOOGLE_ADS_CLIENT_ID": "your_client_id",
        "GOOGLE_ADS_CLIENT_SECRET": "your_client_secret",
        "GOOGLE_ADS_REFRESH_TOKEN": "your_refresh_token",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "your_manager_account_id"
      }
    }
  }
}
```

## Project Structure

```
google_ads_mcp/
├── server.py              # FastMCP server with lifespan management
├── auth.py                # OAuth2 authentication and client creation
├── client.py              # Google Ads API client wrapper
├── models/
│   ├── common.py          # Shared enums, validators, base models
│   ├── tool_inputs.py     # Input models for read tools
│   ├── mutation_inputs.py # Input models for write tools
│   ├── creation_inputs.py # Input models for creation operations
│   └── asset_inputs.py    # Input models for asset operations
├── tools/
│   ├── _helpers.py        # Shared utilities (status maps, safe casts)
│   ├── account.py         # Account overview
│   ├── ads.py             # Ad group ads (creatives, policy, performance)
│   ├── ad_groups.py       # Ad groups listing and performance
│   ├── audiences.py       # Audiences and user interests
│   ├── budgets.py         # Budgets, bidding strategies, change history
│   ├── campaigns.py       # Campaigns listing and performance
│   ├── gaql.py            # Custom GAQL query execution
│   ├── hierarchy.py       # Account hierarchy and accessible customers
│   ├── keyword_planner.py # Keyword idea generation
│   ├── keywords.py        # Keywords listing and performance
│   ├── labels.py          # All label types (campaign, ad group, etc.)
│   ├── search_terms.py    # Search terms report
│   ├── views.py           # Geographic, shopping, display, topic, click views
│   └── mutations/
│       ├── ad_group_ops.py    # Ad group status operations
│       ├── ad_ops.py          # Ad status operations
│       ├── asset_ops.py       # Asset and asset group management
│       ├── bidding_ops.py     # Bidding strategy operations
│       ├── budget_ops.py      # Budget update operations
│       ├── campaign_ops.py    # Campaign update and status operations
│       ├── conversion_ops.py  # Offline conversion uploads
│       ├── creation_ops.py    # Campaign, ad group, and ad creation
│       ├── customer_list_ops.py # Customer match list operations
│       ├── extension_ops.py   # Ad extension creation
│       ├── keyword_ops.py     # Keyword add/update/negative operations
│       ├── shopping_ops.py    # Shopping and Merchant Center operations
│       ├── targeting_ops.py   # Location, device, demographic targeting
│       └── video_ops.py       # Video ad creation
├── builders/              # GAQL query and mutation operation builders
└── utils/
    ├── errors.py          # Custom exception classes
    ├── formatting.py      # Markdown table formatting, currency conversion
    └── pagination.py      # Result pagination utilities
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run --extra dev pytest tests/ -v

# Run specific test file
uv run --extra dev pytest tests/test_tools_ads.py -v

# Run with coverage
uv run --extra dev pytest tests/ --cov=google_ads_mcp --cov-report=term-missing
```

### Test Suite

648 tests covering all tools, models, builders, and utilities.

## License

Proprietary. All rights reserved. This software is licensed for personal use only. You may not modify, distribute, sublicense, or create derivative works based on this software without prior written authorization.
