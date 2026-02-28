"""Shared helpers for tool implementations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.client import GoogleAdsClientWrapper


# Maps our enum values to GAQL campaign status literals
CAMPAIGN_STATUS_MAP: dict[str, str] = {
    "enabled": "ENABLED",
    "paused": "PAUSED",
    "removed": "REMOVED",
}

AD_GROUP_STATUS_MAP: dict[str, str] = {
    "enabled": "ENABLED",
    "paused": "PAUSED",
    "removed": "REMOVED",
}

CAMPAIGN_TYPE_MAP: dict[str, str] = {
    "search": "SEARCH",
    "display": "DISPLAY",
    "shopping": "SHOPPING",
    "video": "VIDEO",
    "performance_max": "PERFORMANCE_MAX",
    "demand_gen": "DEMAND_GEN",
    "app": "APP",
    "smart": "SMART",
    "hotel": "HOTEL",
    "local": "LOCAL",
    "local_services": "LOCAL_SERVICES",
    "travel": "TRAVEL",
}


def get_client(ctx: Context) -> GoogleAdsClientWrapper:
    """Extract Google Ads client from FastMCP context."""
    return ctx.request_context.lifespan_context["ads_client"]


def safe_int(value: Any) -> int:
    """Safely convert a proto value to int, defaulting to 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def safe_float(value: Any) -> float:
    """Safely convert a proto value to float, defaulting to 0.0."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_str(value: Any) -> str:
    """Safely convert a proto value to string."""
    try:
        return str(value) if value is not None else ""
    except (TypeError, ValueError):
        return ""
