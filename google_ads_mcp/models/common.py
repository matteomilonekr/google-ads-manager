"""Common models shared across all Google Ads MCP tools."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class CampaignStatusFilter(str, Enum):
    """Filter for campaign status."""
    ALL = "all"
    ENABLED = "enabled"
    PAUSED = "paused"
    REMOVED = "removed"


class AdGroupStatusFilter(str, Enum):
    """Filter for ad group status."""
    ALL = "all"
    ENABLED = "enabled"
    PAUSED = "paused"
    REMOVED = "removed"


class CampaignTypeFilter(str, Enum):
    """Filter for campaign type."""
    ALL = "all"
    SEARCH = "search"
    DISPLAY = "display"
    SHOPPING = "shopping"
    VIDEO = "video"
    PERFORMANCE_MAX = "performance_max"
    DEMAND_GEN = "demand_gen"
    APP = "app"
    SMART = "smart"
    HOTEL = "hotel"
    LOCAL = "local"
    LOCAL_SERVICES = "local_services"
    TRAVEL = "travel"


class MatchType(str, Enum):
    """Keyword match type."""
    EXACT = "exact"
    PHRASE = "phrase"
    BROAD = "broad"


class StatusAction(str, Enum):
    """Action to take on a resource's status."""
    ENABLE = "enable"
    PAUSE = "pause"
    REMOVE = "remove"


class NegativeKeywordLevel(str, Enum):
    """Level at which to add negative keywords."""
    CAMPAIGN = "campaign"
    AD_GROUP = "ad_group"


class CampaignType(str, Enum):
    """Campaign type for creation."""
    SEARCH = "SEARCH"
    DISPLAY = "DISPLAY"
    SHOPPING = "SHOPPING"
    VIDEO = "VIDEO"
    PERFORMANCE_MAX = "PERFORMANCE_MAX"
    DEMAND_GEN = "DEMAND_GEN"


class BiddingStrategyType(str, Enum):
    """Bidding strategy type."""
    MANUAL_CPC = "MANUAL_CPC"
    TARGET_CPA = "TARGET_CPA"
    TARGET_ROAS = "TARGET_ROAS"
    MAXIMIZE_CONVERSIONS = "MAXIMIZE_CONVERSIONS"
    MAXIMIZE_CONVERSION_VALUE = "MAXIMIZE_CONVERSION_VALUE"
    MAXIMIZE_CLICKS = "MAXIMIZE_CLICKS"


class AdGroupType(str, Enum):
    """Ad group type for creation."""
    SEARCH_STANDARD = "SEARCH_STANDARD"
    DISPLAY_STANDARD = "DISPLAY_STANDARD"
    SHOPPING_PRODUCT = "SHOPPING_PRODUCT"
    VIDEO_RESPONSIVE = "VIDEO_RESPONSIVE"


class ExtensionType(str, Enum):
    """Ad extension type."""
    SITELINK = "SITELINK"
    CALLOUT = "CALLOUT"
    CALL = "CALL"
    STRUCTURED_SNIPPET = "STRUCTURED_SNIPPET"


class DeviceType(str, Enum):
    """Device type for targeting."""
    MOBILE = "MOBILE"
    DESKTOP = "DESKTOP"
    TABLET = "TABLET"


class DemographicDimension(str, Enum):
    """Demographic targeting dimension."""
    AGE = "AGE"
    GENDER = "GENDER"
    PARENTAL_STATUS = "PARENTAL_STATUS"
    INCOME = "INCOME"


class AudienceType(str, Enum):
    """Audience segment type."""
    IN_MARKET = "IN_MARKET"
    AFFINITY = "AFFINITY"
    CUSTOM_INTENT = "CUSTOM_INTENT"
    REMARKETING = "REMARKETING"


class AssetType(str, Enum):
    """Asset type for creation."""
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    YOUTUBE_VIDEO = "YOUTUBE_VIDEO"
    MEDIA_BUNDLE = "MEDIA_BUNDLE"
    CALL_TO_ACTION = "CALL_TO_ACTION"


class AssetFieldType(str, Enum):
    """Asset field type for linking assets to asset groups."""
    HEADLINE = "HEADLINE"
    DESCRIPTION = "DESCRIPTION"
    LONG_HEADLINE = "LONG_HEADLINE"
    BUSINESS_NAME = "BUSINESS_NAME"
    MARKETING_IMAGE = "MARKETING_IMAGE"
    SQUARE_MARKETING_IMAGE = "SQUARE_MARKETING_IMAGE"
    LOGO = "LOGO"
    LANDSCAPE_LOGO = "LANDSCAPE_LOGO"
    YOUTUBE_VIDEO = "YOUTUBE_VIDEO"
    CALL_TO_ACTION_SELECTION = "CALL_TO_ACTION_SELECTION"


class VideoAdFormat(str, Enum):
    """Video ad format."""
    IN_STREAM_SKIPPABLE = "IN_STREAM_SKIPPABLE"
    IN_STREAM_NON_SKIPPABLE = "IN_STREAM_NON_SKIPPABLE"
    BUMPER = "BUMPER"
    VIDEO_RESPONSIVE = "VIDEO_RESPONSIVE"


class ListingGroupDimension(str, Enum):
    """Listing group filter dimension for Shopping/PMax."""
    BRAND = "BRAND"
    CATEGORY_L1 = "CATEGORY_L1"
    CATEGORY_L2 = "CATEGORY_L2"
    PRODUCT_TYPE_L1 = "PRODUCT_TYPE_L1"
    PRODUCT_TYPE_L2 = "PRODUCT_TYPE_L2"
    CUSTOM_LABEL_0 = "CUSTOM_LABEL_0"
    CUSTOM_LABEL_1 = "CUSTOM_LABEL_1"
    ITEM_ID = "ITEM_ID"
    CONDITION = "CONDITION"


def sanitize_customer_id(value: str) -> str:
    """Sanitize and validate a Google Ads customer ID.

    Removes dashes, strips whitespace, validates 10-digit format.

    Args:
        value: Raw customer ID string.

    Returns:
        Sanitized 10-digit customer ID.

    Raises:
        ValueError: If format is invalid.
    """
    cleaned = value.strip().replace("-", "")
    if not cleaned.isdigit():
        raise ValueError(f"Customer ID must be numeric, got: '{value}'")
    if len(cleaned) != 10:
        raise ValueError(f"Customer ID must be 10 digits, got {len(cleaned)} digits")
    return cleaned


class CustomerIdMixin(BaseModel):
    """Mixin providing customer_id field with auto-sanitization."""

    model_config = ConfigDict(str_strip_whitespace=True)

    customer_id: str = Field(
        ...,
        description="Google Ads customer ID (e.g. '1234567890' or '123-456-7890')",
    )

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: str) -> str:
        return sanitize_customer_id(v)
