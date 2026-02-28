"""Tests for targeting mutation tools (location, language)."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.targeting_ops import (
    gads_set_location_targeting,
    gads_set_language_targeting,
)


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


class TestSetLocationTargeting:
    def test_include_locations(self, mock_ctx):
        result = gads_set_location_targeting(
            customer_id="1234567890", campaign_id="111",
            location_ids=[2380, 2826], exclude=False, ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "2" in result  # 2 locations

    def test_exclude_locations(self, mock_ctx):
        result = gads_set_location_targeting(
            customer_id="1234567890", campaign_id="111",
            location_ids=[2380], exclude=True, ctx=mock_ctx,
        )
        assert "exclud" in result.lower() or "esclus" in result.lower()

    def test_single_location(self, mock_ctx):
        result = gads_set_location_targeting(
            customer_id="1234567890", campaign_id="111",
            location_ids=[2840], exclude=False, ctx=mock_ctx,
        )
        assert "1" in result
        assert "111" in result

    def test_campaign_id_in_response(self, mock_ctx):
        result = gads_set_location_targeting(
            customer_id="1234567890", campaign_id="555",
            location_ids=[2380], exclude=False, ctx=mock_ctx,
        )
        assert "555" in result

    def test_invalid_customer_id_rejected(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_set_location_targeting(
                customer_id="bad", campaign_id="111",
                location_ids=[2380], ctx=ctx,
            )

    def test_empty_location_ids_rejected(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_set_location_targeting(
                customer_id="1234567890", campaign_id="111",
                location_ids=[], ctx=ctx,
            )


class TestSetLanguageTargeting:
    def test_set_languages(self, mock_ctx):
        result = gads_set_language_targeting(
            customer_id="1234567890", campaign_id="111",
            language_ids=[1000, 1004], ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "2" in result  # 2 languages

    def test_single_language(self, mock_ctx):
        result = gads_set_language_targeting(
            customer_id="1234567890", campaign_id="111",
            language_ids=[1000], ctx=mock_ctx,
        )
        assert "1" in result
        assert "111" in result

    def test_campaign_id_in_response(self, mock_ctx):
        result = gads_set_language_targeting(
            customer_id="1234567890", campaign_id="999",
            language_ids=[1000], ctx=mock_ctx,
        )
        assert "999" in result

    def test_invalid_customer_id_rejected(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_set_language_targeting(
                customer_id="bad", campaign_id="111",
                language_ids=[1000], ctx=ctx,
            )

    def test_empty_language_ids_rejected(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_set_language_targeting(
                customer_id="1234567890", campaign_id="111",
                language_ids=[], ctx=ctx,
            )
