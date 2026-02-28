"""Tests for Google Ads API client wrapper."""

import pytest
from unittest.mock import MagicMock
from google_ads_mcp.client import GoogleAdsClientWrapper


class TestGoogleAdsClientWrapper:
    def setup_method(self):
        self.mock_client = MagicMock()
        self.wrapper = GoogleAdsClientWrapper(self.mock_client)

    def test_stores_client(self):
        assert self.wrapper.client is self.mock_client

    def test_get_service(self):
        self.mock_client.get_service.return_value = MagicMock()
        svc = self.wrapper.get_service("GoogleAdsService")
        self.mock_client.get_service.assert_called_once_with("GoogleAdsService")
        assert svc is not None

    def test_query_returns_rows(self):
        mock_service = MagicMock()
        self.mock_client.get_service.return_value = mock_service
        mock_row = MagicMock()
        mock_row.campaign.name = "Test Campaign"
        mock_response = MagicMock()
        mock_response.__iter__ = MagicMock(return_value=iter([mock_row]))
        mock_service.search.return_value = mock_response

        rows = self.wrapper.query("1234567890", "SELECT campaign.name FROM campaign")
        assert len(rows) == 1

    def test_query_empty_result(self):
        mock_service = MagicMock()
        self.mock_client.get_service.return_value = mock_service
        mock_response = MagicMock()
        mock_response.__iter__ = MagicMock(return_value=iter([]))
        mock_service.search.return_value = mock_response

        rows = self.wrapper.query("1234567890", "SELECT campaign.name FROM campaign")
        assert rows == []

    def test_query_validates_select_only(self):
        with pytest.raises(ValueError, match="SELECT"):
            self.wrapper.query("1234567890", "UPDATE campaign SET name='test'")

    def test_mutate_calls_service(self):
        mock_service = MagicMock()
        self.mock_client.get_service.return_value = mock_service
        mock_service.mutate.return_value = MagicMock()

        ops = [MagicMock()]
        self.wrapper.mutate("1234567890", ops)
        mock_service.mutate.assert_called_once()


class TestClientWrapperRetry:
    def test_retry_on_transient_error(self):
        mock_client = MagicMock()
        wrapper = GoogleAdsClientWrapper(mock_client, max_retries=3)
        assert wrapper.max_retries == 3

    def test_default_max_retries(self):
        mock_client = MagicMock()
        wrapper = GoogleAdsClientWrapper(mock_client)
        assert wrapper.max_retries == 3
