"""Input models for Google Ads MCP mutation tools."""

from __future__ import annotations

import re

from pydantic import Field, field_validator, model_validator

from google_ads_mcp.models.common import (
    CustomerIdMixin,
    MatchType,
    NegativeKeywordLevel,
    StatusAction,
)


class SetCampaignStatusInput(CustomerIdMixin):
    """Input for gads_set_campaign_status tool."""

    campaign_id: str = Field(..., description="Campaign ID to update.")
    status: StatusAction = Field(..., description="New status: enable, pause, or remove.")


class UpdateCampaignInput(CustomerIdMixin):
    """Input for gads_update_campaign tool."""

    campaign_id: str = Field(..., description="Campaign ID to update.")
    name: str | None = Field(default=None, description="New campaign name.")
    start_date: str | None = Field(default=None, description="New start date YYYY-MM-DD.")
    end_date: str | None = Field(default=None, description="New end date YYYY-MM-DD.")

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v

    @model_validator(mode='after')
    def validate_at_least_one_change(self) -> 'UpdateCampaignInput':
        if self.name is None and self.start_date is None and self.end_date is None:
            raise ValueError('At least one of name, start_date, or end_date must be provided')
        return self


class SetAdGroupStatusInput(CustomerIdMixin):
    """Input for gads_set_ad_group_status tool."""

    ad_group_id: str = Field(..., description="Ad group ID to update.")
    status: StatusAction = Field(..., description="New status: enable, pause, or remove.")


class SetAdStatusInput(CustomerIdMixin):
    """Input for gads_set_ad_status tool."""

    ad_group_id: str = Field(..., description="Ad group ID containing the ad.")
    ad_id: str = Field(..., description="Ad ID to update.")
    status: StatusAction = Field(..., description="New status: enable, pause, or remove.")


class UpdateBudgetInput(CustomerIdMixin):
    """Input for gads_update_budget tool."""

    budget_id: str = Field(..., description="Campaign budget ID.")
    amount_micros: int = Field(
        ..., gt=0, description="New daily budget in micros (1 unit = 1,000,000 micros)."
    )


class AddNegativeKeywordsInput(CustomerIdMixin):
    """Input for gads_add_negative_keywords tool."""

    level: NegativeKeywordLevel = Field(..., description="Level: campaign or ad_group.")
    campaign_id: str | None = Field(
        default=None, description="Campaign ID (required if level=campaign)."
    )
    ad_group_id: str | None = Field(
        default=None, description="Ad group ID (required if level=ad_group)."
    )
    keywords: list[str] = Field(
        ..., min_length=1, max_length=20,
        description="Keywords to add as negatives (max 20 per call).",
    )
    match_type: MatchType = Field(
        default=MatchType.EXACT, description="Match type: exact, phrase, or broad."
    )

    @model_validator(mode='after')
    def validate_level_id_pairing(self) -> 'AddNegativeKeywordsInput':
        if self.level == NegativeKeywordLevel.CAMPAIGN and not self.campaign_id:
            raise ValueError('campaign_id is required when level=campaign')
        if self.level == NegativeKeywordLevel.AD_GROUP and not self.ad_group_id:
            raise ValueError('ad_group_id is required when level=ad_group')
        return self


class SetLocationTargetingInput(CustomerIdMixin):
    """Input for gads_set_location_targeting tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    location_ids: list[int] = Field(
        ..., min_length=1,
        description="Geo target constant IDs (e.g. 2380 for Italy, 2826 for UK).",
    )
    exclude: bool = Field(default=False, description="If true, exclude these locations.")


class SetLanguageTargetingInput(CustomerIdMixin):
    """Input for gads_set_language_targeting tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    language_ids: list[int] = Field(
        ..., min_length=1,
        description="Language criterion IDs (e.g. 1000 for English, 1004 for Italian).",
    )
