# Google Ads MCP Server — Tool Catalog

> **54 tools** for full Google Ads management via AI assistants.
> Built on MCP (Model Context Protocol) + Google Ads API v18.

---

## Overview

| Category | Count |
|----------|-------|
| Read — Account & Campaigns | 7 |
| Read — Ads, Keywords & Search Terms | 6 |
| Read — Labels | 6 |
| Read — Audiences & Interests | 2 |
| Read — Budgets, Bidding & History | 4 |
| Read — Account Hierarchy | 2 |
| Read — Performance Views | 5 |
| Read — Keyword Planner & GAQL | 2 |
| Write — Campaign Management | 5 |
| Write — Ad Group & Ad Management | 5 |
| Write — Keywords | 3 |
| Write — Ad Creation (Advanced) | 3 |
| Write — Targeting | 5 |
| Write — Assets & Shopping | 5 |
| Write — Conversions & Customer Lists | 3 |
| **Total** | **54** |

---

## Read Tools (28)

### Account & Campaigns

#### `get_account_overview`
Get a high-level overview of the Google Ads account with key metrics.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID (e.g. `1234567890` or `123-456-7890`) |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `response_format` | No | `markdown` or `json` |

---

#### `list_campaigns`
List Google Ads campaigns with optional status and type filters.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `status` | No | Filter: `all`, `enabled`, `paused`, `removed` |
| `campaign_type` | No | Filter: `all`, `search`, `display`, `shopping`, `video`, `performance_max`, `demand_gen`, `app`, `smart`, `hotel`, `local`, `local_services`, `travel` |
| `limit` | No | Max results 1-1000 (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `get_campaign_performance`
Get performance metrics for campaigns over a date range.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Specific campaign ID |
| `status` | No | Filter: `all`, `enabled`, `paused`, `removed` |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results 1-1000 (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

**Metrics returned:** Impressions, Clicks, Cost, Conversions, CTR, Avg CPC, Conversion Rate

---

#### `list_ad_groups`
List ad groups with optional campaign and status filters.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `status` | No | Filter: `all`, `enabled`, `paused`, `removed` |
| `limit` | No | Max results 1-1000 (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `get_ad_group_performance`
Get performance metrics for ad groups over a date range.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `ad_group_id` | No | Specific ad group ID |
| `status` | No | Filter: `all`, `enabled`, `paused`, `removed` |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results 1-1000 (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

**Metrics returned:** Impressions, Clicks, Cost, Conversions, CTR, Avg CPC, Conversion Rate

---

### Ads, Keywords & Search Terms

#### `gads_list_ad_group_ads`
List ads within ad groups with creative details, performance metrics, and policy status.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `ad_group_id` | No | Filter by ad group ID |
| `status` | No | Filter: `all`, `enabled`, `paused`, `removed` |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results 1-1000 (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

**Fields returned:** Ad ID, Name, Type, Status, Approval Status, Review Status, Ad Group, Campaign, Impressions, Clicks, Cost, Conversions, CTR

---

#### `list_keywords`
List keywords with optional campaign and ad group filters.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `ad_group_id` | No | Filter by ad group ID |
| `limit` | No | Max results 1-1000 (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `get_keyword_performance`
Get performance metrics for keywords over a date range.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `ad_group_id` | No | Filter by ad group ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results 1-1000 (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `search_terms_report`
Get search terms report showing actual queries that triggered ads.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `ad_group_id` | No | Filter by ad group ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results 1-5000 (default: 100) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

### Labels

#### `gads_list_labels`
List all labels in the Google Ads account.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_campaign_labels`
List campaign-label associations.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `label_id` | No | Filter by label ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_ad_group_labels`
List ad group-label associations.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | No | Filter by ad group ID |
| `label_id` | No | Filter by label ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_ad_group_ad_labels`
List ad-label associations.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `label_id` | No | Filter by label ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_ad_group_criterion_labels`
List criterion-label associations.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `label_id` | No | Filter by label ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_customer_labels`
List customer-label associations.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

### Audiences & Interests

#### `gads_list_audiences`
List audience segments with targeting info and performance metrics.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_user_interests`
List available user interest categories for audience targeting.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `taxonomy_type` | No | Filter by taxonomy type |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

### Budgets, Bidding & History

#### `gads_list_campaign_budgets`
List campaign budgets with detailed configuration.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_get_bidding_strategies`
Get campaign-level bidding strategy configuration.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_get_ad_group_bidding_strategies`
Get ad group-level bidding information including CPC bids and targets.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_change_history`
List change history for account entities showing recent modifications.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `resource_type` | No | Filter by resource type |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

### Account Hierarchy

#### `gads_list_customer_clients`
List client accounts under a manager (MCC) account.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Manager account customer ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_list_accessible_customers`
List all customer accounts accessible with current credentials.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `response_format` | No | `markdown` or `json` |

---

### Performance Views

#### `gads_geographic_view`
Get location-based performance data from geographic view.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_shopping_performance_view`
Get product-level shopping performance data.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_display_keyword_view`
Get display keyword performance data.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_topic_view`
Get topic targeting performance data.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_user_location_view`
Get user location performance data showing where users are physically located.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_click_view`
Get click-level data including GCLID, location, and device info.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | No | Filter by campaign ID |
| `start_date` | No | Start date YYYY-MM-DD (default: 30 days ago) |
| `end_date` | No | End date YYYY-MM-DD (default: today) |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

### Keyword Planner & GAQL

#### `gads_generate_keyword_ideas`
Generate keyword suggestions using Google Ads Keyword Planner.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `keywords` | Yes | Seed keywords (comma-separated or list) |
| `language_id` | No | Language criterion ID (default: English) |
| `geo_target_id` | No | Geo target criterion ID |
| `limit` | No | Max results (default: 50) |
| `offset` | No | Pagination offset |
| `response_format` | No | `markdown` or `json` |

---

#### `gads_execute_gaql`
Execute a custom Google Ads Query Language (GAQL) query.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `query` | Yes | Full GAQL query string |
| `limit` | No | Max results |
| `response_format` | No | `markdown` or `json` |

---

## Write Tools (26)

### Campaign Management

#### `gads_create_campaign`
Create a new campaign with budget and bidding strategy.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `name` | Yes | Campaign name |
| `campaign_type` | Yes | `SEARCH`, `DISPLAY`, `SHOPPING`, `VIDEO`, `PERFORMANCE_MAX`, `DEMAND_GEN` |
| `bidding_strategy_type` | Yes | `MANUAL_CPC`, `TARGET_CPA`, `TARGET_ROAS`, `MAXIMIZE_CONVERSIONS`, `MAXIMIZE_CONVERSION_VALUE`, `MAXIMIZE_CLICKS` |
| `budget_amount_micros` | Yes | Daily budget in micros (e.g. `10000000` = $10) |
| `start_date` | No | Start date YYYY-MM-DD |
| `end_date` | No | End date YYYY-MM-DD |
| `target_cpa_micros` | No | Target CPA in micros (for TARGET_CPA) |
| `target_roas` | No | Target ROAS (for TARGET_ROAS) |

---

#### `gads_update_campaign`
Update campaign settings (name, start/end dates).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID to update |
| `name` | No | New campaign name |
| `start_date` | No | New start date YYYY-MM-DD |
| `end_date` | No | New end date YYYY-MM-DD |

---

#### `gads_set_campaign_status`
Change a campaign's status (enable, pause, or remove).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `status` | Yes | `enable`, `pause`, or `remove` |

---

#### `gads_update_budget`
Update a campaign's daily budget.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `budget_id` | Yes | Budget resource ID |
| `amount_micros` | Yes | New daily budget in micros |

---

#### `gads_set_bidding_strategy`
Set or change a campaign's bidding strategy.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `strategy_type` | Yes | `MANUAL_CPC`, `TARGET_CPA`, `TARGET_ROAS`, `MAXIMIZE_CONVERSIONS`, `MAXIMIZE_CONVERSION_VALUE`, `MAXIMIZE_CLICKS` |
| `target_cpa_micros` | No | Target CPA in micros |
| `target_roas` | No | Target ROAS |

---

### Ad Group & Ad Management

#### `gads_create_ad_group`
Create a new ad group in a campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Parent campaign ID |
| `name` | Yes | Ad group name |
| `ad_group_type` | Yes | `SEARCH_STANDARD`, `DISPLAY_STANDARD`, `SHOPPING_PRODUCT`, `VIDEO_RESPONSIVE` |
| `cpc_bid_micros` | No | Default CPC bid in micros |

---

#### `gads_set_ad_group_status`
Change an ad group's status (enable, pause, or remove).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Ad group ID |
| `status` | Yes | `enable`, `pause`, or `remove` |

---

#### `gads_set_ad_status`
Change an ad's status (enable, pause, or remove).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Ad group ID containing the ad |
| `ad_id` | Yes | Ad ID |
| `status` | Yes | `enable`, `pause`, or `remove` |

---

#### `gads_create_responsive_search_ad`
Create a Responsive Search Ad (RSA) in an ad group.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Target ad group ID |
| `headlines` | No | List of headlines (3-15, max 30 chars each) |
| `descriptions` | No | List of descriptions (2-4, max 90 chars each) |
| `final_urls` | No | Landing page URLs |
| `path1` | No | Display URL path 1 (max 15 chars) |
| `path2` | No | Display URL path 2 (max 15 chars) |

---

#### `gads_create_ad_extension`
Create an ad extension (sitelink, callout, call, or structured snippet).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign to attach extension to |
| `extension_type` | Yes | `SITELINK`, `CALLOUT`, `CALL`, `STRUCTURED_SNIPPET` |
| `link_text` | No | Sitelink text |
| `final_urls` | No | Sitelink URLs |
| `description1` | No | Sitelink description line 1 |
| `description2` | No | Sitelink description line 2 |
| `callout_text` | No | Callout text |
| `phone_number` | No | Call extension phone number |
| `country_code` | No | Phone country code |
| `snippet_header` | No | Structured snippet header |
| `snippet_values` | No | Structured snippet values |

---

### Keywords

#### `gads_add_keywords`
Add positive keywords to an ad group.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Target ad group ID |
| `keywords` | No | List of keyword strings |
| `match_type` | No | `exact`, `phrase`, or `broad` |
| `cpc_bid_micros` | No | CPC bid in micros |

---

#### `gads_update_keyword`
Update a keyword's bid or status.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Ad group ID |
| `criterion_id` | Yes | Keyword criterion ID |
| `cpc_bid_micros` | No | New CPC bid in micros |
| `status` | No | `enable`, `pause`, or `remove` |

---

#### `gads_add_negative_keywords`
Add negative keywords to a campaign or ad group.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `level` | Yes | `campaign` or `ad_group` |
| `campaign_id` | No | Campaign ID (required if level=campaign) |
| `ad_group_id` | No | Ad group ID (required if level=ad_group) |
| `keywords` | No | List of negative keyword strings |
| `match_type` | No | `exact`, `phrase`, or `broad` |

---

### Ad Creation (Advanced)

#### `gads_create_responsive_display_ad`
Create a Responsive Display Ad in an ad group.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Target ad group ID |
| `marketing_image_asset_ids` | No | Marketing image asset IDs |
| `headlines` | No | Short headlines (max 30 chars) |
| `long_headline` | No | Long headline (max 90 chars) |
| `descriptions` | No | Descriptions (max 90 chars) |
| `business_name` | No | Business name (max 25 chars) |
| `final_urls` | No | Landing page URLs |
| `logo_asset_ids` | No | Logo asset IDs |
| `square_image_asset_ids` | No | Square marketing image asset IDs |

---

#### `gads_create_demand_gen_ad`
Create a Demand Gen multi-asset ad.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Target ad group ID |
| `headlines` | No | Headlines |
| `descriptions` | No | Descriptions |
| `marketing_image_asset_ids` | No | Marketing image asset IDs |
| `logo_asset_id` | No | Logo asset ID |
| `business_name` | No | Business name |
| `final_urls` | No | Landing page URLs |
| `call_to_action` | No | CTA type |

---

#### `gads_create_video_ad`
Create a video ad in an ad group.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `ad_group_id` | Yes | Target ad group ID |
| `video_asset_id` | Yes | YouTube video asset ID |
| `ad_format` | Yes | `IN_STREAM_SKIPPABLE`, `IN_STREAM_NON_SKIPPABLE`, `BUMPER`, `VIDEO_RESPONSIVE` |
| `headline` | No | Ad headline |
| `description` | No | Ad description |
| `final_url` | No | Landing page URL |
| `display_url` | No | Display URL |
| `companion_banner_asset_id` | No | Companion banner asset ID |

---

### Targeting

#### `gads_set_location_targeting`
Set location targeting for a campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `location_ids` | No | Google Geo Target constant IDs |
| `exclude` | No | Exclude locations instead of targeting |

---

#### `gads_set_language_targeting`
Set language targeting for a campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `language_ids` | No | Language criterion IDs |

---

#### `gads_set_device_targeting`
Set device bid adjustment for a campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `device` | Yes | `MOBILE`, `DESKTOP`, or `TABLET` |
| `bid_modifier` | Yes | Bid modifier (e.g. `1.2` = +20%, `0` = exclude) |

---

#### `gads_set_demographic_targeting`
Set demographic targeting for a campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `dimension` | Yes | `AGE`, `GENDER`, `PARENTAL_STATUS`, or `INCOME` |
| `values` | No | Target values for the dimension |
| `bid_modifier` | No | Bid modifier |

---

#### `gads_create_audience_segment`
Add an audience segment to a campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `audience_type` | Yes | `IN_MARKET`, `AFFINITY`, `CUSTOM_INTENT`, `REMARKETING` |
| `audience_id` | Yes | Audience segment ID |
| `bid_modifier` | No | Bid modifier |

---

### Assets & Shopping

#### `gads_create_asset`
Create a reusable asset (text, image, video, or CTA).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `asset_type` | Yes | `TEXT`, `IMAGE`, `YOUTUBE_VIDEO`, `MEDIA_BUNDLE`, `CALL_TO_ACTION` |
| `name` | Yes | Asset name |
| `text_content` | No | Text content (for TEXT type) |
| `image_url` | No | Image URL (for IMAGE type) |
| `youtube_video_id` | No | YouTube video ID (for YOUTUBE_VIDEO type) |
| `call_to_action_type` | No | CTA type (for CALL_TO_ACTION type) |

---

#### `gads_create_asset_group`
Create an asset group for a Performance Max or Demand Gen campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | PMax/DG campaign ID |
| `name` | Yes | Asset group name |
| `final_urls` | No | Landing page URLs |
| `final_mobile_urls` | No | Mobile landing page URLs |
| `path1` | No | Display URL path 1 |
| `path2` | No | Display URL path 2 |

---

#### `gads_add_asset_group_assets`
Link assets to an asset group (for PMax/DG campaigns).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `asset_group_id` | Yes | Asset group ID |
| `asset_ids` | No | Asset IDs to link |
| `field_types` | No | Asset field types (`HEADLINE`, `DESCRIPTION`, `MARKETING_IMAGE`, `LOGO`, etc.) |

---

#### `gads_set_listing_group_filter`
Set a listing group filter for a PMax or Shopping asset group.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `asset_group_id` | Yes | Asset group ID |
| `filter_type` | Yes | Filter type |
| `dimension` | Yes | `BRAND`, `CATEGORY_L1`, `CATEGORY_L2`, `PRODUCT_TYPE_L1`, `PRODUCT_TYPE_L2`, `CUSTOM_LABEL_0`, `CUSTOM_LABEL_1`, `ITEM_ID`, `CONDITION` |
| `value` | No | Dimension value |
| `parent_filter_id` | No | Parent filter ID for subdivision |

---

#### `gads_link_merchant_center`
Link a Merchant Center account to a Shopping or PMax campaign.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `campaign_id` | Yes | Campaign ID |
| `merchant_id` | Yes | Merchant Center account ID |
| `feed_label` | No | Feed label |
| `sales_country` | No | Sales country code |

---

### Conversions & Customer Lists

#### `gads_upload_click_conversions`
Upload an offline click conversion to Google Ads.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `conversion_action_id` | Yes | Conversion action resource ID |
| `gclid` | Yes | Google Click ID |
| `conversion_date_time` | Yes | Conversion datetime (YYYY-MM-DD HH:MM:SS+HH:MM) |
| `conversion_value` | No | Conversion value |
| `currency_code` | No | Currency code (e.g. `USD`, `EUR`) |

---

#### `gads_upload_customer_list`
Upload members to a customer match list.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `user_list_id` | Yes | User list resource ID |
| `emails` | No | List of email addresses (SHA256 hashed) |
| `phones` | No | List of phone numbers (SHA256 hashed) |

---

#### `gads_remove_customer_list_members`
Remove members from a customer match list.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `customer_id` | Yes | Google Ads customer ID |
| `user_list_id` | Yes | User list resource ID |
| `emails` | No | Email addresses to remove |
| `phones` | No | Phone numbers to remove |

---

## Common Parameters

All read tools share these common parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `customer_id` | — | Required. Accepts `1234567890` or `123-456-7890` format |
| `limit` | 50 | Results per page (1-1000) |
| `offset` | 0 | Pagination offset |
| `response_format` | `markdown` | `markdown` for readable tables, `json` for structured data |

Date range tools default to the **last 30 days** when `start_date` and `end_date` are omitted.

## Currency Values

All monetary values use **micros** (1 unit = 1,000,000 micros):

| Amount | Micros Value |
|--------|-------------|
| $1.00 | `1000000` |
| $10.00 | `10000000` |
| $50.00 | `50000000` |
| $100.00 | `100000000` |
