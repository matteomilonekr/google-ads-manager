"""Tests for Phase 5 ad creation operation builders."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.builders.operations import (
    build_responsive_display_ad_operation,
    build_video_ad_operation,
    build_demand_gen_ad_operation,
)


@pytest.fixture
def mock_google_client():
    client = MagicMock()
    client.get_type.side_effect = lambda name: MagicMock()
    return client


class TestBuildResponsiveDisplayAdOperation:
    def test_basic(self, mock_google_client):
        op = build_responsive_display_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            marketing_image_asset_ids=["100"],
            headlines=["Buy Now"],
            long_headline="Buy the best shoes online",
            descriptions=["Great deals"],
            business_name="Shoe Store",
            final_urls=["https://example.com"],
        )
        assert op is not None

    def test_with_logos_and_square_images(self, mock_google_client):
        op = build_responsive_display_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            marketing_image_asset_ids=["100", "101"],
            headlines=["H1", "H2"],
            long_headline="Long headline",
            descriptions=["D1", "D2"],
            business_name="Store",
            final_urls=["https://example.com"],
            logo_asset_ids=["300"],
            square_image_asset_ids=["400"],
        )
        assert op is not None


class TestBuildVideoAdOperation:
    def test_in_stream_skippable(self, mock_google_client):
        op = build_video_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            video_asset_id="vid_001",
            ad_format="IN_STREAM_SKIPPABLE",
            headline="Watch Now",
            final_url="https://example.com",
        )
        assert op is not None

    def test_bumper(self, mock_google_client):
        op = build_video_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            video_asset_id="vid_002",
            ad_format="BUMPER",
        )
        assert op is not None

    def test_video_responsive(self, mock_google_client):
        op = build_video_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            video_asset_id="vid_003",
            ad_format="VIDEO_RESPONSIVE",
            headline="Watch",
            description="Amazing video",
            final_url="https://example.com",
        )
        assert op is not None

    def test_with_companion_banner(self, mock_google_client):
        op = build_video_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            video_asset_id="vid_001",
            ad_format="IN_STREAM_SKIPPABLE",
            headline="Watch",
            final_url="https://example.com",
            companion_banner_asset_id="banner_001",
        )
        assert op is not None


class TestBuildDemandGenAdOperation:
    def test_basic(self, mock_google_client):
        op = build_demand_gen_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            headlines=["Discover More"],
            descriptions=["Amazing products"],
            marketing_image_asset_ids=["100"],
            logo_asset_id="200",
            business_name="My Store",
            final_urls=["https://example.com"],
        )
        assert op is not None

    def test_with_call_to_action(self, mock_google_client):
        op = build_demand_gen_ad_operation(
            mock_google_client, "1234567890",
            ad_group_id="222",
            headlines=["H1"],
            descriptions=["D1"],
            marketing_image_asset_ids=["100"],
            logo_asset_id="200",
            business_name="Store",
            final_urls=["https://example.com"],
            call_to_action="SHOP_NOW",
        )
        assert op is not None
