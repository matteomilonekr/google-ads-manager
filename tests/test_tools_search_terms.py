"""Tests for search terms report tool."""

import json
from unittest.mock import MagicMock, patch

from google_ads_mcp.models.tool_inputs import SearchTermsReportInput
from google_ads_mcp.tools.search_terms import (
    _build_search_terms_query,
    _parse_search_term_row,
    search_terms_report,
)


def _make_search_term_row(
    term="buy red shoes", status="ADDED",
    camp_name="Campaign 1", ag_name="Ad Group 1",
    impressions=100, clicks=10, cost_micros=500000,
    conversions=1.0, ctr=0.10, avg_cpc=50000,
):
    row = MagicMock()
    row.search_term_view.search_term = term
    row.search_term_view.status = status
    row.campaign.name = camp_name
    row.ad_group.name = ag_name
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    row.metrics.ctr = ctr
    row.metrics.average_cpc = avg_cpc
    return row


class TestBuildSearchTermsQuery:
    def test_date_range(self):
        params = SearchTermsReportInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_search_terms_query(params)
        assert "FROM search_term_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_campaign_filter(self):
        params = SearchTermsReportInput(
            customer_id="1234567890",
            campaign_id="10",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_search_terms_query(params)
        assert "campaign.id = 10" in query

    def test_ad_group_filter(self):
        params = SearchTermsReportInput(
            customer_id="1234567890",
            ad_group_id="100",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_search_terms_query(params)
        assert "ad_group.id = 100" in query

    def test_order_by(self):
        params = SearchTermsReportInput(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        query = _build_search_terms_query(params)
        assert "ORDER BY metrics.impressions DESC" in query


class TestParseSearchTermRow:
    def test_basic_parsing(self):
        row = _make_search_term_row()
        result = _parse_search_term_row(row)
        assert result["search_term"] == "buy red shoes"
        assert result["campaign"] == "Campaign 1"
        assert result["impressions"] == 100
        assert result["clicks"] == 10


class TestSearchTermsReport:
    @patch("google_ads_mcp.tools.search_terms.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_search_term_row(term="buy shoes"),
            _make_search_term_row(term="red shoes sale"),
        ]
        mock_get_client.return_value = mock_client

        result = search_terms_report(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Search Terms Report" in result
        assert "buy shoes" in result
        assert "red shoes sale" in result

    @patch("google_ads_mcp.tools.search_terms.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_search_term_row()]
        mock_get_client.return_value = mock_client

        result = search_terms_report(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "search_terms" in data
        assert "pagination" in data
        assert data["search_terms"][0]["search_term"] == "buy red shoes"

    @patch("google_ads_mcp.tools.search_terms.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_search_term_row(term=f"term {i}")
            for i in range(10)
        ]
        mock_get_client.return_value = mock_client

        result = search_terms_report(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            limit=3,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 10
        assert data["pagination"]["count"] == 3
        assert data["pagination"]["has_more"] is True

    @patch("google_ads_mcp.tools.search_terms.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = search_terms_report(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result
