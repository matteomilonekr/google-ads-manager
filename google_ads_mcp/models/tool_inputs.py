"""Input models for Google Ads MCP tools."""

from __future__ import annotations

from datetime import date, timedelta

from pydantic import Field

from google_ads_mcp.models.common import (
    AdGroupStatusFilter,
    CampaignStatusFilter,
    CampaignTypeFilter,
    CustomerIdMixin,
    ResponseFormat,
)


def _default_start_date() -> str:
    return (date.today() - timedelta(days=30)).isoformat()


def _default_end_date() -> str:
    return date.today().isoformat()


class ListCampaignsInput(CustomerIdMixin):
    """Input for list_campaigns tool."""

    status: CampaignStatusFilter = CampaignStatusFilter.ALL
    campaign_type: CampaignTypeFilter = CampaignTypeFilter.ALL
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class GetCampaignPerformanceInput(CustomerIdMixin):
    """Input for get_campaign_performance tool."""

    campaign_id: str | None = Field(
        default=None,
        description="Specific campaign ID. If None, returns all campaigns.",
    )
    status: CampaignStatusFilter = CampaignStatusFilter.ENABLED
    start_date: str = Field(default_factory=_default_start_date)
    end_date: str = Field(default_factory=_default_end_date)
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class ListAdGroupsInput(CustomerIdMixin):
    """Input for list_ad_groups tool."""

    campaign_id: str | None = Field(
        default=None,
        description="Filter by campaign ID.",
    )
    status: AdGroupStatusFilter = AdGroupStatusFilter.ALL
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class GetAdGroupPerformanceInput(CustomerIdMixin):
    """Input for get_ad_group_performance tool."""

    campaign_id: str | None = Field(default=None)
    ad_group_id: str | None = Field(default=None)
    status: AdGroupStatusFilter = AdGroupStatusFilter.ENABLED
    start_date: str = Field(default_factory=_default_start_date)
    end_date: str = Field(default_factory=_default_end_date)
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class ListKeywordsInput(CustomerIdMixin):
    """Input for list_keywords tool."""

    campaign_id: str | None = Field(default=None)
    ad_group_id: str | None = Field(default=None)
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class GetKeywordPerformanceInput(CustomerIdMixin):
    """Input for get_keyword_performance tool."""

    campaign_id: str | None = Field(default=None)
    ad_group_id: str | None = Field(default=None)
    start_date: str = Field(default_factory=_default_start_date)
    end_date: str = Field(default_factory=_default_end_date)
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class GetAccountOverviewInput(CustomerIdMixin):
    """Input for get_account_overview tool."""

    start_date: str = Field(default_factory=_default_start_date)
    end_date: str = Field(default_factory=_default_end_date)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class SearchTermsReportInput(CustomerIdMixin):
    """Input for search_terms_report tool."""

    campaign_id: str | None = Field(default=None)
    ad_group_id: str | None = Field(default=None)
    start_date: str = Field(default_factory=_default_start_date)
    end_date: str = Field(default_factory=_default_end_date)
    limit: int = Field(default=100, ge=1, le=5000)
    offset: int = Field(default=0, ge=0)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN
