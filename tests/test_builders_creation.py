"""Tests for Phase 4 creation operation builders."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.builders.operations import (
    build_create_campaign_operations,
    build_create_ad_group_operation,
    build_create_rsa_operation,
    CAMPAIGN_TYPE_TO_ENUM,
    AD_GROUP_TYPE_TO_ENUM,
    BIDDING_STRATEGY_MAP,
)


@pytest.fixture
def mock_google_client():
    client = MagicMock()
    client.get_type.side_effect = lambda name: MagicMock()
    client.get_service.side_effect = lambda name: MagicMock()
    return client


class TestCampaignTypeToEnum:
    def test_search(self):
        assert CAMPAIGN_TYPE_TO_ENUM["SEARCH"] == 2

    def test_display(self):
        assert CAMPAIGN_TYPE_TO_ENUM["DISPLAY"] == 3

    def test_performance_max(self):
        assert CAMPAIGN_TYPE_TO_ENUM["PERFORMANCE_MAX"] == 14


class TestAdGroupTypeToEnum:
    def test_search_standard(self):
        assert AD_GROUP_TYPE_TO_ENUM["SEARCH_STANDARD"] == 2

    def test_video_responsive(self):
        assert AD_GROUP_TYPE_TO_ENUM["VIDEO_RESPONSIVE"] == 9


class TestBiddingStrategyMap:
    def test_manual_cpc(self):
        assert BIDDING_STRATEGY_MAP["MANUAL_CPC"] == "manual_cpc"

    def test_target_cpa(self):
        assert BIDDING_STRATEGY_MAP["TARGET_CPA"] == "target_cpa"


class TestBuildCreateCampaignOperations:
    def test_returns_two_operations(self, mock_google_client):
        ops = build_create_campaign_operations(
            mock_google_client, "1234567890",
            name="Test Campaign",
            campaign_type="SEARCH",
            bidding_strategy_type="MANUAL_CPC",
            budget_amount_micros=10_000_000,
        )
        assert isinstance(ops, list)
        assert len(ops) == 2  # budget + campaign

    def test_with_dates(self, mock_google_client):
        ops = build_create_campaign_operations(
            mock_google_client, "1234567890",
            name="Dated",
            campaign_type="DISPLAY",
            bidding_strategy_type="MAXIMIZE_CLICKS",
            budget_amount_micros=5_000_000,
            start_date="2026-03-01",
            end_date="2026-12-31",
        )
        assert len(ops) == 2

    def test_with_target_cpa(self, mock_google_client):
        ops = build_create_campaign_operations(
            mock_google_client, "1234567890",
            name="CPA",
            campaign_type="SEARCH",
            bidding_strategy_type="TARGET_CPA",
            budget_amount_micros=10_000_000,
            target_cpa_micros=5_000_000,
        )
        assert len(ops) == 2

    def test_with_target_roas(self, mock_google_client):
        ops = build_create_campaign_operations(
            mock_google_client, "1234567890",
            name="ROAS Campaign",
            campaign_type="SEARCH",
            bidding_strategy_type="TARGET_ROAS",
            budget_amount_micros=10_000_000,
            target_roas=4.0,
        )
        assert len(ops) == 2


class TestBuildCreateAdGroupOperation:
    def test_returns_operation(self, mock_google_client):
        op = build_create_ad_group_operation(
            mock_google_client, "1234567890", "111",
            name="My Ad Group",
            ad_group_type="SEARCH_STANDARD",
        )
        assert op is not None

    def test_with_bid(self, mock_google_client):
        op = build_create_ad_group_operation(
            mock_google_client, "1234567890", "111",
            name="Bid Group",
            ad_group_type="SEARCH_STANDARD",
            cpc_bid_micros=2_000_000,
        )
        assert op is not None


class TestBuildCreateRsaOperation:
    def test_returns_operation(self, mock_google_client):
        op = build_create_rsa_operation(
            mock_google_client, "1234567890", "222",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
        )
        assert op is not None

    def test_with_paths(self, mock_google_client):
        op = build_create_rsa_operation(
            mock_google_client, "1234567890", "222",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
            path1="sale",
            path2="shoes",
        )
        assert op is not None
