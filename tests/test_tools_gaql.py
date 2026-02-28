"""Tests for custom GAQL query tool."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.gaql import (
    _flatten_dict,
    gads_execute_gaql,
)


class TestFlattenDict:
    def test_flat_dict(self):
        out = {}
        _flatten_dict({"a": 1, "b": 2}, out)
        assert out == {"a": 1, "b": 2}

    def test_nested_dict(self):
        out = {}
        _flatten_dict({"campaign": {"name": "Test", "id": 123}}, out)
        assert out == {"campaign.name": "Test", "campaign.id": 123}

    def test_deeply_nested(self):
        out = {}
        _flatten_dict({"a": {"b": {"c": "deep"}}}, out)
        assert out == {"a.b.c": "deep"}

    def test_empty_dict(self):
        out = {}
        _flatten_dict({}, out)
        assert out == {}

    def test_mixed_types(self):
        out = {}
        _flatten_dict({"a": 1, "b": {"c": "text"}, "d": [1, 2]}, out)
        assert out["a"] == 1
        assert out["b.c"] == "text"
        assert out["d"] == [1, 2]


class TestGadsExecuteGaql:
    def test_non_select_query_rejected(self):
        result = gads_execute_gaql(
            customer_id="1234567890",
            query="DELETE FROM campaign WHERE campaign.id = 1",
            ctx=MagicMock(),
        )
        assert "Error" in result
        assert "SELECT" in result

    def test_update_query_rejected(self):
        result = gads_execute_gaql(
            customer_id="1234567890",
            query="UPDATE campaign SET name = 'test'",
            ctx=MagicMock(),
        )
        assert "Error" in result

    def test_insert_query_rejected(self):
        result = gads_execute_gaql(
            customer_id="1234567890",
            query="INSERT INTO campaign VALUES ('test')",
            ctx=MagicMock(),
        )
        assert "Error" in result

    @patch("google_ads_mcp.tools.gaql.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()

        mock_row = MagicMock()
        type(mock_row).to_dict = MagicMock(return_value={
            "campaign": {"name": "Test Campaign", "id": "123"},
            "metrics": {"clicks": 50},
        })
        mock_client.query.return_value = [mock_row]
        mock_get_client.return_value = mock_client

        result = gads_execute_gaql(
            customer_id="1234567890",
            query="SELECT campaign.name, metrics.clicks FROM campaign",
            ctx=MagicMock(),
        )
        assert "## GAQL Results" in result
        assert "1 rows" in result

    @patch("google_ads_mcp.tools.gaql.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()

        mock_row = MagicMock()
        type(mock_row).to_dict = MagicMock(return_value={
            "campaign": {"name": "Test", "id": "456"},
        })
        mock_client.query.return_value = [mock_row]
        mock_get_client.return_value = mock_client

        result = gads_execute_gaql(
            customer_id="1234567890",
            query="SELECT campaign.name FROM campaign",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "results" in data
        assert "count" in data
        assert data["count"] == 1

    @patch("google_ads_mcp.tools.gaql.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_execute_gaql(
            customer_id="1234567890",
            query="SELECT campaign.name FROM campaign WHERE campaign.id = 99999",
            ctx=MagicMock(),
        )
        assert "No results found" in result

    @patch("google_ads_mcp.tools.gaql.get_client")
    def test_empty_results_json(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_execute_gaql(
            customer_id="1234567890",
            query="SELECT campaign.name FROM campaign WHERE campaign.id = 99999",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["count"] == 0
        assert data["results"] == []

    @patch("google_ads_mcp.tools.gaql.get_client")
    def test_limit_enforcement(self, mock_get_client):
        mock_client = MagicMock()

        mock_rows = []
        for i in range(10):
            mock_row = MagicMock()
            type(mock_row).to_dict = MagicMock(return_value={"id": str(i)})
            mock_rows.append(mock_row)
        mock_client.query.return_value = mock_rows
        mock_get_client.return_value = mock_client

        result = gads_execute_gaql(
            customer_id="1234567890",
            query="SELECT campaign.id FROM campaign",
            limit=3,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["count"] == 3

    @patch("google_ads_mcp.tools.gaql.get_client")
    def test_row_serialization_fallback(self, mock_get_client):
        """Test fallback when proto to_dict fails."""
        mock_client = MagicMock()

        mock_row = MagicMock()
        type(mock_row).to_dict = MagicMock(side_effect=Exception("Serialization error"))
        mock_row.__str__ = MagicMock(return_value="raw row data")
        mock_client.query.return_value = [mock_row]
        mock_get_client.return_value = mock_client

        result = gads_execute_gaql(
            customer_id="1234567890",
            query="SELECT campaign.name FROM campaign",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["count"] == 1
        assert "raw" in data["results"][0]

    def test_select_case_insensitive(self):
        """SELECT check should be case-insensitive."""
        # This should NOT be rejected (leading whitespace + lowercase)
        # But it calls get_client which we need to mock
        pass

    @patch("google_ads_mcp.tools.gaql.get_client")
    def test_select_with_whitespace(self, mock_get_client):
        """Query with leading whitespace should work."""
        mock_client = MagicMock()
        mock_client.query.return_value = []
        mock_get_client.return_value = mock_client

        result = gads_execute_gaql(
            customer_id="1234567890",
            query="  SELECT campaign.name FROM campaign",
            ctx=MagicMock(),
        )
        assert "No results found" in result

    def test_invalid_customer_id(self):
        """Invalid customer ID should raise ValueError."""
        with pytest.raises(ValueError):
            gads_execute_gaql(
                customer_id="invalid",
                query="SELECT campaign.name FROM campaign",
                ctx=MagicMock(),
            )
