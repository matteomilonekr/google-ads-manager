"""Tests for audience tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.audiences import (
    _build_list_audiences_query,
    _build_list_user_interests_query,
    _parse_audience_row,
    _parse_user_interest_row,
    gads_list_audiences,
    gads_list_user_interests,
)


def _make_audience_row(
    resource_name="campaignAudienceViews/123~456",
    campaign_name="Test Campaign",
    criterion_id="789",
    impressions=1000,
    clicks=50,
    cost_micros=5000000,
    conversions=3.0,
):
    row = MagicMock()
    row.campaign_audience_view.resource_name = resource_name
    row.campaign.name = campaign_name
    row.campaign_criterion.criterion_id = criterion_id
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    return row


def _make_user_interest_row(
    interest_id="10001",
    name="Travel",
    taxonomy_type="AFFINITY",
    availabilities="[]",
):
    row = MagicMock()
    row.user_interest.user_interest_id = interest_id
    row.user_interest.name = name
    row.user_interest.taxonomy_type = taxonomy_type
    row.user_interest.availabilities = availabilities
    return row


class TestBuildListAudiencesQuery:
    def test_basic_query(self):
        query = _build_list_audiences_query(
            cid="1234567890",
            campaign_id=None,
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        assert "FROM campaign_audience_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query
        assert "ORDER BY metrics.impressions DESC" in query

    def test_with_campaign_filter(self):
        query = _build_list_audiences_query(
            cid="1234567890",
            campaign_id="999",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        assert "campaign.id = 999" in query

    def test_without_campaign_filter(self):
        query = _build_list_audiences_query(
            cid="1234567890",
            campaign_id=None,
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        assert "campaign.id" not in query


class TestParseAudienceRow:
    def test_basic_parsing(self):
        row = _make_audience_row()
        result = _parse_audience_row(row)
        assert result["criterion_id"] == "789"
        assert result["campaign"] == "Test Campaign"
        assert result["impressions"] == 1000
        assert result["clicks"] == 50
        assert result["cost"] == "5.00"
        assert result["conversions"] == 3.0


class TestGadsListAudiences:
    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_audience_row(criterion_id="100", campaign_name="Campaign A"),
            _make_audience_row(criterion_id="200", campaign_name="Campaign B"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_audiences(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Audience Segments" in result
        assert "Campaign A" in result
        assert "Campaign B" in result

    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_audience_row(criterion_id="100"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_audiences(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "audiences" in data
        assert "pagination" in data
        assert len(data["audiences"]) == 1
        assert data["audiences"][0]["criterion_id"] == "100"

    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_audiences(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result

    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_audience_row(criterion_id=str(i))
            for i in range(5)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_audiences(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            limit=2,
            offset=0,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["count"] == 2
        assert data["pagination"]["has_more"] is True

    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_default_dates(self, mock_get_client):
        """Verify that omitting dates uses defaults (no error)."""
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_audiences(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Audience Segments" in result


class TestBuildListUserInterestsQuery:
    def test_no_filter(self):
        query = _build_list_user_interests_query(taxonomy_type=None)
        assert "FROM user_interest" in query
        assert "WHERE" not in query
        assert "ORDER BY user_interest.name" in query

    def test_affinity_filter(self):
        query = _build_list_user_interests_query(taxonomy_type="AFFINITY")
        assert "user_interest.taxonomy_type = 'AFFINITY'" in query

    def test_in_market_filter(self):
        query = _build_list_user_interests_query(taxonomy_type="IN_MARKET")
        assert "user_interest.taxonomy_type = 'IN_MARKET'" in query

    def test_case_insensitive_filter(self):
        query = _build_list_user_interests_query(taxonomy_type="affinity")
        assert "user_interest.taxonomy_type = 'AFFINITY'" in query


class TestParseUserInterestRow:
    def test_basic_parsing(self):
        row = _make_user_interest_row()
        result = _parse_user_interest_row(row)
        assert result["id"] == "10001"
        assert result["name"] == "Travel"
        assert "AFFINITY" in result["taxonomy_type"]


class TestGadsListUserInterests:
    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_user_interest_row(interest_id="1", name="Travel"),
            _make_user_interest_row(interest_id="2", name="Sports"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_user_interests(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## User Interests" in result
        assert "Travel" in result
        assert "Sports" in result

    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_user_interest_row(interest_id="1", name="Travel"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_user_interests(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "user_interests" in data
        assert "pagination" in data
        assert len(data["user_interests"]) == 1

    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_with_taxonomy_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_user_interest_row(taxonomy_type="AFFINITY"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_user_interests(
            customer_id="1234567890",
            taxonomy_type="AFFINITY",
            ctx=MagicMock(),
        )
        assert "(AFFINITY)" in result

    @patch("google_ads_mcp.tools.audiences.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_user_interests(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result
