"""Tests for strategy and budget read tools (Phase 4)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.budgets import (
    _build_list_campaign_budgets_query,
    _build_bidding_strategies_query,
    _build_ad_group_bidding_query,
    _build_change_history_query,
    _parse_budget_row,
    _parse_bidding_strategy_row,
    _parse_ad_group_bidding_row,
    _parse_change_history_row,
    gads_list_campaign_budgets,
    gads_get_bidding_strategies,
    gads_get_ad_group_bidding_strategies,
    gads_list_change_history,
)


# ---------------------------------------------------------------------------
# Row factories
# ---------------------------------------------------------------------------

def _make_budget_row(
    budget_id="100",
    name="Daily Budget",
    amount_micros=50000000,
    delivery_method="STANDARD",
    status="ENABLED",
    budget_type="STANDARD",
    explicitly_shared="false",
    total_amount_micros=0,
    recommended_micros=60000000,
):
    row = MagicMock()
    row.campaign_budget.id = budget_id
    row.campaign_budget.name = name
    row.campaign_budget.amount_micros = amount_micros
    row.campaign_budget.delivery_method = delivery_method
    row.campaign_budget.status = status
    row.campaign_budget.type = budget_type
    row.campaign_budget.explicitly_shared = explicitly_shared
    row.campaign_budget.total_amount_micros = total_amount_micros
    row.campaign_budget.recommended_budget_amount_micros = recommended_micros
    return row


def _make_bidding_strategy_row(
    campaign_id="200",
    name="Search Campaign",
    strategy_type="TARGET_CPA",
    bidding_strategy="bidding_strategies/123",
    target_cpa_micros=3000000,
    max_conv_cpa_micros=0,
    target_roas=0.0,
    max_conv_value_roas=0.0,
):
    row = MagicMock()
    row.campaign.id = campaign_id
    row.campaign.name = name
    row.campaign.bidding_strategy_type = strategy_type
    row.campaign.bidding_strategy = bidding_strategy
    row.campaign.target_cpa.target_cpa_micros = target_cpa_micros
    row.campaign.maximize_conversions.target_cpa_micros = max_conv_cpa_micros
    row.campaign.target_roas.target_roas = target_roas
    row.campaign.maximize_conversion_value.target_roas = max_conv_value_roas
    return row


def _make_ad_group_bidding_row(
    ag_id="300",
    name="Ad Group 1",
    cpc_bid_micros=1500000,
    target_cpa_micros=2500000,
    effective_target_cpa_micros=2500000,
    effective_target_roas=3.5,
):
    row = MagicMock()
    row.ad_group.id = ag_id
    row.ad_group.name = name
    row.ad_group.cpc_bid_micros = cpc_bid_micros
    row.ad_group.target_cpa_micros = target_cpa_micros
    row.ad_group.effective_target_cpa_micros = effective_target_cpa_micros
    row.ad_group.effective_target_roas = effective_target_roas
    return row


def _make_change_history_row(
    resource_name="customers/123/campaigns/456",
    resource_type="CAMPAIGN",
    resource_status="ENABLED",
    last_change="2026-02-01T10:30:00Z",
):
    row = MagicMock()
    row.change_status.resource_name = resource_name
    row.change_status.resource_type = resource_type
    row.change_status.resource_status = resource_status
    row.change_status.last_change_date_time = last_change
    return row


# ---------------------------------------------------------------------------
# Campaign Budgets
# ---------------------------------------------------------------------------

class TestBuildListCampaignBudgetsQuery:
    def test_basic_query(self):
        query = _build_list_campaign_budgets_query()
        assert "FROM campaign_budget" in query
        assert "campaign_budget.id" in query
        assert "campaign_budget.amount_micros" in query
        assert "campaign_budget.recommended_budget_amount_micros" in query


class TestParseBudgetRow:
    def test_basic_parsing(self):
        row = _make_budget_row()
        result = _parse_budget_row(row)
        assert result["id"] == "100"
        assert result["name"] == "Daily Budget"
        assert result["amount"] == "50.00"
        assert result["amount_micros"] == 50000000
        assert result["delivery_method"] == "STANDARD"
        assert result["status"] == "ENABLED"
        assert result["recommended_amount"] == "60.00"

    def test_zero_amounts(self):
        row = _make_budget_row(amount_micros=0, recommended_micros=0)
        result = _parse_budget_row(row)
        assert result["amount"] == "0.00"
        assert result["recommended_amount"] == "0.00"


class TestGadsListCampaignBudgets:
    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_budget_row(budget_id="1", name="Budget A"),
            _make_budget_row(budget_id="2", name="Budget B"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_budgets(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Campaign Budgets" in result
        assert "Budget A" in result
        assert "Budget B" in result

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_budget_row()]
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_budgets(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "budgets" in data
        assert "pagination" in data
        assert data["budgets"][0]["id"] == "100"
        assert data["budgets"][0]["amount"] == "50.00"

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_budgets(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_budget_row(budget_id=str(i), name=f"Budget {i}")
            for i in range(8)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_campaign_budgets(
            customer_id="1234567890",
            limit=3,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 8
        assert data["pagination"]["count"] == 3
        assert data["pagination"]["has_more"] is True


# ---------------------------------------------------------------------------
# Bidding Strategies
# ---------------------------------------------------------------------------

class TestBuildBiddingStrategiesQuery:
    def test_basic_query(self):
        query = _build_bidding_strategies_query()
        assert "FROM campaign" in query
        assert "campaign.status != 'REMOVED'" in query
        assert "campaign.bidding_strategy_type" in query
        assert "ORDER BY campaign.name" in query

    def test_campaign_filter(self):
        query = _build_bidding_strategies_query(campaign_id="50")
        assert "campaign.id = 50" in query

    def test_no_campaign_filter(self):
        query = _build_bidding_strategies_query()
        assert "campaign.id =" not in query


class TestParseBiddingStrategyRow:
    def test_target_cpa(self):
        row = _make_bidding_strategy_row(
            strategy_type="TARGET_CPA", target_cpa_micros=3000000
        )
        result = _parse_bidding_strategy_row(row)
        assert result["target_cpa"] == "3.00"
        assert result["target_roas"] == "-"

    def test_target_roas(self):
        row = _make_bidding_strategy_row(
            strategy_type="TARGET_ROAS",
            target_cpa_micros=0,
            target_roas=4.5,
        )
        result = _parse_bidding_strategy_row(row)
        assert result["target_cpa"] == "-"
        assert result["target_roas"] == "4.50"

    def test_maximize_conversions_with_cpa(self):
        row = _make_bidding_strategy_row(
            strategy_type="MAXIMIZE_CONVERSIONS",
            target_cpa_micros=0,
            max_conv_cpa_micros=2000000,
        )
        result = _parse_bidding_strategy_row(row)
        assert result["target_cpa"] == "2.00"

    def test_maximize_conversion_value_with_roas(self):
        row = _make_bidding_strategy_row(
            strategy_type="MAXIMIZE_CONVERSION_VALUE",
            target_cpa_micros=0,
            target_roas=0.0,
            max_conv_value_roas=5.0,
        )
        result = _parse_bidding_strategy_row(row)
        assert result["target_roas"] == "5.00"

    def test_basic_fields(self):
        row = _make_bidding_strategy_row()
        result = _parse_bidding_strategy_row(row)
        assert result["id"] == "200"
        assert result["name"] == "Search Campaign"


class TestGadsGetBiddingStrategies:
    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_bidding_strategy_row(name="Campaign Alpha"),
            _make_bidding_strategy_row(name="Campaign Beta"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_get_bidding_strategies(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Bidding Strategies" in result
        assert "Campaign Alpha" in result
        assert "Campaign Beta" in result

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_bidding_strategy_row()]
        mock_get_client.return_value = mock_client

        result = gads_get_bidding_strategies(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "bidding_strategies" in data
        assert "pagination" in data
        assert data["bidding_strategies"][0]["id"] == "200"

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_campaign_id_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_bidding_strategy_row()]
        mock_get_client.return_value = mock_client

        gads_get_bidding_strategies(
            customer_id="1234567890",
            campaign_id="50",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "campaign.id = 50" in called_query

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_get_bidding_strategies(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result


# ---------------------------------------------------------------------------
# Ad Group Bidding Strategies
# ---------------------------------------------------------------------------

class TestBuildAdGroupBiddingQuery:
    def test_basic_query(self):
        query = _build_ad_group_bidding_query()
        assert "FROM ad_group" in query
        assert "ad_group.status != 'REMOVED'" in query
        assert "ad_group.cpc_bid_micros" in query
        assert "ORDER BY ad_group.name" in query

    def test_campaign_filter(self):
        query = _build_ad_group_bidding_query(campaign_id="60")
        assert "campaign.id = 60" in query

    def test_no_campaign_filter(self):
        query = _build_ad_group_bidding_query()
        assert "campaign.id =" not in query


class TestParseAdGroupBiddingRow:
    def test_basic_parsing(self):
        row = _make_ad_group_bidding_row()
        result = _parse_ad_group_bidding_row(row)
        assert result["id"] == "300"
        assert result["name"] == "Ad Group 1"
        assert result["cpc_bid"] == "1.50"
        assert result["target_cpa"] == "2.50"
        assert result["effective_target_cpa"] == "2.50"
        assert result["effective_target_roas"] == "3.50"


class TestGadsGetAdGroupBiddingStrategies:
    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_ad_group_bidding_row(name="AG Alpha"),
            _make_ad_group_bidding_row(name="AG Beta"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_get_ad_group_bidding_strategies(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Ad Group Bidding" in result
        assert "AG Alpha" in result
        assert "AG Beta" in result

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_ad_group_bidding_row()]
        mock_get_client.return_value = mock_client

        result = gads_get_ad_group_bidding_strategies(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "ad_group_bidding" in data
        assert data["ad_group_bidding"][0]["id"] == "300"
        assert data["ad_group_bidding"][0]["cpc_bid"] == "1.50"

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_campaign_id_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        gads_get_ad_group_bidding_strategies(
            customer_id="1234567890",
            campaign_id="60",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "campaign.id = 60" in called_query

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_get_ad_group_bidding_strategies(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result


# ---------------------------------------------------------------------------
# Change History
# ---------------------------------------------------------------------------

class TestBuildChangeHistoryQuery:
    def test_basic_query(self):
        query = _build_change_history_query()
        assert "FROM change_status" in query
        assert "ORDER BY change_status.last_change_date_time DESC" in query
        assert "WHERE" not in query

    def test_resource_type_filter(self):
        query = _build_change_history_query(resource_type="CAMPAIGN")
        assert "change_status.resource_type = 'CAMPAIGN'" in query
        assert "WHERE" in query

    def test_no_resource_type_filter(self):
        query = _build_change_history_query()
        assert "resource_type =" not in query


class TestParseChangeHistoryRow:
    def test_basic_parsing(self):
        row = _make_change_history_row()
        result = _parse_change_history_row(row)
        assert result["resource_name"] == "customers/123/campaigns/456"
        assert result["resource_type"] == "CAMPAIGN"
        assert result["resource_status"] == "ENABLED"
        assert result["last_change_date_time"] == "2026-02-01T10:30:00Z"


class TestGadsListChangeHistory:
    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_change_history_row(resource_type="CAMPAIGN"),
            _make_change_history_row(resource_type="AD_GROUP"),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_change_history(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Change History" in result
        assert "CAMPAIGN" in result
        assert "AD_GROUP" in result

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_change_history_row()]
        mock_get_client.return_value = mock_client

        result = gads_list_change_history(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "change_history" in data
        assert "pagination" in data
        assert data["change_history"][0]["resource_type"] == "CAMPAIGN"

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_resource_type_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_change_history_row()]
        mock_get_client.return_value = mock_client

        gads_list_change_history(
            customer_id="1234567890",
            resource_type="CAMPAIGN",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "change_status.resource_type = 'CAMPAIGN'" in called_query

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_no_resource_type_filter(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [_make_change_history_row()]
        mock_get_client.return_value = mock_client

        gads_list_change_history(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        called_query = mock_client.query.call_args[0][1]
        assert "WHERE" not in called_query

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_change_history(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result

    @patch("google_ads_mcp.tools.budgets.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_change_history_row(
                resource_name=f"customers/123/campaigns/{i}",
                last_change=f"2026-02-0{i+1}T10:00:00Z",
            )
            for i in range(6)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_change_history(
            customer_id="1234567890",
            limit=2,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 6
        assert data["pagination"]["count"] == 2
        assert data["pagination"]["has_more"] is True
