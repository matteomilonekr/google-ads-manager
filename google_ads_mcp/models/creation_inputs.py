"""Input models for Google Ads MCP Phase 4 creation tools."""

from __future__ import annotations

from datetime import date as date_type

from pydantic import Field, field_validator, model_validator

from google_ads_mcp.models.common import (
    AdGroupType,
    AudienceType,
    BiddingStrategyType,
    CampaignType,
    CustomerIdMixin,
    DemographicDimension,
    DeviceType,
    ExtensionType,
    MatchType,
    StatusAction,
)


class CreateCampaignInput(CustomerIdMixin):
    """Input for gads_create_campaign tool."""

    name: str = Field(..., description="Campaign name.")
    campaign_type: CampaignType = Field(..., description="Campaign type.")
    bidding_strategy_type: BiddingStrategyType = Field(
        ..., description="Bidding strategy type."
    )
    budget_amount_micros: int = Field(
        ..., gt=0, description="Daily budget in micros (1 unit = 1,000,000 micros)."
    )
    start_date: str | None = Field(default=None, description="Start date YYYY-MM-DD.")
    end_date: str | None = Field(default=None, description="End date YYYY-MM-DD.")
    target_cpa_micros: int | None = Field(
        default=None, gt=0, description="Target CPA in micros (required for TARGET_CPA)."
    )
    target_roas: float | None = Field(
        default=None, gt=0, description="Target ROAS (required for TARGET_ROAS, e.g. 3.0 = 300%)."
    )

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            date_type.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be a valid calendar date in YYYY-MM-DD format")
        return v

    @model_validator(mode="after")
    def validate_bidding_targets(self) -> "CreateCampaignInput":
        if (
            self.bidding_strategy_type == BiddingStrategyType.TARGET_CPA
            and self.target_cpa_micros is None
        ):
            raise ValueError("target_cpa_micros is required when bidding_strategy_type=TARGET_CPA")
        if (
            self.bidding_strategy_type == BiddingStrategyType.TARGET_ROAS
            and self.target_roas is None
        ):
            raise ValueError("target_roas is required when bidding_strategy_type=TARGET_ROAS")
        if self.start_date and self.end_date:
            if date_type.fromisoformat(self.start_date) > date_type.fromisoformat(self.end_date):
                raise ValueError("start_date must not be after end_date")
        return self


class CreateAdGroupInput(CustomerIdMixin):
    """Input for gads_create_ad_group tool."""

    campaign_id: str = Field(..., description="Campaign ID to add the ad group to.")
    name: str = Field(..., description="Ad group name.")
    ad_group_type: AdGroupType = Field(..., description="Ad group type.")
    cpc_bid_micros: int | None = Field(
        default=None, gt=0, description="Default CPC bid in micros."
    )


class CreateResponsiveSearchAdInput(CustomerIdMixin):
    """Input for gads_create_responsive_search_ad tool."""

    ad_group_id: str = Field(..., description="Ad group ID.")
    headlines: list[str] = Field(
        ..., min_length=3, max_length=15,
        description="Headlines (min 3, max 15, each max 30 chars).",
    )
    descriptions: list[str] = Field(
        ..., min_length=2, max_length=4,
        description="Descriptions (min 2, max 4, each max 90 chars).",
    )
    final_urls: list[str] = Field(
        ..., min_length=1, description="Landing page URLs."
    )
    path1: str | None = Field(default=None, description="Display URL path 1 (max 15 chars).")
    path2: str | None = Field(default=None, description="Display URL path 2 (max 15 chars).")


class AddKeywordsInput(CustomerIdMixin):
    """Input for gads_add_keywords tool (positive keywords)."""

    ad_group_id: str = Field(..., description="Ad group ID.")
    keywords: list[str] = Field(
        ..., min_length=1, max_length=20,
        description="Keywords to add (max 20 per call).",
    )
    match_type: MatchType = Field(
        default=MatchType.BROAD, description="Match type: exact, phrase, or broad."
    )
    cpc_bid_micros: int | None = Field(
        default=None, gt=0, description="Keyword-level CPC bid in micros."
    )


class SetBiddingStrategyInput(CustomerIdMixin):
    """Input for gads_set_bidding_strategy tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    strategy_type: BiddingStrategyType = Field(..., description="Bidding strategy type.")
    target_cpa_micros: int | None = Field(
        default=None, gt=0, description="Target CPA in micros (required for TARGET_CPA)."
    )
    target_roas: float | None = Field(
        default=None, gt=0, description="Target ROAS (required for TARGET_ROAS)."
    )

    @model_validator(mode="after")
    def validate_strategy_targets(self) -> "SetBiddingStrategyInput":
        if (
            self.strategy_type == BiddingStrategyType.TARGET_CPA
            and self.target_cpa_micros is None
        ):
            raise ValueError("target_cpa_micros is required when strategy_type=TARGET_CPA")
        if (
            self.strategy_type == BiddingStrategyType.TARGET_ROAS
            and self.target_roas is None
        ):
            raise ValueError("target_roas is required when strategy_type=TARGET_ROAS")
        return self


class UpdateKeywordInput(CustomerIdMixin):
    """Input for gads_update_keyword tool."""

    ad_group_id: str = Field(..., description="Ad group ID.")
    criterion_id: str = Field(..., description="Keyword criterion ID.")
    cpc_bid_micros: int | None = Field(
        default=None, gt=0, description="New CPC bid in micros."
    )
    status: StatusAction | None = Field(
        default=None, description="New status: enable, pause, or remove."
    )

    @model_validator(mode="after")
    def validate_at_least_one_change(self) -> "UpdateKeywordInput":
        if self.cpc_bid_micros is None and self.status is None:
            raise ValueError("At least one of cpc_bid_micros or status must be provided")
        return self


class CreateAdExtensionInput(CustomerIdMixin):
    """Input for gads_create_ad_extension tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    extension_type: ExtensionType = Field(..., description="Extension type.")
    # Sitelink fields
    link_text: str | None = Field(default=None, description="Sitelink text.")
    final_urls: list[str] | None = Field(default=None, description="Sitelink URLs.")
    description1: str | None = Field(default=None, description="Sitelink description line 1.")
    description2: str | None = Field(default=None, description="Sitelink description line 2.")
    # Callout fields
    callout_text: str | None = Field(default=None, description="Callout text.")
    # Call fields
    phone_number: str | None = Field(default=None, description="Phone number.")
    country_code: str | None = Field(default=None, description="Country code (e.g. IT, US).")
    # Structured snippet fields
    snippet_header: str | None = Field(default=None, description="Snippet header.")
    snippet_values: list[str] | None = Field(default=None, description="Snippet values.")

    @model_validator(mode="after")
    def validate_extension_fields(self) -> "CreateAdExtensionInput":
        t = self.extension_type
        if t == ExtensionType.SITELINK:
            if not self.link_text:
                raise ValueError("link_text is required for SITELINK extensions")
            if not self.final_urls:
                raise ValueError("final_urls is required for SITELINK extensions")
        elif t == ExtensionType.CALLOUT:
            if not self.callout_text:
                raise ValueError("callout_text is required for CALLOUT extensions")
        elif t == ExtensionType.CALL:
            if not self.phone_number:
                raise ValueError("phone_number is required for CALL extensions")
            if not self.country_code:
                raise ValueError("country_code is required for CALL extensions")
        elif t == ExtensionType.STRUCTURED_SNIPPET:
            if not self.snippet_header:
                raise ValueError("snippet_header is required for STRUCTURED_SNIPPET extensions")
            if not self.snippet_values:
                raise ValueError("snippet_values is required for STRUCTURED_SNIPPET extensions")
        return self


class SetDeviceTargetingInput(CustomerIdMixin):
    """Input for gads_set_device_targeting tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    device: DeviceType = Field(..., description="Device type.")
    bid_modifier: float = Field(
        ..., ge=0, description="Bid modifier (0.0=exclude, 1.0=no change, 1.5=+50%)."
    )


class SetDemographicTargetingInput(CustomerIdMixin):
    """Input for gads_set_demographic_targeting tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    dimension: DemographicDimension = Field(..., description="Demographic dimension.")
    values: list[str] = Field(
        ..., min_length=1, description="Demographic values to target."
    )
    bid_modifier: float | None = Field(
        default=None, ge=0, description="Bid modifier."
    )


class CreateAudienceSegmentInput(CustomerIdMixin):
    """Input for gads_create_audience_segment tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    audience_type: AudienceType = Field(..., description="Audience type.")
    audience_id: str = Field(..., description="Audience segment ID.")
    bid_modifier: float | None = Field(
        default=None, ge=0, description="Bid modifier."
    )
