"""Tests for account overview tool."""

import json
from unittest.mock import MagicMock, patch

from google_ads_mcp.models.tool_inputs import GetAccountOverviewInput
from google_ads_mcp.tools.account import (
    _build_account_performance_query,
    _build_campaign_count_query,
    get_account_overview,
)


def _make_account_perf_row(
    impressions=10000, clicks=500, cost_micros=50000000,
    conversions=50.0, ctr=0.05, avg_cpc=100000,
    conv_rate=0.10, all_conv=55.0, interaction_rate=0.04,
):
    row = MagicMock()
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    row.metrics.ctr = ctr
    row.metrics.average_cpc = avg_cpc
    row.metrics.conversions_from_interactions_rate = conv_rate
    row.metrics.all_conversions = all_conv
    row.metrics.interaction_rate = interaction_rate
    return row


def _make_campaign_status_row(status="ENABLED"):
    row = MagicMock()
    row.campaign.status = status
    row.metrics.impressions = 100
    return row


class TestBuildAccountPerformanceQuery:
    def test_date_range(self):
        params = GetAccountOverviewInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_account_performance_query(params)
        assert "FROM customer" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_select_fields(self):
        params = GetAccountOverviewInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_account_performance_query(params)
        assert "metrics.impressions" in query
        assert "metrics.cost_micros" in query
        assert "metrics.conversions" in query


class TestBuildCampaignCountQuery:
    def test_query_structure(self):
        query = _build_campaign_count_query()
        assert "FROM campaign" in query
        assert "REMOVED" in query


class TestGetAccountOverview:
    @patch("google_ads_mcp.tools.account.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        # First call: account performance
        # Second call: campaign counts
        mock_client.query.side_effect = [
            [
                _make_account_perf_row(impressions=5000, clicks=250, cost_micros=25000000, conversions=25.0),
                _make_account_perf_row(impressions=5000, clicks=250, cost_micros=25000000, conversions=25.0),
            ],
            [
                _make_campaign_status_row("ENABLED"),
                _make_campaign_status_row("ENABLED"),
                _make_campaign_status_row("PAUSED"),
            ],
        ]
        mock_get_client.return_value = mock_client

        result = get_account_overview(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "Account Overview" in result

    @patch("google_ads_mcp.tools.account.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.side_effect = [
            [_make_account_perf_row()],
            [
                _make_campaign_status_row("ENABLED"),
                _make_campaign_status_row("PAUSED"),
            ],
        ]
        mock_get_client.return_value = mock_client

        result = get_account_overview(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "period" in data
        assert "campaigns" in data
        assert "metrics" in data
        assert data["campaigns"]["active"] == 1
        assert data["campaigns"]["paused"] == 1

    @patch("google_ads_mcp.tools.account.get_client")
    def test_aggregation(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.side_effect = [
            [
                _make_account_perf_row(impressions=3000, clicks=150, cost_micros=15000000, conversions=15.0),
                _make_account_perf_row(impressions=7000, clicks=350, cost_micros=35000000, conversions=35.0),
            ],
            [],
        ]
        mock_get_client.return_value = mock_client

        result = get_account_overview(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        # 3000 + 7000 = 10000
        assert data["metrics"]["impressions"] == "10,000"
        # 150 + 350 = 500
        assert data["metrics"]["clicks"] == "500"
        # (15M + 35M) / 1M = 50.00
        assert data["metrics"]["cost"] == "50.00"
        # 15 + 35 = 50.0
        assert data["metrics"]["conversions"] == 50.0

    @patch("google_ads_mcp.tools.account.get_client")
    def test_zero_impressions(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.side_effect = [[], []]
        mock_get_client.return_value = mock_client

        result = get_account_overview(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["metrics"]["ctr"] == "0.00%"
        assert data["metrics"]["conversion_rate"] == "0.00%"
