"""Tests for account hierarchy tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.hierarchy import (
    _build_customer_clients_query,
    _build_merchant_center_links_query,
    _parse_customer_client_row,
    _parse_merchant_center_link_row,
    gads_list_customer_clients,
    gads_list_accessible_customers,
    gads_list_merchant_center_links,
)


# ---------------------------------------------------------------------------
# Helpers to build mock rows
# ---------------------------------------------------------------------------

def _make_customer_client_row(
    client_customer="customers/9876543210",
    descriptive_name="Test Client Account",
    level="1",
    manager="False",
    status="ENABLED",
    currency_code="USD",
    time_zone="America/New_York",
):
    row = MagicMock()
    row.customer_client.client_customer = client_customer
    row.customer_client.descriptive_name = descriptive_name
    row.customer_client.level = level
    row.customer_client.manager = manager
    row.customer_client.status = status
    row.customer_client.currency_code = currency_code
    row.customer_client.time_zone = time_zone
    return row


# ---------------------------------------------------------------------------
# Tests: _build_customer_clients_query
# ---------------------------------------------------------------------------

class TestBuildCustomerClientsQuery:
    def test_query_structure(self):
        query = _build_customer_clients_query()
        assert "FROM customer_client" in query
        assert "customer_client.client_customer" in query
        assert "customer_client.descriptive_name" in query
        assert "customer_client.level" in query
        assert "customer_client.manager" in query
        assert "customer_client.status" in query
        assert "customer_client.currency_code" in query
        assert "customer_client.time_zone" in query


# ---------------------------------------------------------------------------
# Tests: _parse_customer_client_row
# ---------------------------------------------------------------------------

class TestParseCustomerClientRow:
    def test_basic_parsing(self):
        row = _make_customer_client_row()
        result = _parse_customer_client_row(row)
        assert result["client_customer"] == "customers/9876543210"
        assert result["descriptive_name"] == "Test Client Account"
        assert result["level"] == "1"
        assert result["manager"] == "False"
        assert result["currency_code"] == "USD"
        assert result["time_zone"] == "America/New_York"

    def test_status_strip(self):
        row = _make_customer_client_row(status="CustomerStatus.ENABLED")
        result = _parse_customer_client_row(row)
        assert result["status"] == "ENABLED"


# ---------------------------------------------------------------------------
# Tests: gads_list_customer_clients
# ---------------------------------------------------------------------------

class TestGadsListCustomerClients:
    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_customer_client_row(
                descriptive_name="Client A",
                currency_code="EUR",
            ),
            _make_customer_client_row(
                client_customer="customers/1111111111",
                descriptive_name="Client B",
                currency_code="USD",
            ),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_customer_clients(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Customer Clients" in result
        assert "Client A" in result
        assert "Client B" in result

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_customer_client_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_customer_clients(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "customer_clients" in data
        assert "pagination" in data
        assert len(data["customer_clients"]) == 1
        assert data["customer_clients"][0]["descriptive_name"] == "Test Client Account"
        assert data["customer_clients"][0]["currency_code"] == "USD"

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_customer_clients(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_customer_client_row(
                descriptive_name=f"Client {i}",
                client_customer=f"customers/{i}",
            )
            for i in range(6)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_customer_clients(
            customer_id="1234567890",
            limit=3,
            offset=0,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 6
        assert data["pagination"]["count"] == 3
        assert data["pagination"]["has_more"] is True

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_pagination_offset(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_customer_client_row(
                descriptive_name=f"Client {i}",
                client_customer=f"customers/{i}",
            )
            for i in range(6)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_customer_clients(
            customer_id="1234567890",
            limit=3,
            offset=4,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 6
        assert data["pagination"]["count"] == 2
        assert data["pagination"]["has_more"] is False


# ---------------------------------------------------------------------------
# Tests: gads_list_accessible_customers
# ---------------------------------------------------------------------------

class TestGadsListAccessibleCustomers:
    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.resource_names = [
            "customers/1234567890",
            "customers/9876543210",
        ]
        mock_service.list_accessible_customers.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_get_client.return_value = mock_client

        result = gads_list_accessible_customers(ctx=MagicMock())
        assert "## Accessible Customers" in result
        assert "1234567890" in result
        assert "9876543210" in result

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.resource_names = [
            "customers/1234567890",
            "customers/9876543210",
        ]
        mock_service.list_accessible_customers.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_get_client.return_value = mock_client

        result = gads_list_accessible_customers(
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "accessible_customers" in data
        assert "total" in data
        assert data["total"] == 2
        assert data["accessible_customers"][0]["customer_id"] == "1234567890"
        assert data["accessible_customers"][0]["resource_name"] == "customers/1234567890"
        assert data["accessible_customers"][1]["customer_id"] == "9876543210"

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_empty_results_markdown(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.resource_names = []
        mock_service.list_accessible_customers.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_get_client.return_value = mock_client

        result = gads_list_accessible_customers(ctx=MagicMock())
        assert "No accessible customer accounts found" in result

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_empty_results_json(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.resource_names = []
        mock_service.list_accessible_customers.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_get_client.return_value = mock_client

        result = gads_list_accessible_customers(
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["total"] == 0
        assert data["accessible_customers"] == []

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_single_customer(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.resource_names = ["customers/5555555555"]
        mock_service.list_accessible_customers.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_get_client.return_value = mock_client

        result = gads_list_accessible_customers(
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["total"] == 1
        assert data["accessible_customers"][0]["customer_id"] == "5555555555"

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_service_called_correctly(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.resource_names = []
        mock_service.list_accessible_customers.return_value = mock_response
        mock_client.get_service.return_value = mock_service
        mock_get_client.return_value = mock_client

        gads_list_accessible_customers(ctx=MagicMock())
        mock_client.get_service.assert_called_once_with("CustomerService")
        mock_service.list_accessible_customers.assert_called_once()


# ---------------------------------------------------------------------------
# Helpers for Merchant Center link tests
# ---------------------------------------------------------------------------

def _make_merchant_center_link_row(
    merchant_id="123456",
    account_name="My Shop",
    status="ENABLED",
):
    row = MagicMock()
    row.merchant_center_link.id = merchant_id
    row.merchant_center_link.merchant_center_account_name = account_name
    row.merchant_center_link.status = status
    return row


# ---------------------------------------------------------------------------
# Tests: _build_merchant_center_links_query
# ---------------------------------------------------------------------------

class TestBuildMerchantCenterLinksQuery:
    def test_query_structure(self):
        query = _build_merchant_center_links_query()
        assert "FROM merchant_center_link" in query
        assert "merchant_center_link.id" in query
        assert "merchant_center_link.merchant_center_account_name" in query
        assert "merchant_center_link.status" in query


# ---------------------------------------------------------------------------
# Tests: _parse_merchant_center_link_row
# ---------------------------------------------------------------------------

class TestParseMerchantCenterLinkRow:
    def test_basic_parsing(self):
        row = _make_merchant_center_link_row()
        result = _parse_merchant_center_link_row(row)
        assert result["merchant_id"] == "123456"
        assert result["account_name"] == "My Shop"
        assert result["status"] == "ENABLED"

    def test_status_strip(self):
        row = _make_merchant_center_link_row(
            status="MerchantCenterLinkStatus.ENABLED"
        )
        result = _parse_merchant_center_link_row(row)
        assert result["status"] == "ENABLED"


# ---------------------------------------------------------------------------
# Tests: gads_list_merchant_center_links
# ---------------------------------------------------------------------------

class TestGadsListMerchantCenterLinks:
    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_merchant_center_link_row(
                merchant_id="111", account_name="Shop A",
            ),
            _make_merchant_center_link_row(
                merchant_id="222", account_name="Shop B",
            ),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_merchant_center_links(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "## Merchant Center Links" in result
        assert "Shop A" in result
        assert "Shop B" in result

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_merchant_center_link_row(),
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_merchant_center_links(
            customer_id="1234567890",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "merchant_center_links" in data
        assert "pagination" in data
        assert len(data["merchant_center_links"]) == 1
        assert data["merchant_center_links"][0]["merchant_id"] == "123456"
        assert data["merchant_center_links"][0]["account_name"] == "My Shop"

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_list_merchant_center_links(
            customer_id="1234567890",
            ctx=MagicMock(),
        )
        assert "0/0" in result

    @patch("google_ads_mcp.tools.hierarchy.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = [
            _make_merchant_center_link_row(
                merchant_id=str(i), account_name=f"Shop {i}",
            )
            for i in range(5)
        ]
        mock_get_client.return_value = mock_client

        result = gads_list_merchant_center_links(
            customer_id="1234567890",
            limit=2,
            offset=0,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["count"] == 2
        assert data["pagination"]["has_more"] is True
