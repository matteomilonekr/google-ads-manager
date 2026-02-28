"""Tests for asset management tools."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.asset_ops import (
    gads_create_asset,
    gads_create_asset_group,
    gads_add_asset_group_assets,
)


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    response = MagicMock()
    response.mutate_operation_responses = [
        MagicMock(asset_result=MagicMock(resource_name="customers/1234567890/assets/12345")),
    ]
    wrapper.mutate.return_value = response
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


@pytest.fixture
def mock_ctx_asset_group():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    response = MagicMock()
    response.mutate_operation_responses = [
        MagicMock(asset_group_result=MagicMock(resource_name="customers/1234567890/assetGroups/555")),
    ]
    wrapper.mutate.return_value = response
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


@pytest.fixture
def mock_ctx_batch():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    response = MagicMock()
    response.mutate_operation_responses = [MagicMock(), MagicMock(), MagicMock()]
    wrapper.mutate.return_value = response
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


class TestCreateAsset:
    def test_text_asset(self, mock_ctx):
        result = gads_create_asset(
            customer_id="1234567890",
            asset_type="TEXT",
            name="My Headline",
            text_content="Best shoes online",
            ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "12345" in result
        assert "TEXT" in result

    def test_youtube_video_asset(self, mock_ctx):
        result = gads_create_asset(
            customer_id="1234567890",
            asset_type="YOUTUBE_VIDEO",
            name="Product Video",
            youtube_video_id="dQw4w9WgXcQ",
            ctx=mock_ctx,
        )
        assert "12345" in result

    def test_invalid_type(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_asset(
                customer_id="1234567890",
                asset_type="UNKNOWN",
                name="Bad",
                ctx=ctx,
            )


class TestCreateAssetGroup:
    def test_creates_asset_group(self, mock_ctx_asset_group):
        result = gads_create_asset_group(
            customer_id="1234567890",
            campaign_id="111",
            name="PMax Group 1",
            final_urls=["https://example.com"],
            ctx=mock_ctx_asset_group,
        )
        wrapper = mock_ctx_asset_group.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "555" in result
        assert "PMax Group 1" in result

    def test_with_optional_fields(self, mock_ctx_asset_group):
        result = gads_create_asset_group(
            customer_id="1234567890",
            campaign_id="111",
            name="Full Group",
            final_urls=["https://example.com"],
            final_mobile_urls=["https://m.example.com"],
            path1="shoes",
            path2="sale",
            ctx=mock_ctx_asset_group,
        )
        assert isinstance(result, str)


class TestAddAssetGroupAssets:
    def test_links_assets(self, mock_ctx_batch):
        result = gads_add_asset_group_assets(
            customer_id="1234567890",
            asset_group_id="555",
            asset_ids=["100", "200", "300"],
            field_types=["HEADLINE", "DESCRIPTION", "MARKETING_IMAGE"],
            ctx=mock_ctx_batch,
        )
        wrapper = mock_ctx_batch.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "3" in result

    def test_single_asset(self, mock_ctx):
        result = gads_add_asset_group_assets(
            customer_id="1234567890",
            asset_group_id="555",
            asset_ids=["100"],
            field_types=["HEADLINE"],
            ctx=mock_ctx,
        )
        assert "1" in result
