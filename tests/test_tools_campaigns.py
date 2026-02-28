"""Tests for campaign tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.models.tool_inputs import (
    GetCampaignPerformanceInput,
    ListCampaignsInput,
)
from google_ads_mcp.tools.campaigns import (
    _build_campaign_performance_query,
    _build_list_campaigns_query,
    _parse_campaign_row,
    _parse_campaign_performance_row,
    list_campaigns,
    get_campaign_performance,
)


def _make_campaign_row(
    cid="123", name="Test Campaign", status="ENABLED",
    channel_type="SEARCH", bidding="TARGET_CPA", budget="budgets/456",
):
    row = MagicMock()
    row.campaign.id = cid
    row.campaign.name = name
    row.campaign.status = status
    row.campaign.advertising_channel_type = channel_type
    row.campaign.bidding_strategy_type = bidding
    row.campaign.campaign_budget = budget
    return row


def _make_perf_row(
    cid="123", name="Test", status="ENABLED",
    impressions=1000, clicks=50, cost_micros=5000000,
    conversions=5.0, ctr=0.05, avg_cpc=100000,
    conv_rate=0.10,
):
    row = MagicMock()
    row.campaign.id = cid
    row.campaign.name = name
    row.campaign.status = status
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    row.metrics.ctr = ctr
    row.metrics.average_cpc = avg_cpc
    row.metrics.conversions_from_interactions_rate = conv_rate
    return row


class TestBuildListCampaignsQuery:
    def test_no_filters(self):
        params = ListCampaignsInput(customer_id="1234567890")
        query = _build_list_campaigns_query(params)
        assert "FROM campaign" in query
        assert "WHERE" not in query
        assert "ORDER BY campaign.name" in query

    def test_status_filter(self):
        params = ListCampaignsInput(customer_id="1234567890", status="enabled")
        query = _build_list_campaigns_query(params)
        assert "campaign.status = 'ENABLED'" in query

    def test_type_filter(self):
        params = ListCampaignsInput(
            customer_id="1234567890", campaign_type="search"
        )
        query = _build_list_campaigns_query(params)
        assert "campaign.advertising_channel_type = 'SEARCH'" in query

    def test_combined_filters(self):
        params = ListCampaignsInput(
            customer_id="1234567890",
            status="paused",
            campaign_type="display",
        )
        query = _build_list_campaigns_query(params)
        assert "campaign.status = 'PAUSED'" in query
        assert "campaign.advertising_channel_type = 'DISPLAY'" in query
        assert " AND " in query


class TestParseCampaignRow:
    def test_basic_parsing(self):
        row = _make_campaign_row()
        result = _parse_campaign_row(row)
        assert result["id"] == "123"
        assert result["name"] == "Test Campaign"
        assert result["budget"] == "budgets/456"


class TestListCampaigns:
    @patch("google_ads_mcp.tools.campaigns.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_campaign_row(cid="1", name="Campaign A"),
            _make_campaign_row(cid="2", name="Campaign B", status="PAUSED"),
        ]
        mock_get_client.return_value = mock_client

        result = list_campaigns(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Campaigns" in result
        assert "Campaign A" in result
        assert "Campaign B" in result

    @patch("google_ads_mcp.tools.campaigns.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_campaign_row(cid="1", name="Test"),
        ]
        mock_get_client.return_value = mock_client

        result = list_campaigns(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "campaigns" in data
        assert "pagination" in data
        assert len(data["campaigns"]) == 1

    @patch("google_ads_mcp.tools.campaigns.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = list_campaigns(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result

    @patch("google_ads_mcp.tools.campaigns.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_campaign_row(cid=str(i), name=f"Campaign {i}")
            for i in range(5)
        ]
        mock_get_client.return_value = mock_client

        result = list_campaigns(
            customer_id="1234567890",
            limit=2,
            offset=0,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["count"] == 2
        assert data["pagination"]["has_more"] is True


class TestBuildCampaignPerformanceQuery:
    def test_date_range(self):
        params = GetCampaignPerformanceInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_campaign_performance_query(params)
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_specific_campaign(self):
        params = GetCampaignPerformanceInput(
            customer_id="1234567890",
            campaign_id="999",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_campaign_performance_query(params)
        assert "campaign.id = 999" in query

    def test_status_filter(self):
        params = GetCampaignPerformanceInput(
            customer_id="1234567890",
            status="paused",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_campaign_performance_query(params)
        assert "campaign.status = 'PAUSED'" in query


class TestGetCampaignPerformance:
    @patch("google_ads_mcp.tools.campaigns.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_perf_row()]
        mock_get_client.return_value = mock_client

        result = get_campaign_performance(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Campaign Performance" in result
        assert "2026-01-01" in result

    @patch("google_ads_mcp.tools.campaigns.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_perf_row()]
        mock_get_client.return_value = mock_client

        result = get_campaign_performance(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "performance" in data
        assert data["performance"][0]["impressions"] == 1000
