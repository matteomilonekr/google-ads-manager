"""Tests for keyword tools."""

import json
from unittest.mock import MagicMock, patch

from google_ads_mcp.models.tool_inputs import (
    GetKeywordPerformanceInput,
    ListKeywordsInput,
)
from google_ads_mcp.tools.keywords import (
    _build_keyword_performance_query,
    _build_list_keywords_query,
    _parse_keyword_row,
    list_keywords,
    get_keyword_performance,
)


def _make_keyword_row(
    criterion_id="200", text="buy shoes", match_type="EXACT",
    status="ENABLED", ag_name="Ad Group 1", camp_name="Campaign 1",
):
    row = MagicMock()
    row.ad_group_criterion.criterion_id = criterion_id
    row.ad_group_criterion.keyword.text = text
    row.ad_group_criterion.keyword.match_type = match_type
    row.ad_group_criterion.status = status
    row.ad_group.id = "10"
    row.ad_group.name = ag_name
    row.campaign.id = "1"
    row.campaign.name = camp_name
    return row


def _make_kw_perf_row(
    text="buy shoes", match_type="EXACT", ag_name="AG1",
    impressions=200, clicks=20, cost_micros=1000000,
    conversions=2.0, ctr=0.10, avg_cpc=50000, conv_rate=0.10,
):
    row = MagicMock()
    row.ad_group_criterion.keyword.text = text
    row.ad_group_criterion.keyword.match_type = match_type
    row.ad_group.name = ag_name
    row.campaign.name = "Campaign 1"
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    row.metrics.ctr = ctr
    row.metrics.average_cpc = avg_cpc
    row.metrics.conversions_from_interactions_rate = conv_rate
    return row


class TestBuildListKeywordsQuery:
    def test_no_filters(self):
        params = ListKeywordsInput(customer_id="1234567890")
        query = _build_list_keywords_query(params)
        assert "FROM keyword_view" in query
        assert "WHERE" not in query

    def test_campaign_filter(self):
        params = ListKeywordsInput(
            customer_id="1234567890", campaign_id="10"
        )
        query = _build_list_keywords_query(params)
        assert "campaign.id = 10" in query

    def test_ad_group_filter(self):
        params = ListKeywordsInput(
            customer_id="1234567890", ad_group_id="100"
        )
        query = _build_list_keywords_query(params)
        assert "ad_group.id = 100" in query


class TestParseKeywordRow:
    def test_basic_parsing(self):
        row = _make_keyword_row()
        result = _parse_keyword_row(row)
        assert result["keyword"] == "buy shoes"
        assert result["id"] == "200"
        assert result["campaign"] == "Campaign 1"


class TestListKeywords:
    @patch("google_ads_mcp.tools.keywords.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_keyword_row(),
            _make_keyword_row(text="running shoes", match_type="BROAD"),
        ]
        mock_get_client.return_value = mock_client

        result = list_keywords(
            customer_id="1234567890", ctx=MagicMock()
        )
        assert "## Keywords" in result
        assert "buy shoes" in result

    @patch("google_ads_mcp.tools.keywords.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_keyword_row()]
        mock_get_client.return_value = mock_client

        result = list_keywords(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "keywords" in data
        assert data["keywords"][0]["keyword"] == "buy shoes"


class TestBuildKeywordPerformanceQuery:
    def test_date_range(self):
        params = GetKeywordPerformanceInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_keyword_performance_query(params)
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query
        assert "FROM keyword_view" in query

    def test_with_filters(self):
        params = GetKeywordPerformanceInput(
            customer_id="1234567890",
            campaign_id="10",
            ad_group_id="100",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_keyword_performance_query(params)
        assert "campaign.id = 10" in query
        assert "ad_group.id = 100" in query


class TestGetKeywordPerformance:
    @patch("google_ads_mcp.tools.keywords.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_kw_perf_row()]
        mock_get_client.return_value = mock_client

        result = get_keyword_performance(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Keyword Performance" in result

    @patch("google_ads_mcp.tools.keywords.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_kw_perf_row()]
        mock_get_client.return_value = mock_client

        result = get_keyword_performance(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["performance"][0]["clicks"] == 20
        assert data["performance"][0]["keyword"] == "buy shoes"
