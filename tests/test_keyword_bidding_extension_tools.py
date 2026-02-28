"""Tests for keyword, bidding, and extension tools."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.keyword_ops import gads_add_keywords, gads_update_keyword
from google_ads_mcp.tools.mutations.bidding_ops import gads_set_bidding_strategy
from google_ads_mcp.tools.mutations.extension_ops import gads_create_ad_extension


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    wrapper.mutate.return_value = MagicMock(
        mutate_operation_responses=[MagicMock()]
    )
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


class TestAddKeywords:
    def test_add_keywords(self, mock_ctx):
        result = gads_add_keywords(
            customer_id="1234567890", ad_group_id="222",
            keywords=["shoes", "boots"], match_type="broad", ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "2" in result

    def test_with_bid(self, mock_ctx):
        result = gads_add_keywords(
            customer_id="1234567890", ad_group_id="222",
            keywords=["shoes"], match_type="exact",
            cpc_bid_micros=1_500_000, ctx=mock_ctx,
        )
        assert isinstance(result, str)


class TestUpdateKeyword:
    def test_update_bid(self, mock_ctx):
        result = gads_update_keyword(
            customer_id="1234567890", ad_group_id="222",
            criterion_id="555", cpc_bid_micros=2_000_000, ctx=mock_ctx,
        )
        assert "555" in result

    def test_update_status(self, mock_ctx):
        result = gads_update_keyword(
            customer_id="1234567890", ad_group_id="222",
            criterion_id="555", status="pause", ctx=mock_ctx,
        )
        assert "555" in result


class TestSetBiddingStrategy:
    def test_manual_cpc(self, mock_ctx):
        result = gads_set_bidding_strategy(
            customer_id="1234567890", campaign_id="111",
            strategy_type="MANUAL_CPC", ctx=mock_ctx,
        )
        assert "MANUAL_CPC" in result

    def test_target_cpa(self, mock_ctx):
        result = gads_set_bidding_strategy(
            customer_id="1234567890", campaign_id="111",
            strategy_type="TARGET_CPA", target_cpa_micros=5_000_000, ctx=mock_ctx,
        )
        assert "TARGET_CPA" in result


class TestCreateAdExtension:
    def test_sitelink(self, mock_ctx):
        result = gads_create_ad_extension(
            customer_id="1234567890", campaign_id="111",
            extension_type="SITELINK", link_text="About Us",
            final_urls=["https://example.com/about"], ctx=mock_ctx,
        )
        assert "SITELINK" in result

    def test_callout(self, mock_ctx):
        result = gads_create_ad_extension(
            customer_id="1234567890", campaign_id="111",
            extension_type="CALLOUT", callout_text="Free Shipping",
            ctx=mock_ctx,
        )
        assert "CALLOUT" in result
