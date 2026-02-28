"""Tests for ad group tools."""

import json
from unittest.mock import MagicMock, patch

from google_ads_mcp.models.tool_inputs import (
    GetAdGroupPerformanceInput,
    ListAdGroupsInput,
)
from google_ads_mcp.tools.ad_groups import (
    _build_ad_group_performance_query,
    _build_list_ad_groups_query,
    _parse_ad_group_row,
    list_ad_groups,
    get_ad_group_performance,
)


def _make_ad_group_row(
    ag_id="100", ag_name="Ad Group 1", ag_status="ENABLED",
    ag_type="SEARCH_STANDARD", camp_id="10", camp_name="Campaign 1",
):
    row = MagicMock()
    row.ad_group.id = ag_id
    row.ad_group.name = ag_name
    row.ad_group.status = ag_status
    row.ad_group.type_ = ag_type
    row.campaign.id = camp_id
    row.campaign.name = camp_name
    return row


def _make_ag_perf_row(
    ag_id="100", ag_name="AG1", camp_name="Camp1",
    impressions=500, clicks=25, cost_micros=2500000,
    conversions=3.0, ctr=0.05, avg_cpc=100000, conv_rate=0.12,
):
    row = MagicMock()
    row.ad_group.id = ag_id
    row.ad_group.name = ag_name
    row.ad_group.status = "ENABLED"
    row.campaign.name = camp_name
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    row.metrics.ctr = ctr
    row.metrics.average_cpc = avg_cpc
    row.metrics.conversions_from_interactions_rate = conv_rate
    return row


class TestBuildListAdGroupsQuery:
    def test_no_filters(self):
        params = ListAdGroupsInput(customer_id="1234567890")
        query = _build_list_ad_groups_query(params)
        assert "FROM ad_group" in query
        assert "WHERE" not in query

    def test_campaign_filter(self):
        params = ListAdGroupsInput(
            customer_id="1234567890", campaign_id="999"
        )
        query = _build_list_ad_groups_query(params)
        assert "campaign.id = 999" in query

    def test_status_filter(self):
        params = ListAdGroupsInput(
            customer_id="1234567890", status="paused"
        )
        query = _build_list_ad_groups_query(params)
        assert "ad_group.status = 'PAUSED'" in query


class TestParseAdGroupRow:
    def test_basic_parsing(self):
        row = _make_ad_group_row()
        result = _parse_ad_group_row(row)
        assert result["id"] == "100"
        assert result["name"] == "Ad Group 1"
        assert result["campaign_name"] == "Campaign 1"


class TestListAdGroups:
    @patch("google_ads_mcp.tools.ad_groups.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_ad_group_row()]
        mock_get_client.return_value = mock_client

        result = list_ad_groups(
            customer_id="1234567890", ctx=MagicMock()
        )
        assert "## Ad Groups" in result
        assert "Ad Group 1" in result

    @patch("google_ads_mcp.tools.ad_groups.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_ad_group_row()]
        mock_get_client.return_value = mock_client

        result = list_ad_groups(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "ad_groups" in data
        assert len(data["ad_groups"]) == 1

    @patch("google_ads_mcp.tools.ad_groups.get_client")
    def test_with_campaign_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = list_ad_groups(
            customer_id="1234567890",
            campaign_id="555",
            ctx=MagicMock(),
        )
        # Verify the query was built with the campaign filter
        call_args = mock_client.query.call_args
        assert "campaign.id = 555" in call_args[0][1]


class TestBuildAdGroupPerformanceQuery:
    def test_date_range(self):
        params = GetAdGroupPerformanceInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_ad_group_performance_query(params)
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_all_filters(self):
        params = GetAdGroupPerformanceInput(
            customer_id="1234567890",
            campaign_id="10",
            ad_group_id="100",
            status="enabled",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_ad_group_performance_query(params)
        assert "campaign.id = 10" in query
        assert "ad_group.id = 100" in query
        assert "ad_group.status = 'ENABLED'" in query


class TestGetAdGroupPerformance:
    @patch("google_ads_mcp.tools.ad_groups.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_ag_perf_row()]
        mock_get_client.return_value = mock_client

        result = get_ad_group_performance(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Ad Group Performance" in result

    @patch("google_ads_mcp.tools.ad_groups.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_ag_perf_row()]
        mock_get_client.return_value = mock_client

        result = get_ad_group_performance(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["performance"][0]["clicks"] == 25
