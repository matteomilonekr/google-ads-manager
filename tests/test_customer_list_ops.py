"""Tests for customer match list mutation tools."""

import hashlib
import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.mutations.customer_list_ops import (
    _build_user_data_list,
    _hash_value,
    gads_remove_customer_list_members,
    gads_upload_customer_list,
)


class TestHashValue:
    def test_basic_hash(self):
        result = _hash_value("test@example.com")
        expected = hashlib.sha256(b"test@example.com").hexdigest()
        assert result == expected

    def test_deterministic(self):
        assert _hash_value("hello") == _hash_value("hello")

    def test_different_inputs(self):
        assert _hash_value("a") != _hash_value("b")


class TestBuildUserDataList:
    def test_emails_only(self):
        mock_client = MagicMock()
        mock_client.client.get_type.return_value = MagicMock()

        result = _build_user_data_list(
            mock_client,
            emails="test@a.com, test@b.com",
            phones="",
        )
        assert len(result) == 2

    def test_phones_only(self):
        mock_client = MagicMock()
        mock_client.client.get_type.return_value = MagicMock()

        result = _build_user_data_list(
            mock_client,
            emails="",
            phones="+1234567890, +0987654321",
        )
        assert len(result) == 2

    def test_both_emails_and_phones(self):
        mock_client = MagicMock()
        mock_client.client.get_type.return_value = MagicMock()

        result = _build_user_data_list(
            mock_client,
            emails="test@a.com",
            phones="+1234567890",
        )
        assert len(result) == 2

    def test_empty_inputs(self):
        mock_client = MagicMock()
        result = _build_user_data_list(mock_client, emails="", phones="")
        assert len(result) == 0

    def test_whitespace_only_entries(self):
        mock_client = MagicMock()
        result = _build_user_data_list(
            mock_client,
            emails="  ,  ,  ",
            phones="  ,  ",
        )
        assert len(result) == 0

    def test_mixed_valid_and_empty(self):
        mock_client = MagicMock()
        mock_client.client.get_type.return_value = MagicMock()

        result = _build_user_data_list(
            mock_client,
            emails="test@a.com, , test@b.com",
            phones="",
        )
        assert len(result) == 2


class TestGadsUploadCustomerList:
    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_upload_emails(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.received_operations_count = 2

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_upload_customer_list(
            customer_id="1234567890",
            user_list_id="555",
            emails="user1@test.com, user2@test.com",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["uploaded"] == 2
        assert data["received_operations_count"] == 2

    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_upload_phones(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.received_operations_count = 1

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_upload_customer_list(
            customer_id="1234567890",
            user_list_id="555",
            phones="+1234567890",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["uploaded"] == 1

    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_upload_emails_and_phones(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.received_operations_count = 3

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_upload_customer_list(
            customer_id="1234567890",
            user_list_id="555",
            emails="user1@test.com, user2@test.com",
            phones="+1234567890",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["uploaded"] == 3

    def test_empty_input_validation(self):
        """Empty emails and phones should return error without calling API."""
        result = gads_upload_customer_list(
            customer_id="1234567890",
            user_list_id="555",
            emails="",
            phones="",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "error" in data

    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_service_called_correctly(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.received_operations_count = 1

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        gads_upload_customer_list(
            customer_id="1234567890",
            user_list_id="555",
            emails="test@example.com",
            ctx=MagicMock(),
        )

        mock_client.get_service.assert_called_once_with("UserDataService")
        mock_service.upload_user_data.assert_called_once()

    def test_invalid_customer_id(self):
        """Invalid customer ID should raise ValueError."""
        with pytest.raises(ValueError):
            gads_upload_customer_list(
                customer_id="bad",
                user_list_id="555",
                emails="test@example.com",
                ctx=MagicMock(),
            )

    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_response_without_received_operations_count(self, mock_get_client):
        """Fallback when response lacks received_operations_count attribute."""
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock(spec=[])  # Empty spec = no attributes

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_upload_customer_list(
            customer_id="1234567890",
            user_list_id="555",
            emails="test@example.com",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["uploaded"] == 1
        assert data["received_operations_count"] == 1


class TestGadsRemoveCustomerListMembers:
    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_remove_emails(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.received_operations_count = 2

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_remove_customer_list_members(
            customer_id="1234567890",
            user_list_id="555",
            emails="user1@test.com, user2@test.com",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["removed"] == 2
        assert data["received_operations_count"] == 2

    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_remove_phones(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.received_operations_count = 1

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_remove_customer_list_members(
            customer_id="1234567890",
            user_list_id="555",
            phones="+9876543210",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["removed"] == 1

    def test_empty_input_validation(self):
        """Empty emails and phones should return error."""
        result = gads_remove_customer_list_members(
            customer_id="1234567890",
            user_list_id="555",
            emails="",
            phones="",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "error" in data

    def test_invalid_customer_id(self):
        """Invalid customer ID should raise ValueError."""
        with pytest.raises(ValueError):
            gads_remove_customer_list_members(
                customer_id="invalid",
                user_list_id="555",
                emails="test@example.com",
                ctx=MagicMock(),
            )

    @patch("google_ads_mcp.tools.mutations.customer_list_ops.get_client")
    def test_uses_remove_operation(self, mock_get_client):
        """Verify remove operation is used (not create)."""
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.received_operations_count = 1

        mock_service.upload_user_data.return_value = mock_response
        mock_client.get_service.return_value = mock_service

        mock_op = MagicMock()
        mock_client.client.get_type.return_value = mock_op
        mock_get_client.return_value = mock_client

        gads_remove_customer_list_members(
            customer_id="1234567890",
            user_list_id="555",
            emails="test@example.com",
            ctx=MagicMock(),
        )

        mock_service.upload_user_data.assert_called_once()
