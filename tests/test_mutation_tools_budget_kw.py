"""Tests for budget and negative keyword mutation tools."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.budget_ops import gads_update_budget
from google_ads_mcp.tools.mutations.keyword_ops import gads_add_negative_keywords


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


class TestUpdateBudget:
    def test_update_budget(self, mock_ctx):
        result = gads_update_budget(
            customer_id="1234567890", budget_id="444",
            amount_micros=10_000_000, ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "444" in result
        assert "10.00" in result

    def test_budget_shows_currency(self, mock_ctx):
        result = gads_update_budget(
            customer_id="1234567890", budget_id="444",
            amount_micros=5_500_000, ctx=mock_ctx,
        )
        assert "5.50" in result

    def test_invalid_customer_id_rejected(self):
        """Invalid customer IDs should be rejected by the Pydantic model."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_update_budget(
                customer_id="bad", budget_id="444",
                amount_micros=10_000_000, ctx=ctx,
            )

    def test_zero_amount_rejected(self):
        """Budget amount must be positive."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_update_budget(
                customer_id="1234567890", budget_id="444",
                amount_micros=0, ctx=ctx,
            )

    def test_negative_amount_rejected(self):
        """Budget amount must be positive."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_update_budget(
                customer_id="1234567890", budget_id="444",
                amount_micros=-1_000_000, ctx=ctx,
            )


class TestAddNegativeKeywords:
    def test_campaign_level(self, mock_ctx):
        result = gads_add_negative_keywords(
            customer_id="1234567890", level="campaign",
            campaign_id="111", keywords=["free", "cheap"],
            match_type="exact", ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "2" in result  # 2 keywords added

    def test_ad_group_level(self, mock_ctx):
        result = gads_add_negative_keywords(
            customer_id="1234567890", level="ad_group",
            ad_group_id="222", keywords=["discount"],
            ctx=mock_ctx,
        )
        assert "1" in result

    def test_phrase_match_type(self, mock_ctx):
        result = gads_add_negative_keywords(
            customer_id="1234567890", level="campaign",
            campaign_id="111", keywords=["free shipping"],
            match_type="phrase", ctx=mock_ctx,
        )
        assert "phrase" in result

    def test_broad_match_type(self, mock_ctx):
        result = gads_add_negative_keywords(
            customer_id="1234567890", level="campaign",
            campaign_id="111", keywords=["free"],
            match_type="broad", ctx=mock_ctx,
        )
        assert "broad" in result

    def test_campaign_level_without_campaign_id_rejected(self):
        """Campaign level requires campaign_id."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_add_negative_keywords(
                customer_id="1234567890", level="campaign",
                keywords=["free"], ctx=ctx,
            )

    def test_ad_group_level_without_ad_group_id_rejected(self):
        """Ad group level requires ad_group_id."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_add_negative_keywords(
                customer_id="1234567890", level="ad_group",
                keywords=["free"], ctx=ctx,
            )

    def test_keywords_in_response(self, mock_ctx):
        result = gads_add_negative_keywords(
            customer_id="1234567890", level="campaign",
            campaign_id="111", keywords=["free", "cheap", "trial"],
            match_type="exact", ctx=mock_ctx,
        )
        assert "free" in result
        assert "cheap" in result
        assert "trial" in result

    def test_invalid_customer_id_rejected(self):
        """Invalid customer IDs should be rejected."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_add_negative_keywords(
                customer_id="bad", level="campaign",
                campaign_id="111", keywords=["free"], ctx=ctx,
            )
