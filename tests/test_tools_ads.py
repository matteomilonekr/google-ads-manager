"""Tests for ad group ad tools."""

import json
from unittest.mock import MagicMock, patch

from google_ads_mcp.tools.ads import (
    _build_list_ads_query,
    _parse_ad_row,
    gads_list_ad_group_ads,
)


def _make_ad_row(
    ad_id="200", ad_name="Test Ad", ad_type="RESPONSIVE_SEARCH_AD",
    status="ENABLED", approval_status="APPROVED", review_status="REVIEWED",
    ag_id="100", ag_name="Ad Group 1", camp_name="Campaign 1",
    impressions=1000, clicks=50, cost_micros=5000000,
    conversions=5.0, ctr=0.05,
):
    row = MagicMock()
    row.ad_group_ad.ad.id = ad_id
    row.ad_group_ad.ad.name = ad_name
    row.ad_group_ad.ad.type_ = ad_type
    row.ad_group_ad.status = status
    row.ad_group_ad.policy_summary.approval_status = approval_status
    row.ad_group_ad.policy_summary.review_status = review_status
    row.ad_group.id = ag_id
    row.ad_group.name = ag_name
    row.campaign.name = camp_name
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    row.metrics.ctr = ctr
    return row


class TestBuildListAdsQuery:
    def test_default_query(self):
        query = _build_list_ads_query(
            "1234567890", "2026-01-01", "2026-01-31"
        )
        assert "FROM ad_group_ad" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query
        assert "ad_group_ad.ad.id" in query
        assert "metrics.impressions" in query

    def test_campaign_filter(self):
        query = _build_list_ads_query(
            "1234567890", "2026-01-01", "2026-01-31",
            campaign_id="999",
        )
        assert "campaign.id = 999" in query

    def test_ad_group_filter(self):
        query = _build_list_ads_query(
            "1234567890", "2026-01-01", "2026-01-31",
            ad_group_id="100",
        )
        assert "ad_group.id = 100" in query

    def test_status_filter(self):
        query = _build_list_ads_query(
            "1234567890", "2026-01-01", "2026-01-31",
            status="paused",
        )
        assert "ad_group_ad.status = 'PAUSED'" in query

    def test_all_filters(self):
        query = _build_list_ads_query(
            "1234567890", "2026-01-01", "2026-01-31",
            campaign_id="10", ad_group_id="100", status="enabled",
        )
        assert "campaign.id = 10" in query
        assert "ad_group.id = 100" in query
        assert "ad_group_ad.status = 'ENABLED'" in query

    def test_status_all_no_filter(self):
        query = _build_list_ads_query(
            "1234567890", "2026-01-01", "2026-01-31",
            status="all",
        )
        assert "ad_group_ad.status = " not in query


class TestParseAdRow:
    def test_basic_parsing(self):
        row = _make_ad_row()
        result = _parse_ad_row(row)
        assert result["ad_id"] == "200"
        assert result["ad_name"] == "Test Ad"
        assert result["ad_group_name"] == "Ad Group 1"
        assert result["campaign_name"] == "Campaign 1"
        assert result["impressions"] == 1000
        assert result["clicks"] == 50
        assert result["conversions"] == 5.0
        assert result["ctr"] == "5.00%"

    def test_approval_fields(self):
        row = _make_ad_row(approval_status="APPROVED", review_status="REVIEWED")
        result = _parse_ad_row(row)
        assert result["approval_status"] == "APPROVED"
        assert result["review_status"] == "REVIEWED"


class TestGadsListAdGroupAds:
    @patch("google_ads_mcp.tools.ads.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_ad_row()]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_ads(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Ad Group Ads" in result
        assert "Test Ad" in result

    @patch("google_ads_mcp.tools.ads.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_ad_row()]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_ads(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "ad_group_ads" in data
        assert len(data["ad_group_ads"]) == 1
        assert data["ad_group_ads"][0]["ad_id"] == "200"
        assert data["ad_group_ads"][0]["clicks"] == 50

    @patch("google_ads_mcp.tools.ads.get_client")
    def test_with_campaign_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        gads_list_ad_group_ads(
            customer_id="1234567890",
            campaign_id="555",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        call_args = mock_client.query.call_args
        assert "campaign.id = 555" in call_args[0][1]

    @patch("google_ads_mcp.tools.ads.get_client")
    def test_with_ad_group_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        gads_list_ad_group_ads(
            customer_id="1234567890",
            ad_group_id="100",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        call_args = mock_client.query.call_args
        assert "ad_group.id = 100" in call_args[0][1]

    @patch("google_ads_mcp.tools.ads.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_ads(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0/0" in result or "Showing 0" in result
