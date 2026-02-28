"""Tests for shopping tools."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.shopping_ops import (
    gads_set_listing_group_filter,
    gads_link_merchant_center,
)


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    response = MagicMock()
    response.mutate_operation_responses = [
        MagicMock(
            asset_group_listing_group_filter_result=MagicMock(
                resource_name="customers/1234567890/assetGroupListingGroupFilters/555~123"
            )
        ),
    ]
    wrapper.mutate.return_value = response
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


@pytest.fixture
def mock_ctx_campaign():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    wrapper.mutate.return_value = MagicMock(mutate_operation_responses=[MagicMock()])
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


class TestSetListingGroupFilter:
    def test_unit_included_brand(self, mock_ctx):
        result = gads_set_listing_group_filter(
            customer_id="1234567890",
            asset_group_id="555",
            filter_type="UNIT_INCLUDED",
            dimension="BRAND",
            value="Nike",
            ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "BRAND" in result

    def test_subdivision(self, mock_ctx):
        result = gads_set_listing_group_filter(
            customer_id="1234567890",
            asset_group_id="555",
            filter_type="SUBDIVISION",
            dimension="CATEGORY_L1",
            ctx=mock_ctx,
        )
        assert "SUBDIVISION" in result

    def test_with_parent_filter(self, mock_ctx):
        result = gads_set_listing_group_filter(
            customer_id="1234567890",
            asset_group_id="555",
            filter_type="UNIT_INCLUDED",
            dimension="BRAND",
            value="Nike",
            parent_filter_id="parent_001",
            ctx=mock_ctx,
        )
        assert isinstance(result, str)


class TestLinkMerchantCenter:
    def test_basic_link(self, mock_ctx_campaign):
        result = gads_link_merchant_center(
            customer_id="1234567890",
            campaign_id="111",
            merchant_id="12345678",
            ctx=mock_ctx_campaign,
        )
        wrapper = mock_ctx_campaign.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "12345678" in result

    def test_with_feed_label(self, mock_ctx_campaign):
        result = gads_link_merchant_center(
            customer_id="1234567890",
            campaign_id="111",
            merchant_id="12345678",
            feed_label="online",
            sales_country="US",
            ctx=mock_ctx_campaign,
        )
        assert "12345678" in result
