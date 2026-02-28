"""Tests for creation tools (campaign, ad group, RSA)."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.tools.mutations.creation_ops import (
    gads_create_campaign,
    gads_create_ad_group,
    gads_create_responsive_search_ad,
)


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    wrapper = MagicMock()
    wrapper.client = MagicMock()
    # mutate returns response with resource names
    response = MagicMock()
    response.mutate_operation_responses = [
        MagicMock(campaign_budget_result=MagicMock(resource_name="customers/1234567890/campaignBudgets/999")),
        MagicMock(campaign_result=MagicMock(resource_name="customers/1234567890/campaigns/888")),
    ]
    wrapper.mutate.return_value = response
    ctx.request_context.lifespan_context = {"ads_client": wrapper}
    return ctx


class TestCreateCampaign:
    def test_creates_campaign(self, mock_ctx):
        result = gads_create_campaign(
            customer_id="1234567890",
            name="Test Campaign",
            campaign_type="SEARCH",
            bidding_strategy_type="MANUAL_CPC",
            budget_amount_micros=10_000_000,
            ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        wrapper.mutate.assert_called_once()
        assert "Test Campaign" in result
        assert "PAUSED" in result
        assert "SEARCH" in result
        assert "MANUAL_CPC" in result
        assert "888" in result
        assert "999" in result

    def test_with_dates(self, mock_ctx):
        result = gads_create_campaign(
            customer_id="1234567890",
            name="Dated Campaign",
            campaign_type="DISPLAY",
            bidding_strategy_type="MAXIMIZE_CLICKS",
            budget_amount_micros=5_000_000,
            start_date="2026-03-01",
            end_date="2026-12-31",
            ctx=mock_ctx,
        )
        assert isinstance(result, str)
        assert "Dated Campaign" in result
        assert "DISPLAY" in result

    def test_with_target_cpa(self, mock_ctx):
        result = gads_create_campaign(
            customer_id="1234567890",
            name="CPA Campaign",
            campaign_type="SEARCH",
            bidding_strategy_type="TARGET_CPA",
            budget_amount_micros=20_000_000,
            target_cpa_micros=5_000_000,
            ctx=mock_ctx,
        )
        assert "CPA Campaign" in result
        assert "TARGET_CPA" in result

    def test_with_target_roas(self, mock_ctx):
        result = gads_create_campaign(
            customer_id="1234567890",
            name="ROAS Campaign",
            campaign_type="SEARCH",
            bidding_strategy_type="TARGET_ROAS",
            budget_amount_micros=20_000_000,
            target_roas=3.0,
            ctx=mock_ctx,
        )
        assert "ROAS Campaign" in result
        assert "TARGET_ROAS" in result

    def test_target_cpa_without_micros_raises(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_campaign(
                customer_id="1234567890",
                name="Bad CPA",
                campaign_type="SEARCH",
                bidding_strategy_type="TARGET_CPA",
                budget_amount_micros=10_000_000,
                ctx=ctx,
            )

    def test_target_roas_without_value_raises(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_campaign(
                customer_id="1234567890",
                name="Bad ROAS",
                campaign_type="SEARCH",
                bidding_strategy_type="TARGET_ROAS",
                budget_amount_micros=10_000_000,
                ctx=ctx,
            )

    def test_invalid_campaign_type_raises(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_campaign(
                customer_id="1234567890",
                name="Bad Type",
                campaign_type="INVALID",
                bidding_strategy_type="MANUAL_CPC",
                budget_amount_micros=10_000_000,
                ctx=ctx,
            )

    def test_budget_formatted_in_result(self, mock_ctx):
        result = gads_create_campaign(
            customer_id="1234567890",
            name="Budget Test",
            campaign_type="SEARCH",
            bidding_strategy_type="MANUAL_CPC",
            budget_amount_micros=10_000_000,
            ctx=mock_ctx,
        )
        assert "10.00" in result
        assert "/day" in result


class TestCreateAdGroup:
    def test_creates_ad_group(self, mock_ctx):
        # Override mock for ad group response
        response = MagicMock()
        response.mutate_operation_responses = [
            MagicMock(ad_group_result=MagicMock(resource_name="customers/1234567890/adGroups/777")),
        ]
        mock_ctx.request_context.lifespan_context["ads_client"].mutate.return_value = response

        result = gads_create_ad_group(
            customer_id="1234567890",
            campaign_id="111",
            name="My Ad Group",
            ad_group_type="SEARCH_STANDARD",
            ctx=mock_ctx,
        )
        assert "My Ad Group" in result
        assert "SEARCH_STANDARD" in result
        assert "777" in result

    def test_with_cpc_bid(self, mock_ctx):
        response = MagicMock()
        response.mutate_operation_responses = [
            MagicMock(ad_group_result=MagicMock(resource_name="customers/1234567890/adGroups/555")),
        ]
        mock_ctx.request_context.lifespan_context["ads_client"].mutate.return_value = response

        result = gads_create_ad_group(
            customer_id="1234567890",
            campaign_id="111",
            name="CPC Ad Group",
            ad_group_type="SEARCH_STANDARD",
            cpc_bid_micros=1_500_000,
            ctx=mock_ctx,
        )
        assert "CPC Ad Group" in result
        assert "555" in result

    def test_invalid_ad_group_type_raises(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_ad_group(
                customer_id="1234567890",
                campaign_id="111",
                name="Bad Type",
                ad_group_type="INVALID",
                ctx=ctx,
            )

    def test_mutate_called_with_single_operation(self, mock_ctx):
        response = MagicMock()
        response.mutate_operation_responses = [
            MagicMock(ad_group_result=MagicMock(resource_name="customers/1234567890/adGroups/777")),
        ]
        mock_ctx.request_context.lifespan_context["ads_client"].mutate.return_value = response

        gads_create_ad_group(
            customer_id="1234567890",
            campaign_id="111",
            name="Test",
            ad_group_type="DISPLAY_STANDARD",
            ctx=mock_ctx,
        )
        wrapper = mock_ctx.request_context.lifespan_context["ads_client"]
        args = wrapper.mutate.call_args
        # Second argument is the operations list
        assert len(args[0][1]) == 1


class TestCreateResponsiveSearchAd:
    def test_creates_rsa(self, mock_ctx):
        response = MagicMock()
        response.mutate_operation_responses = [
            MagicMock(ad_group_ad_result=MagicMock(resource_name="customers/1234567890/adGroupAds/222~666")),
        ]
        mock_ctx.request_context.lifespan_context["ads_client"].mutate.return_value = response

        result = gads_create_responsive_search_ad(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
            ctx=mock_ctx,
        )
        assert "3 headlines" in result
        assert "2 descriptions" in result
        assert "666" in result

    def test_with_paths(self, mock_ctx):
        response = MagicMock()
        response.mutate_operation_responses = [
            MagicMock(ad_group_ad_result=MagicMock(resource_name="customers/1234567890/adGroupAds/222~777")),
        ]
        mock_ctx.request_context.lifespan_context["ads_client"].mutate.return_value = response

        result = gads_create_responsive_search_ad(
            customer_id="1234567890",
            ad_group_id="222",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
            path1="shoes",
            path2="sale",
            ctx=mock_ctx,
        )
        assert isinstance(result, str)
        assert "3 headlines" in result

    def test_too_few_headlines_raises(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_responsive_search_ad(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=["H1"],
                descriptions=["D1", "D2"],
                final_urls=["https://example.com"],
                ctx=ctx,
            )

    def test_too_few_descriptions_raises(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_responsive_search_ad(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=["H1", "H2", "H3"],
                descriptions=["D1"],
                final_urls=["https://example.com"],
                ctx=ctx,
            )

    def test_no_final_urls_raises(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {"ads_client": MagicMock()}
        with pytest.raises(Exception):
            gads_create_responsive_search_ad(
                customer_id="1234567890",
                ad_group_id="222",
                headlines=["H1", "H2", "H3"],
                descriptions=["D1", "D2"],
                final_urls=[],
                ctx=ctx,
            )
