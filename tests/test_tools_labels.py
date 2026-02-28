"""Tests for label management tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.labels import (
    _build_list_labels_query,
    _build_campaign_labels_query,
    _build_ad_group_labels_query,
    _build_ad_group_ad_labels_query,
    _build_ad_group_criterion_labels_query,
    _build_customer_labels_query,
    _parse_label_row,
    _parse_campaign_label_row,
    _parse_ad_group_label_row,
    _parse_ad_group_ad_label_row,
    _parse_ad_group_criterion_label_row,
    _parse_customer_label_row,
    gads_list_labels,
    gads_list_campaign_labels,
    gads_list_ad_group_labels,
    gads_list_ad_group_ad_labels,
    gads_list_ad_group_criterion_labels,
    gads_list_customer_labels,
)


# ---------------------------------------------------------------------------
# Helpers to build mock rows
# ---------------------------------------------------------------------------

def _make_label_row(
    label_id="100", name="Test Label", status="ENABLED",
    bg_color="#FF0000", description="A test label",
):
    row = MagicMock()
    row.label.id = label_id
    row.label.name = name
    row.label.status = status
    row.label.text_label.background_color = bg_color
    row.label.text_label.description = description
    return row


def _make_campaign_label_row(
    campaign_id="10", campaign_name="Campaign A",
    label_id="100", label_name="Label A",
):
    row = MagicMock()
    row.campaign.id = campaign_id
    row.campaign.name = campaign_name
    row.label.id = label_id
    row.label.name = label_name
    return row


def _make_ad_group_label_row(
    ad_group_id="20", ad_group_name="Ad Group A",
    label_id="100", label_name="Label A",
):
    row = MagicMock()
    row.ad_group.id = ad_group_id
    row.ad_group.name = ad_group_name
    row.label.id = label_id
    row.label.name = label_name
    return row


def _make_ad_group_ad_label_row(
    ad_id="30", ad_name="Ad A",
    label_id="100", label_name="Label A",
):
    row = MagicMock()
    row.ad_group_ad.ad.id = ad_id
    row.ad_group_ad.ad.name = ad_name
    row.label.id = label_id
    row.label.name = label_name
    return row


def _make_criterion_label_row(
    criterion_id="40",
    label_id="100", label_name="Label A",
):
    row = MagicMock()
    row.ad_group_criterion.criterion_id = criterion_id
    row.label.id = label_id
    row.label.name = label_name
    return row


def _make_customer_label_row(
    customer_id="1234567890",
    label_id="100", label_name="Label A",
):
    row = MagicMock()
    row.customer.id = customer_id
    row.label.id = label_id
    row.label.name = label_name
    return row


# ---------------------------------------------------------------------------
# Tests: gads_list_labels
# ---------------------------------------------------------------------------

class TestBuildListLabelsQuery:
    def test_query_structure(self):
        query = _build_list_labels_query()
        assert "FROM label" in query
        assert "label.id" in query
        assert "label.name" in query
        assert "label.status" in query
        assert "label.text_label.background_color" in query
        assert "label.text_label.description" in query
        assert "ORDER BY label.name" in query


class TestParseLabelRow:
    def test_basic_parsing(self):
        row = _make_label_row()
        result = _parse_label_row(row)
        assert result["id"] == "100"
        assert result["name"] == "Test Label"
        assert result["background_color"] == "#FF0000"
        assert result["description"] == "A test label"

    def test_status_strip(self):
        row = _make_label_row(status="LabelStatus.ENABLED")
        result = _parse_label_row(row)
        assert result["status"] == "ENABLED"


class TestGadsListLabels:
    @patch("google_ads_mcp.tools.labels.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_label_row(label_id="1", name="Label A"),
            _make_label_row(label_id="2", name="Label B"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Labels" in result
        assert "Label A" in result
        assert "Label B" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_label_row(label_id="1", name="Test"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_labels(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "labels" in data
        assert "pagination" in data
        assert len(data["labels"]) == 1
        assert data["labels"][0]["name"] == "Test"

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_label_row(label_id=str(i), name=f"Label {i}")
            for i in range(5)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_labels(
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


# ---------------------------------------------------------------------------
# Tests: gads_list_campaign_labels
# ---------------------------------------------------------------------------

class TestBuildCampaignLabelsQuery:
    def test_no_filters(self):
        query = _build_campaign_labels_query()
        assert "FROM campaign_label" in query
        assert "WHERE" not in query

    def test_campaign_id_filter(self):
        query = _build_campaign_labels_query(campaign_id="10")
        assert "campaign.id = 10" in query

    def test_label_id_filter(self):
        query = _build_campaign_labels_query(label_id="100")
        assert "label.id = 100" in query

    def test_combined_filters(self):
        query = _build_campaign_labels_query(campaign_id="10", label_id="100")
        assert "campaign.id = 10" in query
        assert "label.id = 100" in query
        assert " AND " in query


class TestGadsListCampaignLabels:
    @patch("google_ads_mcp.tools.labels.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_campaign_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Campaign Labels" in result
        assert "Campaign A" in result
        assert "Label A" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_campaign_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_labels(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "campaign_labels" in data
        assert "pagination" in data
        assert data["campaign_labels"][0]["campaign_name"] == "Campaign A"

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_with_campaign_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_campaign_label_row(campaign_id="10"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_labels(
            customer_id="1234567890",
            campaign_id="10",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert len(data["campaign_labels"]) == 1

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result


# ---------------------------------------------------------------------------
# Tests: gads_list_ad_group_labels
# ---------------------------------------------------------------------------

class TestBuildAdGroupLabelsQuery:
    def test_no_filters(self):
        query = _build_ad_group_labels_query()
        assert "FROM ad_group_label" in query
        assert "WHERE" not in query

    def test_ad_group_id_filter(self):
        query = _build_ad_group_labels_query(ad_group_id="20")
        assert "ad_group.id = 20" in query

    def test_label_id_filter(self):
        query = _build_ad_group_labels_query(label_id="100")
        assert "label.id = 100" in query


class TestGadsListAdGroupLabels:
    @patch("google_ads_mcp.tools.labels.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_ad_group_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Ad Group Labels" in result
        assert "Ad Group A" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_ad_group_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_labels(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "ad_group_labels" in data
        assert data["ad_group_labels"][0]["ad_group_name"] == "Ad Group A"

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_with_filters(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_ad_group_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_labels(
            customer_id="1234567890",
            ad_group_id="20",
            label_id="100",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert len(data["ad_group_labels"]) == 1

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result


# ---------------------------------------------------------------------------
# Tests: gads_list_ad_group_ad_labels
# ---------------------------------------------------------------------------

class TestBuildAdGroupAdLabelsQuery:
    def test_no_filters(self):
        query = _build_ad_group_ad_labels_query()
        assert "FROM ad_group_ad_label" in query
        assert "WHERE" not in query

    def test_label_id_filter(self):
        query = _build_ad_group_ad_labels_query(label_id="100")
        assert "label.id = 100" in query


class TestGadsListAdGroupAdLabels:
    @patch("google_ads_mcp.tools.labels.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_ad_group_ad_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_ad_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Ad Labels" in result
        assert "Ad A" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_ad_group_ad_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_ad_labels(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "ad_labels" in data
        assert data["ad_labels"][0]["ad_name"] == "Ad A"

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_with_label_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_ad_group_ad_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_ad_labels(
            customer_id="1234567890",
            label_id="100",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert len(data["ad_labels"]) == 1

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_ad_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result


# ---------------------------------------------------------------------------
# Tests: gads_list_ad_group_criterion_labels
# ---------------------------------------------------------------------------

class TestBuildAdGroupCriterionLabelsQuery:
    def test_no_filters(self):
        query = _build_ad_group_criterion_labels_query()
        assert "FROM ad_group_criterion_label" in query
        assert "WHERE" not in query

    def test_label_id_filter(self):
        query = _build_ad_group_criterion_labels_query(label_id="100")
        assert "label.id = 100" in query


class TestGadsListAdGroupCriterionLabels:
    @patch("google_ads_mcp.tools.labels.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_criterion_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_criterion_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Criterion Labels" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_criterion_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_criterion_labels(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "criterion_labels" in data
        assert data["criterion_labels"][0]["criterion_id"] == "40"

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_ad_group_criterion_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result


# ---------------------------------------------------------------------------
# Tests: gads_list_customer_labels
# ---------------------------------------------------------------------------

class TestBuildCustomerLabelsQuery:
    def test_query_structure(self):
        query = _build_customer_labels_query()
        assert "FROM customer_label" in query
        assert "customer.id" in query
        assert "label.id" in query
        assert "label.name" in query


class TestGadsListCustomerLabels:
    @patch("google_ads_mcp.tools.labels.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_customer_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_customer_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Customer Labels" in result
        assert "Label A" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_customer_label_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_customer_labels(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "customer_labels" in data
        assert data["customer_labels"][0]["label_name"] == "Label A"

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_customer_labels(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result

    @patch("google_ads_mcp.tools.labels.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_customer_label_row(label_id=str(i), label_name=f"Label {i}")
            for i in range(4)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_customer_labels(
            customer_id="1234567890",
            limit=2,
            offset=1,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 4
        assert data["pagination"]["count"] == 2
        assert data["pagination"]["offset"] == 1
        assert data["pagination"]["has_more"] is True


# ---------------------------------------------------------------------------
# Tests: parse helper functions
# ---------------------------------------------------------------------------

class TestParseHelpers:
    def test_parse_campaign_label_row(self):
        row = _make_campaign_label_row()
        result = _parse_campaign_label_row(row)
        assert result["campaign_id"] == "10"
        assert result["campaign_name"] == "Campaign A"
        assert result["label_id"] == "100"
        assert result["label_name"] == "Label A"

    def test_parse_ad_group_label_row(self):
        row = _make_ad_group_label_row()
        result = _parse_ad_group_label_row(row)
        assert result["ad_group_id"] == "20"
        assert result["ad_group_name"] == "Ad Group A"

    def test_parse_ad_group_ad_label_row(self):
        row = _make_ad_group_ad_label_row()
        result = _parse_ad_group_ad_label_row(row)
        assert result["ad_id"] == "30"
        assert result["ad_name"] == "Ad A"

    def test_parse_criterion_label_row(self):
        row = _make_criterion_label_row()
        result = _parse_ad_group_criterion_label_row(row)
        assert result["criterion_id"] == "40"
        assert result["label_id"] == "100"

    def test_parse_customer_label_row(self):
        row = _make_customer_label_row()
        result = _parse_customer_label_row(row)
        assert result["customer_id"] == "1234567890"
        assert result["label_name"] == "Label A"
