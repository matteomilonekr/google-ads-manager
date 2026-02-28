"""Tests for response formatting utilities."""

import json
import pytest
from google_ads_mcp.utils.formatting import (
    micros_to_currency,
    format_percentage,
    format_response,
    format_table_markdown,
)


class TestMicrosToCurrency:
    def test_basic_conversion(self):
        assert micros_to_currency(1_000_000) == "1.00"

    def test_zero(self):
        assert micros_to_currency(0) == "0.00"

    def test_large_amount(self):
        assert micros_to_currency(50_000_000) == "50.00"

    def test_with_currency_symbol(self):
        result = micros_to_currency(1_234_560_000, currency="EUR")
        assert result == "1,234.56 EUR"

    def test_none_returns_dash(self):
        assert micros_to_currency(None) == "-"


class TestFormatPercentage:
    def test_basic(self):
        assert format_percentage(0.0456) == "4.56%"

    def test_zero(self):
        assert format_percentage(0) == "0.00%"

    def test_hundred(self):
        assert format_percentage(1.0) == "100.00%"

    def test_none_returns_dash(self):
        assert format_percentage(None) == "-"


class TestFormatResponse:
    def test_markdown_format(self):
        data = {"campaigns": [{"name": "Test", "clicks": 100}]}
        result = format_response(data, response_format="markdown", title="Campaigns")
        assert "# Campaigns" in result
        assert "Test" in result

    def test_json_format(self):
        data = {"campaigns": [{"name": "Test", "clicks": 100}]}
        result = format_response(data, response_format="json")
        parsed = json.loads(result)
        assert parsed == data

    def test_json_format_is_valid_json(self):
        data = {"key": "value"}
        result = format_response(data, response_format="json")
        assert json.loads(result) == data


class TestFormatTableMarkdown:
    def test_basic_table(self):
        rows = [
            {"name": "Campaign A", "clicks": 100},
            {"name": "Campaign B", "clicks": 200},
        ]
        result = format_table_markdown(rows, columns=["name", "clicks"])
        assert "Campaign A" in result
        assert "Campaign B" in result
        assert "100" in result

    def test_empty_rows(self):
        result = format_table_markdown([], columns=["name"])
        assert "nessun risultato" in result.lower() or "no results" in result.lower()

    def test_with_headers(self):
        rows = [{"id": "1", "name": "Test"}]
        result = format_table_markdown(rows, columns=["id", "name"], headers={"id": "ID", "name": "Nome"})
        assert "ID" in result
        assert "Nome" in result
