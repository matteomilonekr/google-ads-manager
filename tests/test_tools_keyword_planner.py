"""Tests for keyword planner tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from google_ads_mcp.tools.keyword_planner import gads_generate_keyword_ideas


def _make_keyword_idea(
    text="running shoes",
    avg_monthly_searches=12000,
    competition="HIGH",
    low_bid_micros=500000,
    high_bid_micros=2500000,
):
    idea = MagicMock()
    idea.text = text
    idea.keyword_idea_metrics.avg_monthly_searches = avg_monthly_searches
    idea.keyword_idea_metrics.competition = competition
    idea.keyword_idea_metrics.low_top_of_page_bid_micros = low_bid_micros
    idea.keyword_idea_metrics.high_top_of_page_bid_micros = high_bid_micros
    return idea


class TestGadsGenerateKeywordIdeas:
    @patch("google_ads_mcp.tools.keyword_planner.get_client")
    def test_markdown_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_service.generate_keyword_ideas.return_value = [
            _make_keyword_idea(text="running shoes"),
            _make_keyword_idea(text="trail running shoes"),
        ]
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="running shoes, sneakers",
            ctx=MagicMock(),
        )
        assert "## Keyword Ideas" in result
        assert "running shoes" in result

    @patch("google_ads_mcp.tools.keyword_planner.get_client")
    def test_json_output(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_service.generate_keyword_ideas.return_value = [
            _make_keyword_idea(text="running shoes", avg_monthly_searches=12000),
        ]
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="running shoes",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "keyword_ideas" in data
        assert "seed_keywords" in data
        assert "pagination" in data
        assert len(data["keyword_ideas"]) == 1
        assert data["keyword_ideas"][0]["keyword"] == "running shoes"
        assert data["keyword_ideas"][0]["avg_monthly_searches"] == 12000
        assert data["seed_keywords"] == ["running shoes"]

    @patch("google_ads_mcp.tools.keyword_planner.get_client")
    def test_with_geo_target(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_service.generate_keyword_ideas.return_value = [
            _make_keyword_idea(text="sneakers"),
        ]
        mock_client.get_service.return_value = mock_service
        mock_request = MagicMock()
        mock_client.client.get_type.return_value = mock_request
        mock_get_client.return_value = mock_client

        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="sneakers",
            geo_target_id="2840",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "keyword_ideas" in data
        assert len(data["keyword_ideas"]) == 1

    @patch("google_ads_mcp.tools.keyword_planner.get_client")
    def test_empty_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_service.generate_keyword_ideas.return_value = []
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="xyz123abc",
            ctx=MagicMock(),
        )
        assert "0 of 0" in result

    def test_empty_keywords(self):
        """Test that empty keywords string returns an error."""
        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "error" in data

    def test_whitespace_only_keywords(self):
        """Test that whitespace-only keywords string returns an error."""
        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="  ,  ,  ",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert "error" in data

    @patch("google_ads_mcp.tools.keyword_planner.get_client")
    def test_pagination(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_service.generate_keyword_ideas.return_value = [
            _make_keyword_idea(text=f"keyword {i}")
            for i in range(10)
        ]
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="test",
            limit=3,
            offset=0,
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["pagination"]["total"] == 10
        assert data["pagination"]["count"] == 3
        assert data["pagination"]["has_more"] is True

    @patch("google_ads_mcp.tools.keyword_planner.get_client")
    def test_competition_parsing(self, mock_get_client):
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_service.generate_keyword_ideas.return_value = [
            _make_keyword_idea(
                text="test keyword",
                competition="KeywordPlanCompetitionLevel.HIGH",
            ),
        ]
        mock_client.get_service.return_value = mock_service
        mock_client.client.get_type.return_value = MagicMock()
        mock_get_client.return_value = mock_client

        result = gads_generate_keyword_ideas(
            customer_id="1234567890",
            keywords="test",
            response_format="json",
            ctx=MagicMock(),
        )
        data = json.loads(result)
        assert data["keyword_ideas"][0]["competition"] == "HIGH"
