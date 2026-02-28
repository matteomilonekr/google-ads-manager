"""Tests for tool helpers."""

from unittest.mock import MagicMock

from google_ads_mcp.tools._helpers import (
    CAMPAIGN_STATUS_MAP,
    CAMPAIGN_TYPE_MAP,
    AD_GROUP_STATUS_MAP,
    get_client,
    safe_int,
    safe_float,
    safe_str,
)


class TestGetClient:
    def test_extracts_client_from_context(self):
        mock_ctx = MagicMock()
        mock_client = MagicMock()
        mock_ctx.request_context.lifespan_context = {"ads_client": mock_client}

        result = get_client(mock_ctx)
        assert result is mock_client


class TestSafeInt:
    def test_valid_int(self):
        assert safe_int(42) == 42

    def test_string_number(self):
        assert safe_int("100") == 100

    def test_none(self):
        assert safe_int(None) == 0

    def test_invalid(self):
        assert safe_int("abc") == 0


class TestSafeFloat:
    def test_valid_float(self):
        assert safe_float(3.14) == 3.14

    def test_none(self):
        assert safe_float(None) == 0.0

    def test_invalid(self):
        assert safe_float("abc") == 0.0


class TestSafeStr:
    def test_valid_string(self):
        assert safe_str("hello") == "hello"

    def test_none(self):
        assert safe_str(None) == ""

    def test_number(self):
        assert safe_str(42) == "42"


class TestMappings:
    def test_campaign_status_map(self):
        assert CAMPAIGN_STATUS_MAP["enabled"] == "ENABLED"
        assert CAMPAIGN_STATUS_MAP["paused"] == "PAUSED"
        assert CAMPAIGN_STATUS_MAP["removed"] == "REMOVED"

    def test_ad_group_status_map(self):
        assert AD_GROUP_STATUS_MAP["enabled"] == "ENABLED"

    def test_campaign_type_map(self):
        assert CAMPAIGN_TYPE_MAP["search"] == "SEARCH"
        assert CAMPAIGN_TYPE_MAP["performance_max"] == "PERFORMANCE_MAX"
        assert len(CAMPAIGN_TYPE_MAP) == 12
