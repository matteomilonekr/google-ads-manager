"""Tests for Phase 5 asset input models and enums."""

import pytest
from pydantic import ValidationError
from google_ads_mcp.models.common import (
    AssetType,
    AssetFieldType,
    VideoAdFormat,
    ListingGroupDimension,
)


class TestAssetTypeEnum:
    def test_text(self):
        assert AssetType.TEXT == "TEXT"

    def test_image(self):
        assert AssetType.IMAGE == "IMAGE"

    def test_youtube_video(self):
        assert AssetType.YOUTUBE_VIDEO == "YOUTUBE_VIDEO"

    def test_all_values(self):
        assert len(AssetType) == 5


class TestAssetFieldTypeEnum:
    def test_headline(self):
        assert AssetFieldType.HEADLINE == "HEADLINE"

    def test_marketing_image(self):
        assert AssetFieldType.MARKETING_IMAGE == "MARKETING_IMAGE"

    def test_all_values(self):
        assert len(AssetFieldType) == 10


class TestVideoAdFormatEnum:
    def test_in_stream_skippable(self):
        assert VideoAdFormat.IN_STREAM_SKIPPABLE == "IN_STREAM_SKIPPABLE"

    def test_bumper(self):
        assert VideoAdFormat.BUMPER == "BUMPER"

    def test_all_values(self):
        assert len(VideoAdFormat) == 4


class TestListingGroupDimensionEnum:
    def test_brand(self):
        assert ListingGroupDimension.BRAND == "BRAND"

    def test_category_l1(self):
        assert ListingGroupDimension.CATEGORY_L1 == "CATEGORY_L1"

    def test_all_values(self):
        assert len(ListingGroupDimension) == 9


from google_ads_mcp.models.asset_inputs import (
    CreateAssetInput,
    CreateAssetGroupInput,
    AssetAssignment,
    AddAssetGroupAssetsInput,
    CreateResponsiveDisplayAdInput,
    CreateVideoAdInput,
    SetListingGroupFilterInput,
    LinkMerchantCenterInput,
    CreateDemandGenAdInput,
)


class TestCreateAssetInput:
    def test_valid_text_asset(self):
        inp = CreateAssetInput(
            customer_id="1234567890",
            asset_type="TEXT",
            name="My Headline",
            text_content="Best shoes online",
        )
        assert inp.asset_type == AssetType.TEXT
        assert inp.text_content == "Best shoes online"

    def test_valid_image_asset(self):
        inp = CreateAssetInput(
            customer_id="1234567890",
            asset_type="IMAGE",
            name="Banner Image",
            image_url="https://example.com/banner.png",
        )
        assert inp.image_url == "https://example.com/banner.png"

    def test_valid_youtube_video_asset(self):
        inp = CreateAssetInput(
            customer_id="1234567890",
            asset_type="YOUTUBE_VIDEO",
            name="Product Video",
            youtube_video_id="dQw4w9WgXcQ",
        )
        assert inp.youtube_video_id == "dQw4w9WgXcQ"

    def test_text_requires_text_content(self):
        with pytest.raises(ValidationError, match="text_content"):
            CreateAssetInput(
                customer_id="1234567890",
                asset_type="TEXT",
                name="Missing Content",
            )

    def test_image_requires_image_url(self):
        with pytest.raises(ValidationError, match="image_url"):
            CreateAssetInput(
                customer_id="1234567890",
                asset_type="IMAGE",
                name="Missing URL",
            )

    def test_image_url_must_be_https(self):
        with pytest.raises(ValidationError, match="(?i)https"):
            CreateAssetInput(
                customer_id="1234567890",
                asset_type="IMAGE",
                name="HTTP URL",
                image_url="http://example.com/banner.png",
            )

    def test_youtube_requires_video_id(self):
        with pytest.raises(ValidationError, match="youtube_video_id"):
            CreateAssetInput(
                customer_id="1234567890",
                asset_type="YOUTUBE_VIDEO",
                name="Missing Video ID",
            )

    def test_youtube_video_id_format(self):
        with pytest.raises(ValidationError, match="(?i)11"):
            CreateAssetInput(
                customer_id="1234567890",
                asset_type="YOUTUBE_VIDEO",
                name="Bad ID",
                youtube_video_id="short",
            )

    def test_invalid_asset_type(self):
        with pytest.raises(ValidationError):
            CreateAssetInput(
                customer_id="1234567890",
                asset_type="UNKNOWN",
                name="Bad Type",
            )

    def test_call_to_action_asset(self):
        inp = CreateAssetInput(
            customer_id="1234567890",
            asset_type="CALL_TO_ACTION",
            name="CTA",
            call_to_action_type="LEARN_MORE",
        )
        assert inp.call_to_action_type == "LEARN_MORE"

    def test_call_to_action_requires_type(self):
        with pytest.raises(ValidationError, match="call_to_action_type"):
            CreateAssetInput(
                customer_id="1234567890",
                asset_type="CALL_TO_ACTION",
                name="Missing CTA Type",
            )


class TestCreateAssetGroupInput:
    def test_valid(self):
        inp = CreateAssetGroupInput(
            customer_id="1234567890",
            campaign_id="111",
            name="PMax Asset Group 1",
            final_urls=["https://example.com"],
        )
        assert inp.name == "PMax Asset Group 1"
        assert inp.final_urls == ["https://example.com"]

    def test_requires_final_urls(self):
        with pytest.raises(ValidationError, match="final_urls"):
            CreateAssetGroupInput(
                customer_id="1234567890",
                campaign_id="111",
                name="Missing URLs",
                final_urls=[],
            )

    def test_with_optional_fields(self):
        inp = CreateAssetGroupInput(
            customer_id="1234567890",
            campaign_id="111",
            name="Full",
            final_urls=["https://example.com"],
            final_mobile_urls=["https://m.example.com"],
            path1="shoes",
            path2="sale",
        )
        assert inp.path1 == "shoes"


class TestAssetAssignment:
    def test_valid(self):
        a = AssetAssignment(asset_id="12345", field_type="HEADLINE")
        assert a.asset_id == "12345"
        assert a.field_type == AssetFieldType.HEADLINE

    def test_invalid_field_type(self):
        with pytest.raises(ValidationError):
            AssetAssignment(asset_id="12345", field_type="INVALID")


class TestAddAssetGroupAssetsInput:
    def test_valid(self):
        inp = AddAssetGroupAssetsInput(
            customer_id="1234567890",
            asset_group_id="555",
            assets=[
                {"asset_id": "100", "field_type": "HEADLINE"},
                {"asset_id": "200", "field_type": "MARKETING_IMAGE"},
            ],
        )
        assert len(inp.assets) == 2

    def test_min_one_asset(self):
        with pytest.raises(ValidationError):
            AddAssetGroupAssetsInput(
                customer_id="1234567890",
                asset_group_id="555",
                assets=[],
            )

    def test_max_twenty_assets(self):
        with pytest.raises(ValidationError):
            AddAssetGroupAssetsInput(
                customer_id="1234567890",
                asset_group_id="555",
                assets=[{"asset_id": str(i), "field_type": "HEADLINE"} for i in range(21)],
            )


class TestCreateResponsiveDisplayAdInput:
    def test_valid(self):
        inp = CreateResponsiveDisplayAdInput(
            customer_id="1234567890",
            ad_group_id="222",
            marketing_image_asset_ids=["100"],
            headlines=["Buy Now"],
            long_headline="Buy the best shoes online today",
            descriptions=["Great deals on shoes"],
            business_name="Shoe Store",
            final_urls=["https://example.com"],
        )
        assert inp.long_headline == "Buy the best shoes online today"

    def test_requires_marketing_images(self):
        with pytest.raises(ValidationError):
            CreateResponsiveDisplayAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                marketing_image_asset_ids=[],
                headlines=["H1"],
                long_headline="Long H1",
                descriptions=["D1"],
                business_name="Biz",
                final_urls=["https://example.com"],
            )

    def test_max_five_headlines(self):
        with pytest.raises(ValidationError):
            CreateResponsiveDisplayAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                marketing_image_asset_ids=["100"],
                headlines=["H1", "H2", "H3", "H4", "H5", "H6"],
                long_headline="Long",
                descriptions=["D1"],
                business_name="Biz",
                final_urls=["https://example.com"],
            )


class TestCreateVideoAdInput:
    def test_valid_in_stream(self):
        inp = CreateVideoAdInput(
            customer_id="1234567890",
            ad_group_id="222",
            video_asset_id="vid_001",
            ad_format="IN_STREAM_SKIPPABLE",
            headline="Watch Now",
            final_url="https://example.com",
        )
        assert inp.ad_format == VideoAdFormat.IN_STREAM_SKIPPABLE

    def test_valid_bumper(self):
        inp = CreateVideoAdInput(
            customer_id="1234567890",
            ad_group_id="222",
            video_asset_id="vid_002",
            ad_format="BUMPER",
        )
        assert inp.ad_format == VideoAdFormat.BUMPER

    def test_in_stream_requires_headline(self):
        with pytest.raises(ValidationError, match="headline"):
            CreateVideoAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                video_asset_id="vid_001",
                ad_format="IN_STREAM_SKIPPABLE",
                final_url="https://example.com",
            )

    def test_in_stream_requires_final_url(self):
        with pytest.raises(ValidationError, match="final_url"):
            CreateVideoAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                video_asset_id="vid_001",
                ad_format="IN_STREAM_SKIPPABLE",
                headline="Watch",
            )


class TestSetListingGroupFilterInput:
    def test_valid_unit_included(self):
        inp = SetListingGroupFilterInput(
            customer_id="1234567890",
            asset_group_id="555",
            filter_type="UNIT_INCLUDED",
            dimension="BRAND",
            value="Nike",
        )
        assert inp.filter_type == "UNIT_INCLUDED"

    def test_valid_subdivision(self):
        inp = SetListingGroupFilterInput(
            customer_id="1234567890",
            asset_group_id="555",
            filter_type="SUBDIVISION",
            dimension="CATEGORY_L1",
        )
        assert inp.dimension == ListingGroupDimension.CATEGORY_L1


class TestLinkMerchantCenterInput:
    def test_valid(self):
        inp = LinkMerchantCenterInput(
            customer_id="1234567890",
            campaign_id="111",
            merchant_id="12345678",
        )
        assert inp.merchant_id == "12345678"

    def test_with_optional_fields(self):
        inp = LinkMerchantCenterInput(
            customer_id="1234567890",
            campaign_id="111",
            merchant_id="12345678",
            feed_label="online",
            sales_country="US",
        )
        assert inp.feed_label == "online"


class TestCreateDemandGenAdInput:
    def test_valid(self):
        inp = CreateDemandGenAdInput(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["Discover More"],
            descriptions=["Amazing products"],
            marketing_image_asset_ids=["100"],
            logo_asset_id="200",
            business_name="My Store",
            final_urls=["https://example.com"],
        )
        assert inp.business_name == "My Store"

    def test_requires_headlines(self):
        with pytest.raises(ValidationError):
            CreateDemandGenAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=[],
                descriptions=["D1"],
                marketing_image_asset_ids=["100"],
                logo_asset_id="200",
                business_name="Biz",
                final_urls=["https://example.com"],
            )

    def test_max_five_headlines(self):
        with pytest.raises(ValidationError):
            CreateDemandGenAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=["H1", "H2", "H3", "H4", "H5", "H6"],
                descriptions=["D1"],
                marketing_image_asset_ids=["100"],
                logo_asset_id="200",
                business_name="Biz",
                final_urls=["https://example.com"],
            )

    def test_with_call_to_action(self):
        inp = CreateDemandGenAdInput(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["H1"],
            descriptions=["D1"],
            marketing_image_asset_ids=["100"],
            logo_asset_id="200",
            business_name="Biz",
            final_urls=["https://example.com"],
            call_to_action="SHOP_NOW",
        )
        assert inp.call_to_action == "SHOP_NOW"
