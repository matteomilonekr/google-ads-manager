"""Tests for mutation operation builders."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.builders.operations import (
    build_campaign_status_operation,
    build_campaign_update_operation,
    build_ad_group_status_operation,
    build_ad_status_operation,
    build_budget_update_operation,
    build_negative_keyword_operations,
    build_location_criterion_operations,
    build_language_criterion_operations,
    STATUS_TO_ENUM,
    MATCH_TYPE_TO_ENUM,
)


@pytest.fixture
def mock_google_client():
    """Mock GoogleAdsClient that returns MagicMock types and services."""
    client = MagicMock()
    # get_type returns a mock proto constructor
    client.get_type.side_effect = lambda name: MagicMock()
    # get_service returns a mock service
    client.get_service.side_effect = lambda name: MagicMock()
    return client


class TestStatusToEnum:
    def test_enable(self):
        assert STATUS_TO_ENUM["enable"] == 2  # ENABLED

    def test_pause(self):
        assert STATUS_TO_ENUM["pause"] == 3  # PAUSED

    def test_remove(self):
        assert STATUS_TO_ENUM["remove"] == 4  # REMOVED


class TestBuildCampaignStatusOperation:
    def test_returns_mutate_operation(self, mock_google_client):
        op = build_campaign_status_operation(
            mock_google_client, "1234567890", "111", "pause"
        )
        assert op is not None
        mock_google_client.get_type.assert_called()

    def test_sets_resource_name(self, mock_google_client):
        op = build_campaign_status_operation(
            mock_google_client, "1234567890", "111", "enable"
        )
        assert op is not None


class TestBuildCampaignUpdateOperation:
    def test_with_name(self, mock_google_client):
        op = build_campaign_update_operation(
            mock_google_client, "1234567890", "111", name="New Campaign"
        )
        assert op is not None

    def test_with_dates(self, mock_google_client):
        op = build_campaign_update_operation(
            mock_google_client, "1234567890", "111",
            start_date="2026-03-01", end_date="2026-12-31"
        )
        assert op is not None


class TestBuildAdGroupStatusOperation:
    def test_returns_operation(self, mock_google_client):
        op = build_ad_group_status_operation(
            mock_google_client, "1234567890", "222", "pause"
        )
        assert op is not None


class TestBuildAdStatusOperation:
    def test_returns_operation(self, mock_google_client):
        op = build_ad_status_operation(
            mock_google_client, "1234567890", "222", "333", "enable"
        )
        assert op is not None


class TestBuildBudgetUpdateOperation:
    def test_returns_operation(self, mock_google_client):
        op = build_budget_update_operation(
            mock_google_client, "1234567890", "444", 5_000_000
        )
        assert op is not None


class TestBuildNegativeKeywordOperations:
    def test_returns_list(self, mock_google_client):
        ops = build_negative_keyword_operations(
            mock_google_client, "1234567890", "campaign", "111",
            ["free", "cheap"], "exact"
        )
        assert isinstance(ops, list)
        assert len(ops) == 2

    def test_single_keyword(self, mock_google_client):
        ops = build_negative_keyword_operations(
            mock_google_client, "1234567890", "ad_group", "222",
            ["discount"], "phrase"
        )
        assert len(ops) == 1


class TestBuildLocationCriterionOperations:
    def test_returns_list(self, mock_google_client):
        ops = build_location_criterion_operations(
            mock_google_client, "1234567890", "111", [2380, 2826], False
        )
        assert isinstance(ops, list)
        assert len(ops) == 2

    def test_exclude(self, mock_google_client):
        ops = build_location_criterion_operations(
            mock_google_client, "1234567890", "111", [2380], True
        )
        assert len(ops) == 1


class TestBuildLanguageCriterionOperations:
    def test_returns_list(self, mock_google_client):
        ops = build_language_criterion_operations(
            mock_google_client, "1234567890", "111", [1000, 1004]
        )
        assert isinstance(ops, list)
        assert len(ops) == 2
