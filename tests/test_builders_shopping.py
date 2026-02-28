"""Tests for Phase 5 shopping operation builders."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.builders.operations import (
    build_listing_group_filter_operation,
    build_merchant_center_link_operation,
    LISTING_GROUP_FILTER_TYPE_TO_ENUM,
)


@pytest.fixture
def mock_google_client():
    client = MagicMock()
    client.get_type.side_effect = lambda name: MagicMock()
    return client


class TestListingGroupFilterTypeToEnum:
    def test_unit_included(self):
        assert LISTING_GROUP_FILTER_TYPE_TO_ENUM["UNIT_INCLUDED"] == 2

    def test_unit_excluded(self):
        assert LISTING_GROUP_FILTER_TYPE_TO_ENUM["UNIT_EXCLUDED"] == 3

    def test_subdivision(self):
        assert LISTING_GROUP_FILTER_TYPE_TO_ENUM["SUBDIVISION"] == 4


class TestBuildListingGroupFilterOperation:
    def test_unit_included_brand(self, mock_google_client):
        op = build_listing_group_filter_operation(
            mock_google_client, "1234567890",
            asset_group_id="555",
            filter_type="UNIT_INCLUDED",
            dimension="BRAND",
            value="Nike",
        )
        assert op is not None

    def test_subdivision(self, mock_google_client):
        op = build_listing_group_filter_operation(
            mock_google_client, "1234567890",
            asset_group_id="555",
            filter_type="SUBDIVISION",
            dimension="CATEGORY_L1",
        )
        assert op is not None

    def test_with_parent_filter(self, mock_google_client):
        op = build_listing_group_filter_operation(
            mock_google_client, "1234567890",
            asset_group_id="555",
            filter_type="UNIT_INCLUDED",
            dimension="BRAND",
            value="Nike",
            parent_filter_id="parent_001",
        )
        assert op is not None


class TestBuildMerchantCenterLinkOperation:
    def test_basic(self, mock_google_client):
        op = build_merchant_center_link_operation(
            mock_google_client, "1234567890",
            campaign_id="111",
            merchant_id="12345678",
        )
        assert op is not None

    def test_with_feed_label(self, mock_google_client):
        op = build_merchant_center_link_operation(
            mock_google_client, "1234567890",
            campaign_id="111",
            merchant_id="12345678",
            feed_label="online",
            sales_country="US",
        )
        assert op is not None
