"""Tests for status mutation tools (campaign, ad group, ad)."""

import pytest
from unittest.mock import MagicMock, patch
from google_ads_mcp.tools.mutations.campaign_ops import (
    gads_set_campaign_status,
    gads_update_campaign,
)
from google_ads_mcp.tools.mutations.ad_group_ops import gads_set_ad_group_status
from google_ads_mcp.tools.mutations.ad_ops import gads_set_ad_status


@pytest.fixture
def mock_ctx():
    """Create a mock MCP context with client wrapper."""
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()  # raw GoogleAdsClient
    wrapper.mutate.return_value = MagicMock(
        mutate_operation_responses=[MagicMock()]
    )
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


class TestSetCampaignStatus:
    def test_pause_campaign(self, mock_ctx):
        result = gads_set_campaign_status(
            customer_id="1234567890", campaign_id="111",
            status="pause", ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "111" in result
        assert "pause" in result.lower() or "PAUSED" in result

    def test_enable_campaign(self, mock_ctx):
        result = gads_set_campaign_status(
            customer_id="1234567890", campaign_id="111",
            status="enable", ctx=mock_ctx,
        )
        assert isinstance(result, str)
        assert "ENABLED" in result

    def test_remove_campaign(self, mock_ctx):
        result = gads_set_campaign_status(
            customer_id="1234567890", campaign_id="111",
            status="remove", ctx=mock_ctx,
        )
        assert isinstance(result, str)
        assert "REMOVED" in result

    def test_invalid_status_rejected(self):
        """Invalid status values should be rejected by the Pydantic model."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_set_campaign_status(
                customer_id="1234567890", campaign_id="111",
                status="invalid", ctx=ctx,
            )

    def test_invalid_customer_id_rejected(self):
        """Invalid customer IDs should be rejected by the Pydantic model."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_set_campaign_status(
                customer_id="abc", campaign_id="111",
                status="pause", ctx=ctx,
            )


class TestUpdateCampaign:
    def test_update_name(self, mock_ctx):
        result = gads_update_campaign(
            customer_id="1234567890", campaign_id="111",
            name="Updated Name", ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert isinstance(result, str)
        assert "name" in result

    def test_update_dates(self, mock_ctx):
        result = gads_update_campaign(
            customer_id="1234567890", campaign_id="111",
            start_date="2026-03-01", end_date="2026-12-31", ctx=mock_ctx,
        )
        assert isinstance(result, str)
        assert "start_date" in result
        assert "end_date" in result

    def test_update_name_and_dates(self, mock_ctx):
        result = gads_update_campaign(
            customer_id="1234567890", campaign_id="111",
            name="New Name", start_date="2026-03-01", end_date="2026-12-31",
            ctx=mock_ctx,
        )
        assert "name" in result
        assert "start_date" in result
        assert "end_date" in result

    def test_no_fields_raises(self):
        """Must provide at least one field to update."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_update_campaign(
                customer_id="1234567890", campaign_id="111",
                ctx=ctx,
            )

    def test_invalid_date_format_raises(self):
        """Invalid date format should be rejected."""
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_update_campaign(
                customer_id="1234567890", campaign_id="111",
                start_date="01-03-2026", ctx=ctx,
            )


class TestSetAdGroupStatus:
    def test_pause_ad_group(self, mock_ctx):
        result = gads_set_ad_group_status(
            customer_id="1234567890", ad_group_id="222",
            status="pause", ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "222" in result
        assert "PAUSED" in result

    def test_enable_ad_group(self, mock_ctx):
        result = gads_set_ad_group_status(
            customer_id="1234567890", ad_group_id="222",
            status="enable", ctx=mock_ctx,
        )
        assert "ENABLED" in result

    def test_remove_ad_group(self, mock_ctx):
        result = gads_set_ad_group_status(
            customer_id="1234567890", ad_group_id="222",
            status="remove", ctx=mock_ctx,
        )
        assert "REMOVED" in result


class TestSetAdStatus:
    def test_pause_ad(self, mock_ctx):
        result = gads_set_ad_status(
            customer_id="1234567890", ad_group_id="222",
            ad_id="333", status="pause", ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "333" in result
        assert "PAUSED" in result

    def test_enable_ad(self, mock_ctx):
        result = gads_set_ad_status(
            customer_id="1234567890", ad_group_id="222",
            ad_id="333", status="enable", ctx=mock_ctx,
        )
        assert "ENABLED" in result

    def test_remove_ad(self, mock_ctx):
        result = gads_set_ad_status(
            customer_id="1234567890", ad_group_id="222",
            ad_id="333", status="remove", ctx=mock_ctx,
        )
        assert "REMOVED" in result
