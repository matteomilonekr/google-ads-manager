"""Tests for keyword, bidding, and update builders."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.builders.operations import (
    build_add_keywords_operations,
    build_bidding_strategy_operation,
    build_update_keyword_operation,
)


@pytest.fixture
def mock_google_client():
    client = MagicMock()
    client.get_type.side_effect = lambda name: MagicMock()
    return client


class TestBuildAddKeywordsOperations:
    def test_returns_list(self, mock_google_client):
        ops = build_add_keywords_operations(
            mock_google_client, "1234567890", "222",
            ["shoes", "boots"], "broad",
        )
        assert isinstance(ops, list)
        assert len(ops) == 2

    def test_single_keyword(self, mock_google_client):
        ops = build_add_keywords_operations(
            mock_google_client, "1234567890", "222",
            ["shoes"], "exact",
        )
        assert len(ops) == 1

    def test_with_bid(self, mock_google_client):
        ops = build_add_keywords_operations(
            mock_google_client, "1234567890", "222",
            ["shoes"], "exact", cpc_bid_micros=1_500_000,
        )
        assert len(ops) == 1


class TestBuildBiddingStrategyOperation:
    def test_manual_cpc(self, mock_google_client):
        op = build_bidding_strategy_operation(
            mock_google_client, "1234567890", "111",
            strategy_type="MANUAL_CPC",
        )
        assert op is not None

    def test_target_cpa(self, mock_google_client):
        op = build_bidding_strategy_operation(
            mock_google_client, "1234567890", "111",
            strategy_type="TARGET_CPA",
            target_cpa_micros=5_000_000,
        )
        assert op is not None

    def test_target_roas(self, mock_google_client):
        op = build_bidding_strategy_operation(
            mock_google_client, "1234567890", "111",
            strategy_type="TARGET_ROAS",
            target_roas=3.0,
        )
        assert op is not None


class TestBuildUpdateKeywordOperation:
    def test_update_bid(self, mock_google_client):
        op = build_update_keyword_operation(
            mock_google_client, "1234567890", "222", "555",
            cpc_bid_micros=2_000_000,
        )
        assert op is not None

    def test_update_status(self, mock_google_client):
        op = build_update_keyword_operation(
            mock_google_client, "1234567890", "222", "555",
            status="pause",
        )
        assert op is not None

    def test_update_both(self, mock_google_client):
        op = build_update_keyword_operation(
            mock_google_client, "1234567890", "222", "555",
            cpc_bid_micros=2_000_000, status="enable",
        )
        assert op is not None
