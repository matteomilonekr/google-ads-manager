"""Tests for error handling utilities."""

import pytest
from google_ads_mcp.utils.errors import (
    GoogleAdsMCPError,
    AuthenticationError,
    QuotaExhaustedError,
    ResourceNotFoundError,
    InvalidInputError,
    format_google_ads_error,
)


class TestGoogleAdsMCPError:
    def test_base_error_has_message(self):
        err = GoogleAdsMCPError("something failed")
        assert str(err) == "something failed"
        assert err.message == "something failed"

    def test_base_error_has_details(self):
        err = GoogleAdsMCPError("failed", details={"code": 123})
        assert err.details == {"code": 123}


class TestAuthenticationError:
    def test_is_subclass(self):
        err = AuthenticationError("bad token")
        assert isinstance(err, GoogleAdsMCPError)


class TestQuotaExhaustedError:
    def test_has_retry_after(self):
        err = QuotaExhaustedError("quota exceeded", retry_after_seconds=60)
        assert err.retry_after_seconds == 60


class TestResourceNotFoundError:
    def test_has_resource_info(self):
        err = ResourceNotFoundError("not found", resource_type="campaign", resource_id="123")
        assert err.resource_type == "campaign"
        assert err.resource_id == "123"


class TestInvalidInputError:
    def test_has_field_name(self):
        err = InvalidInputError("bad input", field="customer_id")
        assert err.field == "customer_id"


class TestFormatGoogleAdsError:
    def test_format_authentication_error(self):
        result = format_google_ads_error("AUTHENTICATION_ERROR", "Token expired")
        assert "auth" in result.lower() or "token" in result.lower()
        assert isinstance(result, str)

    def test_format_quota_error(self):
        result = format_google_ads_error("QUOTA_ERROR", "Rate limit exceeded")
        assert "quota" in result.lower() or "limit" in result.lower()

    def test_format_resource_not_found(self):
        result = format_google_ads_error("RESOURCE_NOT_FOUND", "Campaign 123 not found")
        assert "not found" in result.lower() or "non trovat" in result.lower()

    def test_format_unknown_error(self):
        result = format_google_ads_error("UNKNOWN_ERROR", "Something bad")
        assert isinstance(result, str)
        assert len(result) > 0
