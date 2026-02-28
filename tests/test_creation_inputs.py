"""Tests for Phase 4 creation input models."""

import pytest
from pydantic import ValidationError
from google_ads_mcp.models.creation_inputs import (
    CreateCampaignInput,
    CreateAdGroupInput,
    CreateResponsiveSearchAdInput,
    AddKeywordsInput,
    SetBiddingStrategyInput,
    UpdateKeywordInput,
    CreateAdExtensionInput,
    SetDeviceTargetingInput,
    SetDemographicTargetingInput,
    CreateAudienceSegmentInput,
)
from google_ads_mcp.models.common import (
    CampaignType,
    BiddingStrategyType,
    AdGroupType,
    ExtensionType,
    DeviceType,
    DemographicDimension,
    AudienceType,
    MatchType,
    StatusAction,
)


class TestCreateCampaignInput:
    def test_valid_search(self):
        inp = CreateCampaignInput(
            customer_id="123-456-7890",
            name="My Search Campaign",
            campaign_type="SEARCH",
            bidding_strategy_type="MANUAL_CPC",
            budget_amount_micros=10_000_000,
        )
        assert inp.customer_id == "1234567890"
        assert inp.campaign_type == CampaignType.SEARCH
        assert inp.bidding_strategy_type == BiddingStrategyType.MANUAL_CPC
        assert inp.budget_amount_micros == 10_000_000
        assert inp.start_date is None

    def test_valid_with_dates(self):
        inp = CreateCampaignInput(
            customer_id="1234567890",
            name="Dated Campaign",
            campaign_type="DISPLAY",
            bidding_strategy_type="MAXIMIZE_CLICKS",
            budget_amount_micros=5_000_000,
            start_date="2026-03-01",
            end_date="2026-12-31",
        )
        assert inp.start_date == "2026-03-01"
        assert inp.end_date == "2026-12-31"

    def test_budget_must_be_positive(self):
        with pytest.raises(ValidationError, match="greater than 0"):
            CreateCampaignInput(
                customer_id="1234567890",
                name="Bad",
                campaign_type="SEARCH",
                bidding_strategy_type="MANUAL_CPC",
                budget_amount_micros=0,
            )

    def test_invalid_campaign_type(self):
        with pytest.raises(ValidationError):
            CreateCampaignInput(
                customer_id="1234567890",
                name="Bad",
                campaign_type="UNKNOWN",
                bidding_strategy_type="MANUAL_CPC",
                budget_amount_micros=1_000_000,
            )

    def test_invalid_date_format(self):
        with pytest.raises(ValidationError):
            CreateCampaignInput(
                customer_id="1234567890",
                name="Bad",
                campaign_type="SEARCH",
                bidding_strategy_type="MANUAL_CPC",
                budget_amount_micros=1_000_000,
                start_date="01-03-2026",
            )

    def test_target_cpa_requires_target(self):
        with pytest.raises(ValidationError, match="target_cpa_micros"):
            CreateCampaignInput(
                customer_id="1234567890",
                name="CPA Campaign",
                campaign_type="SEARCH",
                bidding_strategy_type="TARGET_CPA",
                budget_amount_micros=10_000_000,
            )

    def test_target_roas_requires_target(self):
        with pytest.raises(ValidationError, match="target_roas"):
            CreateCampaignInput(
                customer_id="1234567890",
                name="ROAS Campaign",
                campaign_type="SEARCH",
                bidding_strategy_type="TARGET_ROAS",
                budget_amount_micros=10_000_000,
            )

    def test_target_cpa_with_value(self):
        inp = CreateCampaignInput(
            customer_id="1234567890",
            name="CPA Campaign",
            campaign_type="SEARCH",
            bidding_strategy_type="TARGET_CPA",
            budget_amount_micros=10_000_000,
            target_cpa_micros=5_000_000,
        )
        assert inp.target_cpa_micros == 5_000_000

    def test_impossible_date_rejected(self):
        with pytest.raises(ValidationError):
            CreateCampaignInput(
                customer_id="1234567890",
                name="Bad",
                campaign_type="SEARCH",
                bidding_strategy_type="MANUAL_CPC",
                budget_amount_micros=1_000_000,
                start_date="2026-02-31",
            )

    def test_end_before_start_rejected(self):
        with pytest.raises(ValidationError, match="start_date must not be after end_date"):
            CreateCampaignInput(
                customer_id="1234567890",
                name="Bad",
                campaign_type="SEARCH",
                bidding_strategy_type="MANUAL_CPC",
                budget_amount_micros=1_000_000,
                start_date="2026-12-31",
                end_date="2026-01-01",
            )


class TestCreateAdGroupInput:
    def test_valid(self):
        inp = CreateAdGroupInput(
            customer_id="1234567890",
            campaign_id="111",
            name="My Ad Group",
            ad_group_type="SEARCH_STANDARD",
        )
        assert inp.campaign_id == "111"
        assert inp.ad_group_type == AdGroupType.SEARCH_STANDARD
        assert inp.cpc_bid_micros is None

    def test_with_bid(self):
        inp = CreateAdGroupInput(
            customer_id="1234567890",
            campaign_id="111",
            name="Bid Group",
            ad_group_type="SEARCH_STANDARD",
            cpc_bid_micros=2_000_000,
        )
        assert inp.cpc_bid_micros == 2_000_000


class TestCreateResponsiveSearchAdInput:
    def test_valid(self):
        inp = CreateResponsiveSearchAdInput(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
        )
        assert len(inp.headlines) == 3
        assert len(inp.descriptions) == 2
        assert inp.path1 is None

    def test_min_headlines(self):
        with pytest.raises(ValidationError, match="at least 3"):
            CreateResponsiveSearchAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=["H1", "H2"],
                descriptions=["D1", "D2"],
                final_urls=["https://example.com"],
            )

    def test_max_headlines(self):
        with pytest.raises(ValidationError, match="at most 15"):
            CreateResponsiveSearchAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=[f"H{i}" for i in range(16)],
                descriptions=["D1", "D2"],
                final_urls=["https://example.com"],
            )

    def test_min_descriptions(self):
        with pytest.raises(ValidationError, match="at least 2"):
            CreateResponsiveSearchAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=["H1", "H2", "H3"],
                descriptions=["D1"],
                final_urls=["https://example.com"],
            )

    def test_max_descriptions(self):
        with pytest.raises(ValidationError, match="at most 4"):
            CreateResponsiveSearchAdInput(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=["H1", "H2", "H3"],
                descriptions=["D1", "D2", "D3", "D4", "D5"],
                final_urls=["https://example.com"],
            )

    def test_with_paths(self):
        inp = CreateResponsiveSearchAdInput(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
            path1="sale",
            path2="shoes",
        )
        assert inp.path1 == "sale"
        assert inp.path2 == "shoes"


class TestAddKeywordsInput:
    def test_valid(self):
        inp = AddKeywordsInput(
            customer_id="1234567890",
            ad_group_id="222",
            keywords=["running shoes", "athletic shoes"],
            match_type="broad",
        )
        assert inp.match_type == MatchType.BROAD
        assert inp.cpc_bid_micros is None

    def test_with_bid(self):
        inp = AddKeywordsInput(
            customer_id="1234567890",
            ad_group_id="222",
            keywords=["shoes"],
            match_type="exact",
            cpc_bid_micros=1_500_000,
        )
        assert inp.cpc_bid_micros == 1_500_000

    def test_max_20(self):
        with pytest.raises(ValidationError, match="at most 20"):
            AddKeywordsInput(
                customer_id="1234567890",
                ad_group_id="222",
                keywords=[f"kw{i}" for i in range(21)],
            )

    def test_empty_rejected(self):
        with pytest.raises(ValidationError, match="at least 1"):
            AddKeywordsInput(
                customer_id="1234567890",
                ad_group_id="222",
                keywords=[],
            )


class TestSetBiddingStrategyInput:
    def test_manual_cpc(self):
        inp = SetBiddingStrategyInput(
            customer_id="1234567890",
            campaign_id="111",
            strategy_type="MANUAL_CPC",
        )
        assert inp.strategy_type == BiddingStrategyType.MANUAL_CPC

    def test_target_cpa_requires_value(self):
        with pytest.raises(ValidationError, match="target_cpa_micros"):
            SetBiddingStrategyInput(
                customer_id="1234567890",
                campaign_id="111",
                strategy_type="TARGET_CPA",
            )

    def test_target_roas_requires_value(self):
        with pytest.raises(ValidationError, match="target_roas"):
            SetBiddingStrategyInput(
                customer_id="1234567890",
                campaign_id="111",
                strategy_type="TARGET_ROAS",
            )

    def test_target_cpa_with_value(self):
        inp = SetBiddingStrategyInput(
            customer_id="1234567890",
            campaign_id="111",
            strategy_type="TARGET_CPA",
            target_cpa_micros=3_000_000,
        )
        assert inp.target_cpa_micros == 3_000_000


class TestUpdateKeywordInput:
    def test_update_bid(self):
        inp = UpdateKeywordInput(
            customer_id="1234567890",
            ad_group_id="222",
            criterion_id="555",
            cpc_bid_micros=2_000_000,
        )
        assert inp.cpc_bid_micros == 2_000_000
        assert inp.status is None

    def test_update_status(self):
        inp = UpdateKeywordInput(
            customer_id="1234567890",
            ad_group_id="222",
            criterion_id="555",
            status="pause",
        )
        assert inp.status == StatusAction.PAUSE

    def test_requires_at_least_one_change(self):
        with pytest.raises(ValidationError, match="(?i)at least one"):
            UpdateKeywordInput(
                customer_id="1234567890",
                ad_group_id="222",
                criterion_id="555",
            )


class TestCreateAdExtensionInput:
    def test_sitelink(self):
        inp = CreateAdExtensionInput(
            customer_id="1234567890",
            campaign_id="111",
            extension_type="SITELINK",
            link_text="About Us",
            final_urls=["https://example.com/about"],
        )
        assert inp.extension_type == ExtensionType.SITELINK

    def test_callout(self):
        inp = CreateAdExtensionInput(
            customer_id="1234567890",
            campaign_id="111",
            extension_type="CALLOUT",
            callout_text="Free Shipping",
        )
        assert inp.callout_text == "Free Shipping"

    def test_call(self):
        inp = CreateAdExtensionInput(
            customer_id="1234567890",
            campaign_id="111",
            extension_type="CALL",
            phone_number="+39123456789",
            country_code="IT",
        )
        assert inp.phone_number == "+39123456789"

    def test_structured_snippet(self):
        inp = CreateAdExtensionInput(
            customer_id="1234567890",
            campaign_id="111",
            extension_type="STRUCTURED_SNIPPET",
            snippet_header="Brands",
            snippet_values=["Nike", "Adidas", "Puma"],
        )
        assert inp.snippet_header == "Brands"

    def test_sitelink_requires_link_text(self):
        with pytest.raises(ValidationError, match="link_text"):
            CreateAdExtensionInput(
                customer_id="1234567890",
                campaign_id="111",
                extension_type="SITELINK",
                final_urls=["https://example.com"],
            )

    def test_callout_requires_text(self):
        with pytest.raises(ValidationError, match="callout_text"):
            CreateAdExtensionInput(
                customer_id="1234567890",
                campaign_id="111",
                extension_type="CALLOUT",
            )

    def test_call_requires_phone(self):
        with pytest.raises(ValidationError, match="phone_number"):
            CreateAdExtensionInput(
                customer_id="1234567890",
                campaign_id="111",
                extension_type="CALL",
            )

    def test_snippet_requires_header_and_values(self):
        with pytest.raises(ValidationError, match="snippet_header"):
            CreateAdExtensionInput(
                customer_id="1234567890",
                campaign_id="111",
                extension_type="STRUCTURED_SNIPPET",
            )

    def test_call_requires_country_code(self):
        with pytest.raises(ValidationError, match="country_code"):
            CreateAdExtensionInput(
                customer_id="1234567890",
                campaign_id="111",
                extension_type="CALL",
                phone_number="+39123456789",
            )

    def test_snippet_requires_values(self):
        with pytest.raises(ValidationError, match="snippet_values"):
            CreateAdExtensionInput(
                customer_id="1234567890",
                campaign_id="111",
                extension_type="STRUCTURED_SNIPPET",
                snippet_header="Brands",
            )


class TestSetDeviceTargetingInput:
    def test_valid(self):
        inp = SetDeviceTargetingInput(
            customer_id="1234567890",
            campaign_id="111",
            device="MOBILE",
            bid_modifier=1.5,
        )
        assert inp.device == DeviceType.MOBILE
        assert inp.bid_modifier == 1.5

    def test_exclude_device(self):
        inp = SetDeviceTargetingInput(
            customer_id="1234567890",
            campaign_id="111",
            device="TABLET",
            bid_modifier=0.0,
        )
        assert inp.bid_modifier == 0.0

    def test_negative_modifier_rejected(self):
        with pytest.raises(ValidationError):
            SetDeviceTargetingInput(
                customer_id="1234567890",
                campaign_id="111",
                device="MOBILE",
                bid_modifier=-0.5,
            )


class TestSetDemographicTargetingInput:
    def test_valid(self):
        inp = SetDemographicTargetingInput(
            customer_id="1234567890",
            campaign_id="111",
            dimension="AGE",
            values=["AGE_RANGE_25_34", "AGE_RANGE_35_44"],
        )
        assert inp.dimension == DemographicDimension.AGE
        assert len(inp.values) == 2

    def test_empty_values_rejected(self):
        with pytest.raises(ValidationError, match="at least 1"):
            SetDemographicTargetingInput(
                customer_id="1234567890",
                campaign_id="111",
                dimension="GENDER",
                values=[],
            )


class TestCreateAudienceSegmentInput:
    def test_valid(self):
        inp = CreateAudienceSegmentInput(
            customer_id="1234567890",
            campaign_id="111",
            audience_type="IN_MARKET",
            audience_id="123456",
        )
        assert inp.audience_type == AudienceType.IN_MARKET

    def test_with_bid_modifier(self):
        inp = CreateAudienceSegmentInput(
            customer_id="1234567890",
            campaign_id="111",
            audience_type="REMARKETING",
            audience_id="789",
            bid_modifier=1.2,
        )
        assert inp.bid_modifier == 1.2
