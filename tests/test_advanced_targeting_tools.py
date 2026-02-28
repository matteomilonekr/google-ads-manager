"""Tests for device, demographic, and audience targeting tools."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.targeting_ops import (
    gads_set_device_targeting,
    gads_set_demographic_targeting,
    gads_create_audience_segment,
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


class TestSetDeviceTargeting:
    def test_mobile_boost(self, mock_ctx):
        result = gads_set_device_targeting(
            customer_id="1234567890", campaign_id="111",
            device="MOBILE", bid_modifier=1.5, ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "MOBILE" in result

    def test_exclude_tablet(self, mock_ctx):
        result = gads_set_device_targeting(
            customer_id="1234567890", campaign_id="111",
            device="TABLET", bid_modifier=0.0, ctx=mock_ctx,
        )
        assert "TABLET" in result


class TestSetDemographicTargeting:
    def test_age_targeting(self, mock_ctx):
        result = gads_set_demographic_targeting(
            customer_id="1234567890", campaign_id="111",
            dimension="AGE", values=["AGE_RANGE_25_34", "AGE_RANGE_35_44"],
            ctx=mock_ctx,
        )
        assert "2" in result

    def test_with_bid_modifier(self, mock_ctx):
        result = gads_set_demographic_targeting(
            customer_id="1234567890", campaign_id="111",
            dimension="GENDER", values=["MALE"],
            bid_modifier=1.2, ctx=mock_ctx,
        )
        assert isinstance(result, str)


class TestCreateAudienceSegment:
    def test_in_market(self, mock_ctx):
        result = gads_create_audience_segment(
            customer_id="1234567890", campaign_id="111",
            audience_type="IN_MARKET", audience_id="123456",
            ctx=mock_ctx,
        )
        assert "IN_MARKET" in result

    def test_remarketing_with_modifier(self, mock_ctx):
        result = gads_create_audience_segment(
            customer_id="1234567890", campaign_id="111",
            audience_type="REMARKETING", audience_id="789",
            bid_modifier=1.5, ctx=mock_ctx,
        )
        assert "REMARKETING" in result
