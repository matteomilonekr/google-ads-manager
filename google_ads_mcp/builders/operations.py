"""Build Google Ads API mutate operations.

Each builder takes the raw GoogleAdsClient (not the wrapper) plus IDs and
values, and returns a MutateOperation proto ready for client.mutate().
"""

from __future__ import annotations

from typing import Any

from google.ads.googleads.client import GoogleAdsClient


# CampaignStatus / AdGroupStatus / AdGroupAdStatus numeric values
STATUS_TO_ENUM: dict[str, int] = {
    "enable": 2,   # ENABLED
    "pause": 3,    # PAUSED
    "remove": 4,   # REMOVED
}

MATCH_TYPE_TO_ENUM: dict[str, int] = {
    "exact": 2,    # EXACT
    "phrase": 3,   # PHRASE
    "broad": 4,    # BROAD
}

CAMPAIGN_TYPE_TO_ENUM: dict[str, int] = {
    "SEARCH": 2,
    "DISPLAY": 3,
    "SHOPPING": 4,
    "VIDEO": 6,
    "PERFORMANCE_MAX": 14,
    "DEMAND_GEN": 15,
}

AD_GROUP_TYPE_TO_ENUM: dict[str, int] = {
    "SEARCH_STANDARD": 2,
    "DISPLAY_STANDARD": 3,
    "SHOPPING_PRODUCT": 4,
    "VIDEO_RESPONSIVE": 9,
}

DEVICE_TYPE_TO_CRITERION: dict[str, int] = {
    "MOBILE": 30001,
    "DESKTOP": 30000,
    "TABLET": 30002,
}

BUDGET_DELIVERY_STANDARD = 2

BIDDING_STRATEGY_MAP: dict[str, str] = {
    "MANUAL_CPC": "manual_cpc",
    "TARGET_CPA": "target_cpa",
    "TARGET_ROAS": "target_roas",
    "MAXIMIZE_CONVERSIONS": "maximize_conversions",
    "MAXIMIZE_CONVERSION_VALUE": "maximize_conversion_value",
    "MAXIMIZE_CLICKS": "maximize_clicks",
}

ASSET_TYPE_TO_ENUM: dict[str, int] = {
    "TEXT": 4,
    "IMAGE": 5,
    "YOUTUBE_VIDEO": 2,
    "MEDIA_BUNDLE": 3,
    "CALL_TO_ACTION": 30,
}

ASSET_FIELD_TYPE_TO_ENUM: dict[str, int] = {
    "HEADLINE": 2,
    "DESCRIPTION": 3,
    "LONG_HEADLINE": 19,
    "BUSINESS_NAME": 12,
    "MARKETING_IMAGE": 4,
    "SQUARE_MARKETING_IMAGE": 11,
    "LOGO": 5,
    "LANDSCAPE_LOGO": 14,
    "YOUTUBE_VIDEO": 7,
    "CALL_TO_ACTION_SELECTION": 20,
}

LISTING_GROUP_FILTER_TYPE_TO_ENUM: dict[str, int] = {
    "UNIT_INCLUDED": 2,
    "UNIT_EXCLUDED": 3,
    "SUBDIVISION": 4,
}


def _resource_name(customer_id: str, resource: str, resource_id: str) -> str:
    """Build a Google Ads resource name string."""
    return f"customers/{customer_id}/{resource}/{resource_id}"


def build_campaign_status_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    status: str,
) -> Any:
    """Build a MutateOperation to change campaign status."""
    mutate_op = client.get_type("MutateOperation")
    campaign_op = mutate_op.campaign_operation
    campaign = campaign_op.update
    campaign.resource_name = _resource_name(customer_id, "campaigns", campaign_id)
    campaign.status = STATUS_TO_ENUM[status]
    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")
    campaign_op.update_mask.CopyFrom(field_mask)
    return mutate_op


def build_campaign_update_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    name: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Any:
    """Build a MutateOperation to update campaign fields."""
    mutate_op = client.get_type("MutateOperation")
    campaign_op = mutate_op.campaign_operation
    campaign = campaign_op.update
    campaign.resource_name = _resource_name(customer_id, "campaigns", campaign_id)

    paths: list[str] = []
    if name is not None:
        campaign.name = name
        paths.append("name")
    if start_date is not None:
        campaign.start_date = start_date
        paths.append("start_date")
    if end_date is not None:
        campaign.end_date = end_date
        paths.append("end_date")

    field_mask = client.get_type("FieldMask")
    field_mask.paths.extend(paths)
    campaign_op.update_mask.CopyFrom(field_mask)
    return mutate_op


def build_ad_group_status_operation(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    status: str,
) -> Any:
    """Build a MutateOperation to change ad group status."""
    mutate_op = client.get_type("MutateOperation")
    ag_op = mutate_op.ad_group_operation
    ad_group = ag_op.update
    ad_group.resource_name = _resource_name(customer_id, "adGroups", ad_group_id)
    ad_group.status = STATUS_TO_ENUM[status]
    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")
    ag_op.update_mask.CopyFrom(field_mask)
    return mutate_op


def build_ad_status_operation(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    status: str,
) -> Any:
    """Build a MutateOperation to change ad status."""
    mutate_op = client.get_type("MutateOperation")
    ad_op = mutate_op.ad_group_ad_operation
    ad_group_ad = ad_op.update
    ad_group_ad.resource_name = _resource_name(
        customer_id, "adGroupAds", f"{ad_group_id}~{ad_id}"
    )
    ad_group_ad.status = STATUS_TO_ENUM[status]
    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")
    ad_op.update_mask.CopyFrom(field_mask)
    return mutate_op


def build_budget_update_operation(
    client: GoogleAdsClient,
    customer_id: str,
    budget_id: str,
    amount_micros: int,
) -> Any:
    """Build a MutateOperation to update a campaign budget."""
    mutate_op = client.get_type("MutateOperation")
    budget_op = mutate_op.campaign_budget_operation
    budget = budget_op.update
    budget.resource_name = _resource_name(customer_id, "campaignBudgets", budget_id)
    budget.amount_micros = amount_micros
    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("amount_micros")
    budget_op.update_mask.CopyFrom(field_mask)
    return mutate_op


def build_negative_keyword_operations(
    client: GoogleAdsClient,
    customer_id: str,
    level: str,
    parent_id: str,
    keywords: list[str],
    match_type: str,
) -> list[Any]:
    """Build MutateOperations to add negative keywords."""
    ops: list[Any] = []
    mt_enum = MATCH_TYPE_TO_ENUM[match_type]

    for keyword_text in keywords:
        mutate_op = client.get_type("MutateOperation")

        if level == "campaign":
            criterion_op = mutate_op.campaign_criterion_operation
            criterion = criterion_op.create
            criterion.campaign = _resource_name(customer_id, "campaigns", parent_id)
            criterion.negative = True
            criterion.keyword.text = keyword_text
            criterion.keyword.match_type = mt_enum
        else:
            criterion_op = mutate_op.ad_group_criterion_operation
            criterion = criterion_op.create
            criterion.ad_group = _resource_name(customer_id, "adGroups", parent_id)
            criterion.negative = True
            criterion.keyword.text = keyword_text
            criterion.keyword.match_type = mt_enum

        ops.append(mutate_op)

    return ops


def build_location_criterion_operations(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    location_ids: list[int],
    exclude: bool,
) -> list[Any]:
    """Build MutateOperations for location targeting."""
    ops: list[Any] = []

    for loc_id in location_ids:
        mutate_op = client.get_type("MutateOperation")
        criterion_op = mutate_op.campaign_criterion_operation
        criterion = criterion_op.create
        criterion.campaign = _resource_name(customer_id, "campaigns", campaign_id)
        criterion.location.geo_target_constant = f"geoTargetConstants/{loc_id}"
        if exclude:
            criterion.negative = True
        ops.append(mutate_op)

    return ops


def build_language_criterion_operations(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    language_ids: list[int],
) -> list[Any]:
    """Build MutateOperations for language targeting."""
    ops: list[Any] = []

    for lang_id in language_ids:
        mutate_op = client.get_type("MutateOperation")
        criterion_op = mutate_op.campaign_criterion_operation
        criterion = criterion_op.create
        criterion.campaign = _resource_name(customer_id, "campaigns", campaign_id)
        criterion.language.language_constant = f"languageConstants/{lang_id}"
        ops.append(mutate_op)

    return ops


def build_create_campaign_operations(
    client: GoogleAdsClient,
    customer_id: str,
    name: str,
    campaign_type: str,
    bidding_strategy_type: str,
    budget_amount_micros: int,
    start_date: str | None = None,
    end_date: str | None = None,
    target_cpa_micros: int | None = None,
    target_roas: float | None = None,
) -> list[Any]:
    """Build MutateOperations to create a campaign with budget (atomic batch)."""
    ops: list[Any] = []

    # Operation 1: Create budget with temp resource name
    budget_op = client.get_type("MutateOperation")
    budget = budget_op.campaign_budget_operation.create
    budget.name = f"{name} Budget"
    budget.amount_micros = budget_amount_micros
    budget.delivery_method = BUDGET_DELIVERY_STANDARD
    budget.resource_name = f"customers/{customer_id}/campaignBudgets/-1"
    ops.append(budget_op)

    # Operation 2: Create campaign referencing temp budget
    campaign_op = client.get_type("MutateOperation")
    campaign = campaign_op.campaign_operation.create
    campaign.name = name
    campaign.advertising_channel_type = CAMPAIGN_TYPE_TO_ENUM[campaign_type]
    campaign.status = STATUS_TO_ENUM["pause"]
    campaign.campaign_budget = f"customers/{customer_id}/campaignBudgets/-1"

    # Set bidding strategy
    strategy_field = BIDDING_STRATEGY_MAP[bidding_strategy_type]
    bidding = getattr(campaign, strategy_field)
    if bidding_strategy_type == "TARGET_CPA" and target_cpa_micros is not None:
        bidding.target_cpa_micros = target_cpa_micros
    elif bidding_strategy_type == "TARGET_ROAS" and target_roas is not None:
        bidding.target_roas = target_roas

    if start_date is not None:
        campaign.start_date = start_date
    if end_date is not None:
        campaign.end_date = end_date

    ops.append(campaign_op)
    return ops


def build_create_ad_group_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    name: str,
    ad_group_type: str,
    cpc_bid_micros: int | None = None,
) -> Any:
    """Build a MutateOperation to create an ad group."""
    mutate_op = client.get_type("MutateOperation")
    ad_group = mutate_op.ad_group_operation.create
    ad_group.name = name
    ad_group.campaign = _resource_name(customer_id, "campaigns", campaign_id)
    ad_group.type_ = AD_GROUP_TYPE_TO_ENUM[ad_group_type]
    ad_group.status = STATUS_TO_ENUM["enable"]
    if cpc_bid_micros is not None:
        ad_group.cpc_bid_micros = cpc_bid_micros
    return mutate_op


def build_create_rsa_operation(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    headlines: list[str],
    descriptions: list[str],
    final_urls: list[str],
    path1: str | None = None,
    path2: str | None = None,
) -> Any:
    """Build a MutateOperation to create a Responsive Search Ad."""
    mutate_op = client.get_type("MutateOperation")
    ad_group_ad = mutate_op.ad_group_ad_operation.create
    ad_group_ad.ad_group = _resource_name(customer_id, "adGroups", ad_group_id)
    ad_group_ad.status = STATUS_TO_ENUM["enable"]

    ad = ad_group_ad.ad
    ad.final_urls.extend(final_urls)

    for headline_text in headlines:
        headline = client.get_type("AdTextAsset")
        headline.text = headline_text
        ad.responsive_search_ad.headlines.append(headline)

    for desc_text in descriptions:
        desc = client.get_type("AdTextAsset")
        desc.text = desc_text
        ad.responsive_search_ad.descriptions.append(desc)

    if path1 is not None:
        ad.responsive_search_ad.path1 = path1
    if path2 is not None:
        ad.responsive_search_ad.path2 = path2

    return mutate_op


def build_add_keywords_operations(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    keywords: list[str],
    match_type: str,
    cpc_bid_micros: int | None = None,
) -> list[Any]:
    """Build MutateOperations to add positive keywords to an ad group."""
    ops: list[Any] = []
    mt_enum = MATCH_TYPE_TO_ENUM[match_type]

    for keyword_text in keywords:
        mutate_op = client.get_type("MutateOperation")
        criterion_op = mutate_op.ad_group_criterion_operation
        criterion = criterion_op.create
        criterion.ad_group = _resource_name(customer_id, "adGroups", ad_group_id)
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = mt_enum
        if cpc_bid_micros is not None:
            criterion.cpc_bid_micros = cpc_bid_micros
        ops.append(mutate_op)

    return ops


def build_bidding_strategy_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    strategy_type: str,
    target_cpa_micros: int | None = None,
    target_roas: float | None = None,
) -> Any:
    """Build a MutateOperation to set a campaign's bidding strategy."""
    mutate_op = client.get_type("MutateOperation")
    campaign_op = mutate_op.campaign_operation
    campaign = campaign_op.update
    campaign.resource_name = _resource_name(customer_id, "campaigns", campaign_id)

    strategy_field = BIDDING_STRATEGY_MAP[strategy_type]
    bidding = getattr(campaign, strategy_field)
    if strategy_type == "TARGET_CPA" and target_cpa_micros is not None:
        bidding.target_cpa_micros = target_cpa_micros
    elif strategy_type == "TARGET_ROAS" and target_roas is not None:
        bidding.target_roas = target_roas

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append(strategy_field)
    campaign_op.update_mask.CopyFrom(field_mask)
    return mutate_op


def build_update_keyword_operation(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    criterion_id: str,
    cpc_bid_micros: int | None = None,
    status: str | None = None,
) -> Any:
    """Build a MutateOperation to update a keyword criterion."""
    mutate_op = client.get_type("MutateOperation")
    criterion_op = mutate_op.ad_group_criterion_operation
    criterion = criterion_op.update
    criterion.resource_name = _resource_name(
        customer_id, "adGroupCriteria", f"{ad_group_id}~{criterion_id}"
    )

    paths: list[str] = []
    if cpc_bid_micros is not None:
        criterion.cpc_bid_micros = cpc_bid_micros
        paths.append("cpc_bid_micros")
    if status is not None:
        criterion.status = STATUS_TO_ENUM[status]
        paths.append("status")

    field_mask = client.get_type("FieldMask")
    field_mask.paths.extend(paths)
    criterion_op.update_mask.CopyFrom(field_mask)
    return mutate_op


def build_create_extension_operation(
    client: GoogleAdsClient,
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
) -> Any:
    """Build a MutateOperation to create a campaign asset (extension)."""
    mutate_op = client.get_type("MutateOperation")
    asset_op = mutate_op.asset_operation
    asset = asset_op.create

    if extension_type == "SITELINK":
        asset.sitelink_asset.link_text = link_text
        asset.sitelink_asset.final_urls.extend(final_urls or [])
        if description1:
            asset.sitelink_asset.description1 = description1
        if description2:
            asset.sitelink_asset.description2 = description2
    elif extension_type == "CALLOUT":
        asset.callout_asset.callout_text = callout_text
    elif extension_type == "CALL":
        asset.call_asset.phone_number = phone_number
        asset.call_asset.country_code = country_code
    elif extension_type == "STRUCTURED_SNIPPET":
        asset.structured_snippet_asset.header = snippet_header
        asset.structured_snippet_asset.values.extend(snippet_values or [])

    return mutate_op


def build_device_targeting_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    device: str,
    bid_modifier: float,
) -> Any:
    """Build a MutateOperation for device bid adjustment."""
    mutate_op = client.get_type("MutateOperation")
    criterion_op = mutate_op.campaign_criterion_operation
    criterion = criterion_op.create
    criterion.campaign = _resource_name(customer_id, "campaigns", campaign_id)
    criterion.device.type_ = DEVICE_TYPE_TO_CRITERION[device]
    criterion.bid_modifier = bid_modifier
    return mutate_op


def build_demographic_targeting_operations(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    dimension: str,
    values: list[str],
    bid_modifier: float | None = None,
) -> list[Any]:
    """Build MutateOperations for demographic targeting."""
    ops: list[Any] = []

    for value in values:
        mutate_op = client.get_type("MutateOperation")
        criterion_op = mutate_op.campaign_criterion_operation
        criterion = criterion_op.create
        criterion.campaign = _resource_name(customer_id, "campaigns", campaign_id)

        if dimension == "AGE":
            criterion.age_range.type_ = value
        elif dimension == "GENDER":
            criterion.gender.type_ = value
        elif dimension == "PARENTAL_STATUS":
            criterion.parental_status.type_ = value
        elif dimension == "INCOME":
            criterion.income_range.type_ = value

        if bid_modifier is not None:
            criterion.bid_modifier = bid_modifier

        ops.append(mutate_op)

    return ops


def build_audience_segment_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    audience_type: str,
    audience_id: str,
    bid_modifier: float | None = None,
) -> Any:
    """Build a MutateOperation to add an audience segment to a campaign."""
    mutate_op = client.get_type("MutateOperation")
    criterion_op = mutate_op.campaign_criterion_operation
    criterion = criterion_op.create
    criterion.campaign = _resource_name(customer_id, "campaigns", campaign_id)

    if audience_type in ("IN_MARKET", "AFFINITY", "CUSTOM_INTENT"):
        criterion.user_interest.user_interest_category = (
            f"customers/{customer_id}/userInterests/{audience_id}"
        )
    elif audience_type == "REMARKETING":
        criterion.user_list.user_list = (
            f"customers/{customer_id}/userLists/{audience_id}"
        )

    if bid_modifier is not None:
        criterion.bid_modifier = bid_modifier

    return mutate_op


def build_create_asset_operation(
    client: GoogleAdsClient,
    customer_id: str,
    asset_type: str,
    name: str,
    text_content: str | None = None,
    image_data: bytes | None = None,
    youtube_video_id: str | None = None,
    call_to_action_type: str | None = None,
) -> Any:
    """Build a MutateOperation to create an asset."""
    mutate_op = client.get_type("MutateOperation")
    asset = mutate_op.asset_operation.create
    asset.name = name
    asset.type_ = ASSET_TYPE_TO_ENUM[asset_type]

    if asset_type == "TEXT":
        asset.text_asset.text = text_content
    elif asset_type == "IMAGE":
        asset.image_asset.data = image_data
        asset.image_asset.file_size = len(image_data) if image_data else 0
    elif asset_type == "YOUTUBE_VIDEO":
        asset.youtube_video_asset.youtube_video_id = youtube_video_id
    elif asset_type == "CALL_TO_ACTION":
        asset.call_to_action_asset.call_to_action = call_to_action_type

    return mutate_op


def build_create_asset_group_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    name: str,
    final_urls: list[str],
    final_mobile_urls: list[str] | None = None,
    path1: str | None = None,
    path2: str | None = None,
) -> Any:
    """Build a MutateOperation to create an asset group."""
    mutate_op = client.get_type("MutateOperation")
    asset_group = mutate_op.asset_group_operation.create
    asset_group.name = name
    asset_group.campaign = _resource_name(customer_id, "campaigns", campaign_id)
    asset_group.final_urls.extend(final_urls)
    asset_group.status = STATUS_TO_ENUM["enable"]

    if final_mobile_urls:
        asset_group.final_mobile_urls.extend(final_mobile_urls)
    if path1 is not None:
        asset_group.path1 = path1
    if path2 is not None:
        asset_group.path2 = path2

    return mutate_op


def build_asset_group_asset_operations(
    client: GoogleAdsClient,
    customer_id: str,
    asset_group_id: str,
    assets: list[dict[str, str]],
) -> list[Any]:
    """Build MutateOperations to link assets to an asset group."""
    ops: list[Any] = []

    for assignment in assets:
        mutate_op = client.get_type("MutateOperation")
        aga = mutate_op.asset_group_asset_operation.create
        aga.asset_group = _resource_name(customer_id, "assetGroups", asset_group_id)
        aga.asset = _resource_name(customer_id, "assets", assignment["asset_id"])
        aga.field_type = ASSET_FIELD_TYPE_TO_ENUM[assignment["field_type"]]
        ops.append(mutate_op)

    return ops


def build_responsive_display_ad_operation(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    marketing_image_asset_ids: list[str],
    headlines: list[str],
    long_headline: str,
    descriptions: list[str],
    business_name: str,
    final_urls: list[str],
    logo_asset_ids: list[str] | None = None,
    square_image_asset_ids: list[str] | None = None,
) -> Any:
    """Build a MutateOperation to create a Responsive Display Ad."""
    mutate_op = client.get_type("MutateOperation")
    ad_group_ad = mutate_op.ad_group_ad_operation.create
    ad_group_ad.ad_group = _resource_name(customer_id, "adGroups", ad_group_id)
    ad_group_ad.status = STATUS_TO_ENUM["enable"]

    ad = ad_group_ad.ad
    ad.final_urls.extend(final_urls)

    rda = ad.responsive_display_ad

    for img_id in marketing_image_asset_ids:
        img_asset = client.get_type("AdImageAsset")
        img_asset.asset = _resource_name(customer_id, "assets", img_id)
        rda.marketing_images.append(img_asset)

    if square_image_asset_ids:
        for img_id in square_image_asset_ids:
            img_asset = client.get_type("AdImageAsset")
            img_asset.asset = _resource_name(customer_id, "assets", img_id)
            rda.square_marketing_images.append(img_asset)

    if logo_asset_ids:
        for logo_id in logo_asset_ids:
            logo_asset = client.get_type("AdImageAsset")
            logo_asset.asset = _resource_name(customer_id, "assets", logo_id)
            rda.logo_images.append(logo_asset)

    for headline_text in headlines:
        h = client.get_type("AdTextAsset")
        h.text = headline_text
        rda.headlines.append(h)

    long_h = client.get_type("AdTextAsset")
    long_h.text = long_headline
    rda.long_headline = long_h

    for desc_text in descriptions:
        d = client.get_type("AdTextAsset")
        d.text = desc_text
        rda.descriptions.append(d)

    rda.business_name = business_name

    return mutate_op


def build_video_ad_operation(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    video_asset_id: str,
    ad_format: str,
    headline: str | None = None,
    description: str | None = None,
    final_url: str | None = None,
    display_url: str | None = None,
    companion_banner_asset_id: str | None = None,
) -> Any:
    """Build a MutateOperation to create a video ad."""
    mutate_op = client.get_type("MutateOperation")
    ad_group_ad = mutate_op.ad_group_ad_operation.create
    ad_group_ad.ad_group = _resource_name(customer_id, "adGroups", ad_group_id)
    ad_group_ad.status = STATUS_TO_ENUM["enable"]

    ad = ad_group_ad.ad
    if final_url:
        ad.final_urls.append(final_url)
    if display_url:
        ad.display_url = display_url

    video_resource = _resource_name(customer_id, "assets", video_asset_id)

    if ad_format in ("IN_STREAM_SKIPPABLE", "IN_STREAM_NON_SKIPPABLE"):
        ad.video_ad.in_stream.action_headline = headline or ""
        if companion_banner_asset_id:
            ad.video_ad.in_stream.companion_banner.asset = _resource_name(
                customer_id, "assets", companion_banner_asset_id
            )
    elif ad_format == "BUMPER":
        ad.video_ad.bumper.companion_banner  # access to initialize
    elif ad_format == "VIDEO_RESPONSIVE":
        if headline:
            h = client.get_type("AdTextAsset")
            h.text = headline
            ad.video_responsive_ad.headlines.append(h)
        if description:
            d = client.get_type("AdTextAsset")
            d.text = description
            ad.video_responsive_ad.long_headlines.append(d)

    ad.video_ad.video.asset = video_resource

    return mutate_op


def build_demand_gen_ad_operation(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    headlines: list[str],
    descriptions: list[str],
    marketing_image_asset_ids: list[str],
    logo_asset_id: str,
    business_name: str,
    final_urls: list[str],
    call_to_action: str | None = None,
) -> Any:
    """Build a MutateOperation to create a Demand Gen multi-asset ad."""
    mutate_op = client.get_type("MutateOperation")
    ad_group_ad = mutate_op.ad_group_ad_operation.create
    ad_group_ad.ad_group = _resource_name(customer_id, "adGroups", ad_group_id)
    ad_group_ad.status = STATUS_TO_ENUM["enable"]

    ad = ad_group_ad.ad
    ad.final_urls.extend(final_urls)

    dg = ad.demand_gen_multi_asset_ad

    for headline_text in headlines:
        h = client.get_type("AdTextAsset")
        h.text = headline_text
        dg.headlines.append(h)

    for desc_text in descriptions:
        d = client.get_type("AdTextAsset")
        d.text = desc_text
        dg.descriptions.append(d)

    for img_id in marketing_image_asset_ids:
        img_asset = client.get_type("AdImageAsset")
        img_asset.asset = _resource_name(customer_id, "assets", img_id)
        dg.marketing_images.append(img_asset)

    logo = client.get_type("AdImageAsset")
    logo.asset = _resource_name(customer_id, "assets", logo_asset_id)
    dg.logo_images.append(logo)

    dg.business_name = business_name

    if call_to_action:
        dg.call_to_action_text = call_to_action

    return mutate_op


def build_listing_group_filter_operation(
    client: GoogleAdsClient,
    customer_id: str,
    asset_group_id: str,
    filter_type: str,
    dimension: str,
    value: str | None = None,
    parent_filter_id: str | None = None,
) -> Any:
    """Build a MutateOperation to create a listing group filter."""
    mutate_op = client.get_type("MutateOperation")
    lgf = mutate_op.asset_group_listing_group_filter_operation.create
    lgf.asset_group = _resource_name(customer_id, "assetGroups", asset_group_id)
    lgf.type_ = LISTING_GROUP_FILTER_TYPE_TO_ENUM[filter_type]

    if parent_filter_id:
        lgf.parent_listing_group_filter = _resource_name(
            customer_id, "assetGroupListingGroupFilters", parent_filter_id
        )

    if value is not None:
        if dimension.startswith("CATEGORY"):
            lgf.case_value.product_category.category_id = int(value) if value.isdigit() else 0
            lgf.case_value.product_category.level = dimension
        elif dimension.startswith("PRODUCT_TYPE"):
            lgf.case_value.product_type.value = value
            lgf.case_value.product_type.level = dimension
        elif dimension.startswith("CUSTOM_LABEL"):
            lgf.case_value.product_custom_attribute.value = value
            lgf.case_value.product_custom_attribute.index = dimension
        elif dimension == "BRAND":
            lgf.case_value.product_brand.value = value
        elif dimension == "ITEM_ID":
            lgf.case_value.product_item_id.value = value
        elif dimension == "CONDITION":
            lgf.case_value.product_condition.condition = value

    return mutate_op


def build_merchant_center_link_operation(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    merchant_id: str,
    feed_label: str | None = None,
    sales_country: str | None = None,
) -> Any:
    """Build a MutateOperation to link Merchant Center to a campaign."""
    mutate_op = client.get_type("MutateOperation")
    campaign_op = mutate_op.campaign_operation
    campaign = campaign_op.update
    campaign.resource_name = _resource_name(customer_id, "campaigns", campaign_id)

    campaign.shopping_setting.merchant_id = int(merchant_id)
    paths = ["shopping_setting.merchant_id"]

    if feed_label:
        campaign.shopping_setting.feed_label = feed_label
        paths.append("shopping_setting.feed_label")
    if sales_country:
        campaign.shopping_setting.sales_country = sales_country
        paths.append("shopping_setting.sales_country")

    field_mask = client.get_type("FieldMask")
    field_mask.paths.extend(paths)
    campaign_op.update_mask.CopyFrom(field_mask)
    return mutate_op
