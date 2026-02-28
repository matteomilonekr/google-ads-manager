"""Tests for extension and targeting builders."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.builders.operations import (
    build_create_extension_operation,
    build_device_targeting_operation,
    build_demographic_targeting_operations,
    build_audience_segment_operation,
    DEVICE_TYPE_TO_CRITERION,
)


@pytest.fixture
def mock_google_client():
    client = MagicMock()
    client.get_type.side_effect = lambda name: MagicMock()
    return client


class TestBuildCreateExtensionOperation:
    def test_sitelink(self, mock_google_client):
        op = build_create_extension_operation(
            mock_google_client, "1234567890", "111",
            extension_type="SITELINK",
            link_text="About Us",
            final_urls=["https://example.com/about"],
        )
        assert op is not None

    def test_callout(self, mock_google_client):
        op = build_create_extension_operation(
            mock_google_client, "1234567890", "111",
            extension_type="CALLOUT",
            callout_text="Free Shipping",
        )
        assert op is not None

    def test_call(self, mock_google_client):
        op = build_create_extension_operation(
            mock_google_client, "1234567890", "111",
            extension_type="CALL",
            phone_number="+39123456789",
            country_code="IT",
        )
        assert op is not None

    def test_structured_snippet(self, mock_google_client):
        op = build_create_extension_operation(
            mock_google_client, "1234567890", "111",
            extension_type="STRUCTURED_SNIPPET",
            snippet_header="Brands",
            snippet_values=["Nike", "Adidas"],
        )
        assert op is not None


class TestDeviceTypeMap:
    def test_mobile(self):
        assert DEVICE_TYPE_TO_CRITERION["MOBILE"] == 30001

    def test_desktop(self):
        assert DEVICE_TYPE_TO_CRITERION["DESKTOP"] == 30000

    def test_tablet(self):
        assert DEVICE_TYPE_TO_CRITERION["TABLET"] == 30002


class TestBuildDeviceTargetingOperation:
    def test_returns_operation(self, mock_google_client):
        op = build_device_targeting_operation(
            mock_google_client, "1234567890", "111",
            device="MOBILE", bid_modifier=1.5,
        )
        assert op is not None

    def test_exclude_device(self, mock_google_client):
        op = build_device_targeting_operation(
            mock_google_client, "1234567890", "111",
            device="TABLET", bid_modifier=0.0,
        )
        assert op is not None


class TestBuildDemographicTargetingOperations:
    def test_returns_list(self, mock_google_client):
        ops = build_demographic_targeting_operations(
            mock_google_client, "1234567890", "111",
            dimension="AGE",
            values=["AGE_RANGE_25_34", "AGE_RANGE_35_44"],
        )
        assert isinstance(ops, list)
        assert len(ops) == 2

    def test_with_bid_modifier(self, mock_google_client):
        ops = build_demographic_targeting_operations(
            mock_google_client, "1234567890", "111",
            dimension="GENDER",
            values=["MALE"],
            bid_modifier=1.2,
        )
        assert len(ops) == 1


class TestBuildAudienceSegmentOperation:
    def test_returns_operation(self, mock_google_client):
        op = build_audience_segment_operation(
            mock_google_client, "1234567890", "111",
            audience_type="IN_MARKET",
            audience_id="123456",
        )
        assert op is not None

    def test_with_bid_modifier(self, mock_google_client):
        op = build_audience_segment_operation(
            mock_google_client, "1234567890", "111",
            audience_type="REMARKETING",
            audience_id="789",
            bid_modifier=1.5,
        )
        assert op is not None
