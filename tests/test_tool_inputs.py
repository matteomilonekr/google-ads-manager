"""Tests for tool input models."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from google_ads_mcp.models.tool_inputs import (
    GetAccountOverviewInput,
    GetAdGroupPerformanceInput,
    GetCampaignPerformanceInput,
    GetKeywordPerformanceInput,
    ListAdGroupsInput,
    ListCampaignsInput,
    ListKeywordsInput,
    SearchTermsReportInput,
)


class TestListCampaignsInput:
    def test_defaults(self):
        inp = ListCampaignsInput(customer_id="1234567890")
        assert inp.status.value == "all"
        assert inp.campaign_type.value == "all"
        assert inp.limit == 50
        assert inp.offset == 0
        assert inp.response_format.value == "markdown"

    def test_customer_id_sanitized(self):
        inp = ListCampaignsInput(customer_id="123-456-7890")
        assert inp.customer_id == "1234567890"

    def test_invalid_customer_id(self):
        with pytest.raises(ValidationError):
            ListCampaignsInput(customer_id="abc")

    def test_limit_bounds(self):
        with pytest.raises(ValidationError):
            ListCampaignsInput(customer_id="1234567890", limit=0)
        with pytest.raises(ValidationError):
            ListCampaignsInput(customer_id="1234567890", limit=1001)

    def test_custom_filters(self):
        inp = ListCampaignsInput(
            customer_id="1234567890",
            status="enabled",
            campaign_type="search",
            limit=10,
            offset=5,
            response_format="json",
        )
        assert inp.status.value == "enabled"
        assert inp.campaign_type.value == "search"
        assert inp.limit == 10
        assert inp.offset == 5
        assert inp.response_format.value == "json"


class TestGetCampaignPerformanceInput:
    def test_default_dates(self):
        inp = GetCampaignPerformanceInput(customer_id="1234567890")
        expected_start = (date.today() - timedelta(days=30)).isoformat()
        expected_end = date.today().isoformat()
        assert inp.start_date == expected_start
        assert inp.end_date == expected_end

    def test_custom_dates(self):
        inp = GetCampaignPerformanceInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        assert inp.start_date == "2026-01-01"
        assert inp.end_date == "2026-01-31"

    def test_optional_campaign_id(self):
        inp = GetCampaignPerformanceInput(customer_id="1234567890")
        assert inp.campaign_id is None

        inp2 = GetCampaignPerformanceInput(
            customer_id="1234567890", campaign_id="12345"
        )
        assert inp2.campaign_id == "12345"


class TestListAdGroupsInput:
    def test_defaults(self):
        inp = ListAdGroupsInput(customer_id="1234567890")
        assert inp.campaign_id is None
        assert inp.status.value == "all"

    def test_with_campaign_filter(self):
        inp = ListAdGroupsInput(
            customer_id="1234567890", campaign_id="999"
        )
        assert inp.campaign_id == "999"


class TestGetAdGroupPerformanceInput:
    def test_defaults(self):
        inp = GetAdGroupPerformanceInput(customer_id="1234567890")
        assert inp.campaign_id is None
        assert inp.ad_group_id is None
        assert inp.status.value == "enabled"


class TestListKeywordsInput:
    def test_defaults(self):
        inp = ListKeywordsInput(customer_id="1234567890")
        assert inp.campaign_id is None
        assert inp.ad_group_id is None
        assert inp.limit == 50


class TestGetKeywordPerformanceInput:
    def test_defaults(self):
        inp = GetKeywordPerformanceInput(customer_id="1234567890")
        assert inp.start_date == (date.today() - timedelta(days=30)).isoformat()


class TestGetAccountOverviewInput:
    def test_defaults(self):
        inp = GetAccountOverviewInput(customer_id="1234567890")
        assert inp.response_format.value == "markdown"
        assert inp.start_date is not None
        assert inp.end_date is not None


class TestSearchTermsReportInput:
    def test_defaults(self):
        inp = SearchTermsReportInput(customer_id="1234567890")
        assert inp.limit == 100
        assert inp.campaign_id is None

    def test_limit_bounds(self):
        inp = SearchTermsReportInput(customer_id="1234567890", limit=5000)
        assert inp.limit == 5000
        with pytest.raises(ValidationError):
            SearchTermsReportInput(customer_id="1234567890", limit=5001)
