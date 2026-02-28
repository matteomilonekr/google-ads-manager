"""Shared utilities for Google Ads MCP server."""

from google_ads_mcp.utils.errors import (
    GoogleAdsMCPError,
    AuthenticationError,
    QuotaExhaustedError,
    ResourceNotFoundError,
    InvalidInputError,
    format_google_ads_error,
)
from google_ads_mcp.utils.formatting import (
    micros_to_currency,
    format_percentage,
    format_response,
    format_table_markdown,
)
from google_ads_mcp.utils.pagination import paginate_results, PaginationInfo

__all__ = [
    "GoogleAdsMCPError",
    "AuthenticationError",
    "QuotaExhaustedError",
    "ResourceNotFoundError",
    "InvalidInputError",
    "format_google_ads_error",
    "micros_to_currency",
    "format_percentage",
    "format_response",
    "format_table_markdown",
    "paginate_results",
    "PaginationInfo",
]
