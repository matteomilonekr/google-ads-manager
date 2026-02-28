"""Tests for common Pydantic models."""

import pytest
from pydantic import ValidationError
from google_ads_mcp.models.common import (
    ResponseFormat,
    CampaignStatusFilter,
    CustomerIdMixin,
    sanitize_customer_id,
)


class TestResponseFormat:
    def test_markdown_value(self):
        assert ResponseFormat.MARKDOWN == "markdown"

    def test_json_value(self):
        assert ResponseFormat.JSON == "json"


class TestCampaignStatusFilter:
    def test_all_statuses(self):
        assert CampaignStatusFilter.ALL == "all"
        assert CampaignStatusFilter.ENABLED == "enabled"
        assert CampaignStatusFilter.PAUSED == "paused"
        assert CampaignStatusFilter.REMOVED == "removed"


class TestSanitizeCustomerId:
    def test_removes_dashes(self):
        assert sanitize_customer_id("123-456-7890") == "1234567890"

    def test_no_dashes(self):
        assert sanitize_customer_id("1234567890") == "1234567890"

    def test_strips_whitespace(self):
        assert sanitize_customer_id("  1234567890  ") == "1234567890"

    def test_invalid_non_numeric(self):
        with pytest.raises(ValueError, match="numeric"):
            sanitize_customer_id("abc123")

    def test_invalid_wrong_length(self):
        with pytest.raises(ValueError, match="10 digit"):
            sanitize_customer_id("123")


class TestCustomerIdMixin:
    def test_valid_customer_id(self):
        from pydantic import BaseModel

        class TestModel(CustomerIdMixin, BaseModel):
            pass

        m = TestModel(customer_id="123-456-7890")
        assert m.customer_id == "1234567890"

    def test_invalid_customer_id(self):
        from pydantic import BaseModel

        class TestModel(CustomerIdMixin, BaseModel):
            pass

        with pytest.raises(ValidationError):
            TestModel(customer_id="bad")
