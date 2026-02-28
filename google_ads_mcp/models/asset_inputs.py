"""Input models for Google Ads MCP Phase 5 asset tools."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, model_validator

from google_ads_mcp.models.common import (
    AssetFieldType,
    AssetType,
    CustomerIdMixin,
    ListingGroupDimension,
    VideoAdFormat,
)


class CreateAssetInput(CustomerIdMixin):
    """Input for gads_create_asset tool."""

    asset_type: AssetType = Field(..., description="Asset type.")
    name: str = Field(..., description="Asset name.")
    # TEXT fields
    text_content: str | None = Field(default=None, description="Text content (required for TEXT).")
    # IMAGE fields
    image_url: str | None = Field(default=None, description="Public HTTPS image URL (required for IMAGE).")
    # YOUTUBE_VIDEO fields
    youtube_video_id: str | None = Field(default=None, description="YouTube video ID, 11 chars (required for YOUTUBE_VIDEO).")
    # CALL_TO_ACTION fields
    call_to_action_type: str | None = Field(default=None, description="CTA type e.g. LEARN_MORE, SHOP_NOW (required for CALL_TO_ACTION).")

    @model_validator(mode="after")
    def validate_type_specific_fields(self) -> "CreateAssetInput":
        t = self.asset_type
        if t == AssetType.TEXT:
            if not self.text_content:
                raise ValueError("text_content is required for TEXT assets")
        elif t == AssetType.IMAGE:
            if not self.image_url:
                raise ValueError("image_url is required for IMAGE assets")
            if not self.image_url.startswith("https://"):
                raise ValueError("image_url must be an HTTPS URL")
        elif t == AssetType.YOUTUBE_VIDEO:
            if not self.youtube_video_id:
                raise ValueError("youtube_video_id is required for YOUTUBE_VIDEO assets")
            if not re.match(r"^[a-zA-Z0-9_-]{11}$", self.youtube_video_id):
                raise ValueError("youtube_video_id must be exactly 11 alphanumeric characters")
        elif t == AssetType.CALL_TO_ACTION:
            if not self.call_to_action_type:
                raise ValueError("call_to_action_type is required for CALL_TO_ACTION assets")
        return self


class CreateAssetGroupInput(CustomerIdMixin):
    """Input for gads_create_asset_group tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    name: str = Field(..., description="Asset group name.")
    final_urls: list[str] = Field(..., min_length=1, description="Final URLs (min 1).")
    final_mobile_urls: list[str] | None = Field(default=None, description="Mobile-specific final URLs.")
    path1: str | None = Field(default=None, description="Display URL path 1.")
    path2: str | None = Field(default=None, description="Display URL path 2.")


class AssetAssignment(BaseModel):
    """A single asset-to-field-type assignment."""

    asset_id: str = Field(..., description="Asset ID.")
    field_type: AssetFieldType = Field(..., description="Field type for this asset.")


class AddAssetGroupAssetsInput(CustomerIdMixin):
    """Input for gads_add_asset_group_assets tool."""

    asset_group_id: str = Field(..., description="Asset group ID.")
    assets: list[AssetAssignment] = Field(
        ..., min_length=1, max_length=20,
        description="Assets to link (min 1, max 20).",
    )


class CreateResponsiveDisplayAdInput(CustomerIdMixin):
    """Input for gads_create_responsive_display_ad tool."""

    ad_group_id: str = Field(..., description="Ad group ID.")
    marketing_image_asset_ids: list[str] = Field(
        ..., min_length=1, description="Marketing image asset IDs (min 1)."
    )
    headlines: list[str] = Field(
        ..., min_length=1, max_length=5, description="Headlines (min 1, max 5)."
    )
    long_headline: str = Field(..., description="Long headline.")
    descriptions: list[str] = Field(
        ..., min_length=1, max_length=5, description="Descriptions (min 1, max 5)."
    )
    business_name: str = Field(..., description="Business name.")
    final_urls: list[str] = Field(..., min_length=1, description="Final URLs.")
    logo_asset_ids: list[str] | None = Field(default=None, description="Logo asset IDs.")
    square_image_asset_ids: list[str] | None = Field(default=None, description="Square image asset IDs.")


class CreateVideoAdInput(CustomerIdMixin):
    """Input for gads_create_video_ad tool."""

    ad_group_id: str = Field(..., description="Ad group ID.")
    video_asset_id: str = Field(..., description="Video asset ID (YouTube video).")
    ad_format: VideoAdFormat = Field(..., description="Video ad format.")
    headline: str | None = Field(default=None, description="Headline (required for IN_STREAM).")
    description: str | None = Field(default=None, description="Description.")
    final_url: str | None = Field(default=None, description="Final URL (required for IN_STREAM).")
    display_url: str | None = Field(default=None, description="Display URL.")
    companion_banner_asset_id: str | None = Field(default=None, description="Companion banner asset ID.")

    @model_validator(mode="after")
    def validate_format_requirements(self) -> "CreateVideoAdInput":
        if self.ad_format in (VideoAdFormat.IN_STREAM_SKIPPABLE, VideoAdFormat.IN_STREAM_NON_SKIPPABLE):
            if not self.headline:
                raise ValueError("headline is required for IN_STREAM ad formats")
            if not self.final_url:
                raise ValueError("final_url is required for IN_STREAM ad formats")
        return self


class SetListingGroupFilterInput(CustomerIdMixin):
    """Input for gads_set_listing_group_filter tool."""

    asset_group_id: str = Field(..., description="Asset group ID.")
    filter_type: str = Field(..., description="Filter type: UNIT_INCLUDED, UNIT_EXCLUDED, or SUBDIVISION.")
    dimension: ListingGroupDimension = Field(..., description="Listing group dimension.")
    value: str | None = Field(default=None, description="Filter value (e.g. brand name).")
    parent_filter_id: str | None = Field(default=None, description="Parent filter ID for sub-filters.")


class LinkMerchantCenterInput(CustomerIdMixin):
    """Input for gads_link_merchant_center tool."""

    campaign_id: str = Field(..., description="Campaign ID.")
    merchant_id: str = Field(..., description="Merchant Center account ID.")
    feed_label: str | None = Field(default=None, description="Feed label.")
    sales_country: str | None = Field(default=None, description="Sales country code (e.g. US, IT).")


class CreateDemandGenAdInput(CustomerIdMixin):
    """Input for gads_create_demand_gen_ad tool."""

    ad_group_id: str = Field(..., description="Ad group ID.")
    headlines: list[str] = Field(
        ..., min_length=1, max_length=5, description="Headlines (min 1, max 5)."
    )
    descriptions: list[str] = Field(
        ..., min_length=1, max_length=5, description="Descriptions (min 1, max 5)."
    )
    marketing_image_asset_ids: list[str] = Field(
        ..., min_length=1, description="Marketing image asset IDs."
    )
    logo_asset_id: str = Field(..., description="Logo asset ID.")
    business_name: str = Field(..., description="Business name.")
    final_urls: list[str] = Field(..., min_length=1, description="Final URLs.")
    call_to_action: str | None = Field(default=None, description="CTA type e.g. SHOP_NOW, LEARN_MORE.")
