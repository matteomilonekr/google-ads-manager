"""Tests for display, video, and demand gen ad tools."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.creation_ops import (
    gads_create_responsive_display_ad,
    gads_create_demand_gen_ad,
)
from google_ads_mcp.tools.mutations.video_ops import gads_create_video_ad


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    response = MagicMock()
    response.mutate_operation_responses = [
        MagicMock(ad_group_ad_result=MagicMock(
            resource_name="customers/1234567890/adGroupAds/222~777"
        )),
    ]
    wrapper.mutate.return_value = response
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


class TestCreateResponsiveDisplayAd:
    def test_creates_ad(self, mock_ctx):
        result = gads_create_responsive_display_ad(
            customer_id="1234567890",
            ad_group_id="222",
            marketing_image_asset_ids=["100"],
            headlines=["Buy Now"],
            long_headline="Buy the best shoes online today",
            descriptions=["Great deals on shoes"],
            business_name="Shoe Store",
            final_urls=["https://example.com"],
            ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "777" in result or "222~777" in result

    def test_with_logos(self, mock_ctx):
        result = gads_create_responsive_display_ad(
            customer_id="1234567890",
            ad_group_id="222",
            marketing_image_asset_ids=["100"],
            headlines=["H1"],
            long_headline="Long",
            descriptions=["D1"],
            business_name="Store",
            final_urls=["https://example.com"],
            logo_asset_ids=["300"],
            square_image_asset_ids=["400"],
            ctx=mock_ctx,
        )
        assert isinstance(result, str)


class TestCreateVideoAd:
    def test_in_stream(self, mock_ctx):
        result = gads_create_video_ad(
            customer_id="1234567890",
            ad_group_id="222",
            video_asset_id="vid_001",
            ad_format="IN_STREAM_SKIPPABLE",
            headline="Watch Now",
            final_url="https://example.com",
            ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "IN_STREAM_SKIPPABLE" in result

    def test_bumper(self, mock_ctx):
        result = gads_create_video_ad(
            customer_id="1234567890",
            ad_group_id="222",
            video_asset_id="vid_002",
            ad_format="BUMPER",
            ctx=mock_ctx,
        )
        assert "BUMPER" in result

    def test_video_responsive(self, mock_ctx):
        result = gads_create_video_ad(
            customer_id="1234567890",
            ad_group_id="222",
            video_asset_id="vid_003",
            ad_format="VIDEO_RESPONSIVE",
            headline="Watch",
            description="Amazing",
            final_url="https://example.com",
            ctx=mock_ctx,
        )
        assert "VIDEO_RESPONSIVE" in result


class TestCreateDemandGenAd:
    def test_creates_ad(self, mock_ctx):
        result = gads_create_demand_gen_ad(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["Discover More"],
            descriptions=["Amazing products"],
            marketing_image_asset_ids=["100"],
            logo_asset_id="200",
            business_name="My Store",
            final_urls=["https://example.com"],
            ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "Demand Gen" in result or "demand_gen" in result.lower() or "222" in result

    def test_with_cta(self, mock_ctx):
        result = gads_create_demand_gen_ad(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["H1"],
            descriptions=["D1"],
            marketing_image_asset_ids=["100"],
            logo_asset_id="200",
            business_name="Store",
            final_urls=["https://example.com"],
            call_to_action="SHOP_NOW",
            ctx=mock_ctx,
        )
        assert isinstance(result, str)
