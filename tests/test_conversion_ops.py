"""Tests for conversion upload mutation tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.mutations.conversion_ops import (
    gads_upload_click_conversions,
)


class TestGadsUploadClickConversions:
    @patch("google_ads_mcp.tools.mutations.conversion_ops.get_client")
    def test_successful_upload(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()

        mock_result = MagicMock()
        mock_result.gclid = "test_gclid_123"
        mock_result.conversion_action = "customers/1234567890/conversionActions/456"
        mock_result.conversion_date_time = "2026-01-15 12:00:00+00:00"

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        mock_service.upload_click_conversions.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_upload_click_conversions(
            customer_id="1234567890",
            conversion_action_id="456",
            gclid="test_gclid_123",
            conversion_date_time="2026-01-15 12:00:00+00:00",
            conversion_value=99.99,
            currency_code="EUR",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["uploaded"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["gclid"] == "test_gclid_123"

    @patch("google_ads_mcp.tools.mutations.conversion_ops.get_client")
    def test_default_values(self, mock_get_client):
        """Test upload with default conversion_value and currency_code."""
        mock_client = MagicMock()
        mock_service = MagicMock()

        mock_result = MagicMock()
        mock_result.gclid = "gclid_abc"
        mock_result.conversion_action = "customers/1234567890/conversionActions/789"
        mock_result.conversion_date_time = "2026-02-01 08:00:00+00:00"

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        mock_service.upload_click_conversions.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_upload_click_conversions(
            customer_id="1234567890",
            conversion_action_id="789",
            gclid="gclid_abc",
            conversion_date_time="2026-02-01 08:00:00+00:00",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["uploaded"] == 1

    @patch("google_ads_mcp.tools.mutations.conversion_ops.get_client")
    def test_empty_response_results(self, mock_get_client):
        """Test when API returns no results (possible partial failure)."""
        mock_client = MagicMock()
        mock_service = MagicMock()

        mock_response = MagicMock()
        mock_response.results = []

        mock_service.upload_click_conversions.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_upload_click_conversions(
            customer_id="1234567890",
            conversion_action_id="456",
            gclid="test_gclid",
            conversion_date_time="2026-01-15 12:00:00+00:00",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["uploaded"] == 0
        assert data["results"] == []

    @patch("google_ads_mcp.tools.mutations.conversion_ops.get_client")
    def test_service_called_correctly(self, mock_get_client):
        """Verify the service is called with the right request structure."""
        mock_client = MagicMock()
        mock_service = MagicMock()

        mock_response = MagicMock()
        mock_response.results = []
        mock_service.upload_click_conversions.return_value = mock_response

        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        gads_upload_click_conversions(
            customer_id="1234567890",
            conversion_action_id="456",
            gclid="test_gclid",
            conversion_date_time="2026-01-15 12:00:00+00:00",
            ctx=MagicMock(),
        )

        mock_client.get_service.assert_called_once_with("ConversionUploadService")
        mock_service.upload_click_conversions.assert_called_once()

    def test_invalid_customer_id(self):
        """Invalid customer ID should raise ValueError."""
        with pytest.raises(ValueError):
            gads_upload_click_conversions(
                customer_id="bad",
                conversion_action_id="456",
                gclid="test",
                conversion_date_time="2026-01-15 12:00:00+00:00",
                ctx=MagicMock(),
            )
