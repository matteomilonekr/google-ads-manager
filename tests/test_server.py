"""Tests for the MCP server setup."""

import pytest
from unittest.mock import patch, MagicMock
from google_ads_mcp.server import create_server, SERVER_NAME


class TestServerCreation:
    def test_server_name(self):
        assert SERVER_NAME == "google_ads_mcp"

    @patch("google_ads_mcp.server.load_config_from_env")
    @patch("google_ads_mcp.server.create_google_ads_client")
    def test_create_server_returns_fastmcp(self, mock_create, mock_load):
        mock_load.return_value = MagicMock()
        mock_create.return_value = MagicMock()
        server = create_server()
        assert server is not None
        assert server.name == SERVER_NAME


class TestServerLifespan:
    @patch("google_ads_mcp.server.load_config_from_env")
    @patch("google_ads_mcp.server.create_google_ads_client")
    @pytest.mark.asyncio
    async def test_lifespan_yields_client_wrapper(self, mock_create, mock_load):
        from google_ads_mcp.server import app_lifespan
        mock_load.return_value = MagicMock()
        mock_create.return_value = MagicMock()

        mock_server = MagicMock()
        async with app_lifespan(mock_server) as state:
            assert "ads_client" in state
            from google_ads_mcp.client import GoogleAdsClientWrapper
            assert isinstance(state["ads_client"], GoogleAdsClientWrapper)
