"""Tests for Phase 5 asset operation builders."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.builders.operations import (
    build_create_asset_operation,
    build_create_asset_group_operation,
    build_asset_group_asset_operations,
    ASSET_TYPE_TO_ENUM,
    ASSET_FIELD_TYPE_TO_ENUM,
)


@pytest.fixture
def mock_google_client():
    client = MagicMock()
    client.get_type.side_effect = lambda name: MagicMock()
    return client


class TestAssetTypeToEnum:
    def test_text(self):
        assert ASSET_TYPE_TO_ENUM["TEXT"] == 4

    def test_image(self):
        assert ASSET_TYPE_TO_ENUM["IMAGE"] == 5

    def test_youtube_video(self):
        assert ASSET_TYPE_TO_ENUM["YOUTUBE_VIDEO"] == 2


class TestAssetFieldTypeToEnum:
    def test_headline(self):
        assert ASSET_FIELD_TYPE_TO_ENUM["HEADLINE"] == 2

    def test_marketing_image(self):
        assert ASSET_FIELD_TYPE_TO_ENUM["MARKETING_IMAGE"] == 4

    def test_logo(self):
        assert ASSET_FIELD_TYPE_TO_ENUM["LOGO"] == 5


class TestBuildCreateAssetOperation:
    def test_text_asset(self, mock_google_client):
        op = build_create_asset_operation(
            mock_google_client, "1234567890",
            asset_type="TEXT", name="Headline Asset",
            text_content="Best shoes online",
        )
        assert op is not None

    def test_youtube_video_asset(self, mock_google_client):
        op = build_create_asset_operation(
            mock_google_client, "1234567890",
            asset_type="YOUTUBE_VIDEO", name="Video Asset",
            youtube_video_id="dQw4w9WgXcQ",
        )
        assert op is not None

    def test_image_asset(self, mock_google_client):
        op = build_create_asset_operation(
            mock_google_client, "1234567890",
            asset_type="IMAGE", name="Image Asset",
            image_data=b"\x89PNG\r\n",
        )
        assert op is not None

    def test_call_to_action_asset(self, mock_google_client):
        op = build_create_asset_operation(
            mock_google_client, "1234567890",
            asset_type="CALL_TO_ACTION", name="CTA",
            call_to_action_type="LEARN_MORE",
        )
        assert op is not None


class TestBuildCreateAssetGroupOperation:
    def test_basic(self, mock_google_client):
        op = build_create_asset_group_operation(
            mock_google_client, "1234567890",
            campaign_id="111", name="Asset Group 1",
            final_urls=["https://example.com"],
        )
        assert op is not None

    def test_with_optional_fields(self, mock_google_client):
        op = build_create_asset_group_operation(
            mock_google_client, "1234567890",
            campaign_id="111", name="Full Group",
            final_urls=["https://example.com"],
            final_mobile_urls=["https://m.example.com"],
            path1="shoes", path2="sale",
        )
        assert op is not None


class TestBuildAssetGroupAssetOperations:
    def test_single_asset(self, mock_google_client):
        ops = build_asset_group_asset_operations(
            mock_google_client, "1234567890",
            asset_group_id="555",
            assets=[{"asset_id": "100", "field_type": "HEADLINE"}],
        )
        assert isinstance(ops, list)
        assert len(ops) == 1

    def test_multiple_assets(self, mock_google_client):
        ops = build_asset_group_asset_operations(
            mock_google_client, "1234567890",
            asset_group_id="555",
            assets=[
                {"asset_id": "100", "field_type": "HEADLINE"},
                {"asset_id": "200", "field_type": "DESCRIPTION"},
                {"asset_id": "300", "field_type": "MARKETING_IMAGE"},
            ],
        )
        assert len(ops) == 3
