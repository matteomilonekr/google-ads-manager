"""FastMCP server for Google Ads API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from google_ads_mcp.auth import load_config_from_env, create_google_ads_client
from google_ads_mcp.client import GoogleAdsClientWrapper

logger = logging.getLogger(__name__)

SERVER_NAME = "google_ads_mcp"


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Initialize Google Ads client at server startup.

    Yields a dict with 'ads_client' key containing the GoogleAdsClientWrapper.
    Tools access it via ctx.request_context.lifespan_state["ads_client"].
    """
    logger.info("Initializing Google Ads MCP server...")
    config = load_config_from_env()
    raw_client = create_google_ads_client(config)
    wrapper = GoogleAdsClientWrapper(raw_client)
    logger.info("Google Ads client initialized successfully.")

    yield {"ads_client": wrapper}

    logger.info("Google Ads MCP server shutting down.")


def create_server() -> FastMCP:
    """Create and configure the FastMCP server instance.

    Returns:
        Configured FastMCP server (tools not yet registered).
    """
    return FastMCP(
        SERVER_NAME,
        lifespan=app_lifespan,
    )


# Module-level server instance - tools register on this via @mcp.tool()
mcp = create_server()

# Import tools module to trigger @mcp.tool() registration
import google_ads_mcp.tools  # noqa: E402, F401


def main() -> None:
    """Entry point for running the server."""
    mcp.run()


if __name__ == "__main__":
    main()
