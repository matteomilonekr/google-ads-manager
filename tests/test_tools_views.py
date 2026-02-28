"""Tests for performance view tools (Phase 3)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.views import (
    _build_geographic_view_query,
    _build_shopping_performance_query,
    _build_display_keyword_view_query,
    _build_topic_view_query,
    _build_user_location_view_query,
    _build_click_view_query,
    _parse_geographic_row,
    _parse_shopping_performance_row,
    _parse_display_keyword_row,
    _parse_topic_row,
    _parse_user_location_row,
    _parse_click_row,
    gads_geographic_view,
    gads_shopping_performance_view,
    gads_display_keyword_view,
    gads_topic_view,
    gads_user_location_view,
    gads_click_view,
)


# ---------------------------------------------------------------------------
# Row factories
# ---------------------------------------------------------------------------

def _make_geographic_row(
    country_id="2380",
    location_type="AREA_OF_INTEREST",
    campaign_name="Campaign 1",
    impressions=500,
    clicks=25,
    cost_micros=2500000,
    conversions=3.0,
):
    row = MagicMock()
    row.geographic_view.country_criterion_id = country_id
    row.geographic_view.location_type = location_type
    row.campaign.name = campaign_name
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    return row


def _make_shopping_row(
    item_id="SKU-123",
    title="Red Widget",
    brand="Acme",
    category_l1="Home & Garden",
    impressions=1000,
    clicks=40,
    cost_micros=4000000,
    conversions=5.0,
):
    row = MagicMock()
    row.segments.product_item_id = item_id
    row.segments.product_title = title
    row.segments.product_brand = brand
    row.segments.product_category_level1 = category_l1
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    return row


def _make_display_keyword_row(
    resource_name="customers/123/displayKeywordViews/456~789",
    display_name="shoes",
    keyword_text="running shoes",
    impressions=800,
    clicks=30,
    cost_micros=3000000,
    conversions=2.0,
):
    row = MagicMock()
    row.display_keyword_view.resource_name = resource_name
    row.ad_group_criterion.display_name = display_name
    row.ad_group_criterion.keyword.text = keyword_text
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    return row


def _make_topic_row(
    resource_name="customers/123/topicViews/456~789",
    topic_path=None,
    impressions=600,
    clicks=20,
    cost_micros=2000000,
    conversions=1.5,
):
    if topic_path is None:
        topic_path = ["Arts & Entertainment", "Movies"]
    row = MagicMock()
    row.topic_view.resource_name = resource_name
    row.ad_group_criterion.topic.path = topic_path
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    return row


def _make_user_location_row(
    country_id="2380",
    targeting_location="true",
    impressions=700,
    clicks=35,
    cost_micros=3500000,
    conversions=4.0,
):
    row = MagicMock()
    row.user_location_view.country_criterion_id = country_id
    row.user_location_view.targeting_location = targeting_location
    row.metrics.impressions = impressions
    row.metrics.clicks = clicks
    row.metrics.cost_micros = cost_micros
    row.metrics.conversions = conversions
    return row


def _make_click_row(
    gclid="CjwKCAtest123",
    city="Milan",
    country="Italy",
    campaign_location_target="locations/2380",
    ad_network_type="SEARCH",
    device="MOBILE",
    clicks=1,
):
    row = MagicMock()
    row.click_view.gclid = gclid
    row.click_view.area_of_interest.city = city
    row.click_view.area_of_interest.country = country
    row.click_view.campaign_location_target = campaign_location_target
    row.segments.ad_network_type = ad_network_type
    row.segments.device = device
    row.metrics.clicks = clicks
    return row


# ---------------------------------------------------------------------------
# Geographic View
# ---------------------------------------------------------------------------

class TestBuildGeographicViewQuery:
    def test_date_range(self):
        query = _build_geographic_view_query("1234567890", "2026-01-01", "2026-01-31")
        assert "FROM geographic_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_campaign_filter(self):
        query = _build_geographic_view_query("1234567890", "2026-01-01", "2026-01-31", campaign_id="99")
        assert "campaign.id = 99" in query

    def test_no_campaign_filter(self):
        query = _build_geographic_view_query("1234567890", "2026-01-01", "2026-01-31")
        assert "campaign.id" not in query

    def test_order_by(self):
        query = _build_geographic_view_query("1234567890", "2026-01-01", "2026-01-31")
        assert "ORDER BY metrics.impressions DESC" in query


class TestParseGeographicRow:
    def test_basic_parsing(self):
        row = _make_geographic_row()
        result = _parse_geographic_row(row)
        assert result["country_criterion_id"] == "2380"
        assert result["campaign"] == "Campaign 1"
        assert result["impressions"] == 500
        assert result["clicks"] == 25


class TestGadsGeographicView:
    @patch("google_ads_mcp.tools.views.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_geographic_row(country_id="2380", campaign_name="IT Campaign"),
            _make_geographic_row(country_id="2840", campaign_name="US Campaign"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_geographic_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Geographic View" in result
        assert "IT Campaign" in result
        assert "US Campaign" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_geographic_row()]
        mock_get_client.return_value = mock_client

        result = gads_geographic_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "geographic_data" in data
        assert "pagination" in data
        assert data["geographic_data"][0]["country_criterion_id"] == "2380"

    @patch("google_ads_mcp.tools.views.get_client")
    def test_campaign_id_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_geographic_row()]
        mock_get_client.return_value = mock_client

        gads_geographic_view(
            customer_id="1234567890",
            campaign_id="42",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "campaign.id = 42" in called_query

    @patch("google_ads_mcp.tools.views.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_geographic_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_date_defaults(self, mock_get_client):
        """Verify default dates are applied when not provided."""
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_geographic_view(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        # Should not raise and should contain a date range header
        assert "Geographic View" in result


# ---------------------------------------------------------------------------
# Shopping Performance View
# ---------------------------------------------------------------------------

class TestBuildShoppingPerformanceQuery:
    def test_date_range(self):
        query = _build_shopping_performance_query("1234567890", "2026-01-01", "2026-01-31")
        assert "FROM shopping_performance_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_campaign_filter(self):
        query = _build_shopping_performance_query("1234567890", "2026-01-01", "2026-01-31", campaign_id="55")
        assert "campaign.id = 55" in query


class TestParseShoppingPerformanceRow:
    def test_basic_parsing(self):
        row = _make_shopping_row()
        result = _parse_shopping_performance_row(row)
        assert result["product_item_id"] == "SKU-123"
        assert result["product_title"] == "Red Widget"
        assert result["product_brand"] == "Acme"
        assert result["impressions"] == 1000
        assert result["clicks"] == 40


class TestGadsShoppingPerformanceView:
    @patch("google_ads_mcp.tools.views.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_shopping_row(item_id="SKU-A", title="Widget A"),
            _make_shopping_row(item_id="SKU-B", title="Widget B"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_shopping_performance_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Shopping Performance" in result
        assert "Widget A" in result
        assert "Widget B" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_shopping_row()]
        mock_get_client.return_value = mock_client

        result = gads_shopping_performance_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "shopping_performance" in data
        assert data["shopping_performance"][0]["product_item_id"] == "SKU-123"

    @patch("google_ads_mcp.tools.views.get_client")
    def test_campaign_id_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_shopping_row()]
        mock_get_client.return_value = mock_client

        gads_shopping_performance_view(
            customer_id="1234567890",
            campaign_id="77",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "campaign.id = 77" in called_query

    @patch("google_ads_mcp.tools.views.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_shopping_performance_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result


# ---------------------------------------------------------------------------
# Display Keyword View
# ---------------------------------------------------------------------------

class TestBuildDisplayKeywordViewQuery:
    def test_date_range(self):
        query = _build_display_keyword_view_query("1234567890", "2026-01-01", "2026-01-31")
        assert "FROM display_keyword_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_campaign_filter(self):
        query = _build_display_keyword_view_query("1234567890", "2026-01-01", "2026-01-31", campaign_id="33")
        assert "campaign.id = 33" in query


class TestParseDisplayKeywordRow:
    def test_basic_parsing(self):
        row = _make_display_keyword_row()
        result = _parse_display_keyword_row(row)
        assert result["display_name"] == "shoes"
        assert result["keyword_text"] == "running shoes"
        assert result["impressions"] == 800


class TestGadsDisplayKeywordView:
    @patch("google_ads_mcp.tools.views.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_display_keyword_row(display_name="shoes"),
            _make_display_keyword_row(display_name="clothing"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_display_keyword_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Display Keyword View" in result
        assert "shoes" in result
        assert "clothing" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_display_keyword_row()]
        mock_get_client.return_value = mock_client

        result = gads_display_keyword_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "display_keywords" in data
        assert data["display_keywords"][0]["keyword_text"] == "running shoes"

    @patch("google_ads_mcp.tools.views.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_display_keyword_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result


# ---------------------------------------------------------------------------
# Topic View
# ---------------------------------------------------------------------------

class TestBuildTopicViewQuery:
    def test_date_range(self):
        query = _build_topic_view_query("1234567890", "2026-01-01", "2026-01-31")
        assert "FROM topic_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_campaign_filter(self):
        query = _build_topic_view_query("1234567890", "2026-01-01", "2026-01-31", campaign_id="11")
        assert "campaign.id = 11" in query


class TestParseTopicRow:
    def test_list_path(self):
        row = _make_topic_row(topic_path=["Arts & Entertainment", "Movies"])
        result = _parse_topic_row(row)
        assert result["topic_path"] == "Arts & Entertainment > Movies"

    def test_string_path(self):
        row = _make_topic_row(topic_path="/Arts & Entertainment/Movies")
        result = _parse_topic_row(row)
        assert result["topic_path"] == "/Arts & Entertainment/Movies"

    def test_basic_parsing(self):
        row = _make_topic_row()
        result = _parse_topic_row(row)
        assert result["impressions"] == 600
        assert result["clicks"] == 20


class TestGadsTopicView:
    @patch("google_ads_mcp.tools.views.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_topic_row(topic_path=["Arts", "Movies"]),
        ]
        mock_get_client.return_value = mock_client

        result = gads_topic_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Topic View" in result
        assert "Arts > Movies" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_topic_row()]
        mock_get_client.return_value = mock_client

        result = gads_topic_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "topics" in data
        assert "pagination" in data

    @patch("google_ads_mcp.tools.views.get_client")
    def test_campaign_id_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        gads_topic_view(
            customer_id="1234567890",
            campaign_id="11",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "campaign.id = 11" in called_query

    @patch("google_ads_mcp.tools.views.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_topic_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result


# ---------------------------------------------------------------------------
# User Location View
# ---------------------------------------------------------------------------

class TestBuildUserLocationViewQuery:
    def test_date_range(self):
        query = _build_user_location_view_query("1234567890", "2026-01-01", "2026-01-31")
        assert "FROM user_location_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_campaign_filter(self):
        query = _build_user_location_view_query("1234567890", "2026-01-01", "2026-01-31", campaign_id="22")
        assert "campaign.id = 22" in query


class TestParseUserLocationRow:
    def test_basic_parsing(self):
        row = _make_user_location_row()
        result = _parse_user_location_row(row)
        assert result["country_criterion_id"] == "2380"
        assert result["impressions"] == 700
        assert result["clicks"] == 35


class TestGadsUserLocationView:
    @patch("google_ads_mcp.tools.views.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_user_location_row(country_id="2380"),
            _make_user_location_row(country_id="2840"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_user_location_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## User Location View" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_user_location_row()]
        mock_get_client.return_value = mock_client

        result = gads_user_location_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "user_locations" in data
        assert data["user_locations"][0]["country_criterion_id"] == "2380"

    @patch("google_ads_mcp.tools.views.get_client")
    def test_campaign_id_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        gads_user_location_view(
            customer_id="1234567890",
            campaign_id="22",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "campaign.id = 22" in called_query

    @patch("google_ads_mcp.tools.views.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_user_location_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result


# ---------------------------------------------------------------------------
# Click View
# ---------------------------------------------------------------------------

class TestBuildClickViewQuery:
    def test_date_range(self):
        query = _build_click_view_query("1234567890", "2026-01-01", "2026-01-31")
        assert "FROM click_view" in query
        assert "BETWEEN '2026-01-01' AND '2026-01-31'" in query

    def test_campaign_filter(self):
        query = _build_click_view_query("1234567890", "2026-01-01", "2026-01-31", campaign_id="88")
        assert "campaign.id = 88" in query


class TestParseClickRow:
    def test_basic_parsing(self):
        row = _make_click_row()
        result = _parse_click_row(row)
        assert result["gclid"] == "CjwKCAtest123"
        assert result["city"] == "Milan"
        assert result["country"] == "Italy"
        assert result["device"] == "MOBILE"
        assert result["clicks"] == 1


class TestGadsClickView:
    @patch("google_ads_mcp.tools.views.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_click_row(gclid="gclid1", city="Milan"),
            _make_click_row(gclid="gclid2", city="Rome"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_click_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "## Click View" in result
        assert "Milan" in result
        assert "Rome" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_click_row()]
        mock_get_client.return_value = mock_client

        result = gads_click_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "clicks" in data
        assert data["clicks"][0]["gclid"] == "CjwKCAtest123"
        assert data["clicks"][0]["city"] == "Milan"

    @patch("google_ads_mcp.tools.views.get_client")
    def test_campaign_id_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        gads_click_view(
            customer_id="1234567890",
            campaign_id="88",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "campaign.id = 88" in called_query

    @patch("google_ads_mcp.tools.views.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_click_view(
            customer_id="1234567890",
            start_date="2026-01-01",
            end_date="2026-01-31",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result

    @patch("google_ads_mcp.tools.views.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_click_row(gclid=f"gclid_{i}")
            for i in range(10)
        ]
        mock_get_client.return_value = mock_client

        result = gads_click_view(
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
