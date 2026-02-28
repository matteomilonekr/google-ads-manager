"""Tests for mutation input models."""

import pytest
from pydantic import ValidationError
from google_ads_mcp.models.mutation_inputs import (
    SetCampaignStatusInput,
    UpdateCampaignInput,
    SetAdGroupStatusInput,
    SetAdStatusInput,
    UpdateBudgetInput,
    AddNegativeKeywordsInput,
    SetLocationTargetingInput,
    SetLanguageTargetingInput,
)
from google_ads_mcp.models.common import StatusAction, NegativeKeywordLevel, MatchType


class TestSetCampaignStatusInput:
    def test_valid(self):
        inp = SetCampaignStatusInput(
            customer_id="123-456-7890", campaign_id="111", status="pause"
        )
        assert inp.customer_id == "1234567890"
        assert inp.campaign_id == "111"
        assert inp.status == StatusAction.PAUSE

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            SetCampaignStatusInput(
                customer_id="1234567890", campaign_id="111", status="invalid"
            )


class TestUpdateCampaignInput:
    def test_valid_with_name(self):
        inp = UpdateCampaignInput(
            customer_id="1234567890", campaign_id="111", name="New Name"
        )
        assert inp.name == "New Name"
        assert inp.start_date is None
        assert inp.end_date is None

    def test_requires_at_least_one_field(self):
        with pytest.raises(ValidationError, match="(?i)at least one"):
            UpdateCampaignInput(customer_id="1234567890", campaign_id="111")

    def test_invalid_date_format_rejected(self):
        with pytest.raises(ValidationError):
            UpdateCampaignInput(
                customer_id="1234567890", campaign_id="111",
                start_date="15-01-2026"
            )


class TestSetAdGroupStatusInput:
    def test_valid(self):
        inp = SetAdGroupStatusInput(
            customer_id="1234567890", ad_group_id="222", status="enable"
        )
        assert inp.ad_group_id == "222"
        assert inp.status == StatusAction.ENABLE


class TestSetAdStatusInput:
    def test_valid(self):
        inp = SetAdStatusInput(
            customer_id="1234567890",
            ad_group_id="222",
            ad_id="333",
            status="remove",
        )
        assert inp.ad_group_id == "222"
        assert inp.ad_id == "333"
        assert inp.status == StatusAction.REMOVE


class TestUpdateBudgetInput:
    def test_valid(self):
        inp = UpdateBudgetInput(
            customer_id="1234567890", budget_id="444", amount_micros=5_000_000
        )
        assert inp.amount_micros == 5_000_000

    def test_amount_must_be_positive(self):
        with pytest.raises(ValidationError, match="greater than 0"):
            UpdateBudgetInput(
                customer_id="1234567890", budget_id="444", amount_micros=0
            )

    def test_negative_amount_rejected(self):
        with pytest.raises(ValidationError):
            UpdateBudgetInput(
                customer_id="1234567890", budget_id="444", amount_micros=-100
            )


class TestAddNegativeKeywordsInput:
    def test_valid_campaign_level(self):
        inp = AddNegativeKeywordsInput(
            customer_id="1234567890",
            level="campaign",
            campaign_id="111",
            keywords=["free", "cheap"],
            match_type="exact",
        )
        assert inp.level == NegativeKeywordLevel.CAMPAIGN
        assert inp.keywords == ["free", "cheap"]
        assert inp.match_type == MatchType.EXACT

    def test_valid_ad_group_level(self):
        inp = AddNegativeKeywordsInput(
            customer_id="1234567890",
            level="ad_group",
            ad_group_id="222",
            keywords=["discount"],
        )
        assert inp.level == NegativeKeywordLevel.AD_GROUP

    def test_max_20_keywords(self):
        with pytest.raises(ValidationError, match="at most 20"):
            AddNegativeKeywordsInput(
                customer_id="1234567890",
                level="campaign",
                campaign_id="111",
                keywords=[f"kw{i}" for i in range(21)],
            )

    def test_empty_keywords_rejected(self):
        with pytest.raises(ValidationError, match="at least 1"):
            AddNegativeKeywordsInput(
                customer_id="1234567890",
                level="campaign",
                campaign_id="111",
                keywords=[],
            )

    def test_campaign_level_requires_campaign_id(self):
        with pytest.raises(ValidationError):
            AddNegativeKeywordsInput(
                customer_id="1234567890",
                level="campaign",
                keywords=["test"],
            )

    def test_ad_group_level_requires_ad_group_id(self):
        with pytest.raises(ValidationError):
            AddNegativeKeywordsInput(
                customer_id="1234567890",
                level="ad_group",
                keywords=["test"],
            )


class TestSetLocationTargetingInput:
    def test_valid(self):
        inp = SetLocationTargetingInput(
            customer_id="1234567890",
            campaign_id="111",
            location_ids=[2380, 2826],
            exclude=False,
        )
        assert inp.location_ids == [2380, 2826]
        assert inp.exclude is False

    def test_default_exclude_false(self):
        inp = SetLocationTargetingInput(
            customer_id="1234567890",
            campaign_id="111",
            location_ids=[2380],
        )
        assert inp.exclude is False


class TestSetLanguageTargetingInput:
    def test_valid(self):
        inp = SetLanguageTargetingInput(
            customer_id="1234567890",
            campaign_id="111",
            language_ids=[1000, 1004],
        )
        assert inp.language_ids == [1000, 1004]
