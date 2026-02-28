"""Pagination utilities for Google Ads MCP server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationInfo:
    """Immutable pagination metadata."""

    total: int
    count: int
    offset: int
    limit: int
    has_more: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "count": self.count,
            "offset": self.offset,
            "limit": self.limit,
            "has_more": self.has_more,
        }


def paginate_results(
    items: list[T],
    limit: int,
    offset: int = 0,
) -> tuple[list[T], PaginationInfo]:
    """Paginate a list of results.

    Args:
        items: Full list of items.
        limit: Maximum items per page.
        offset: Starting index.

    Returns:
        Tuple of (page_items, pagination_info).
    """
    total = len(items)
    page = items[offset : offset + limit]
    has_more = (offset + limit) < total

    info = PaginationInfo(
        total=total,
        count=len(page),
        offset=offset,
        limit=limit,
        has_more=has_more,
    )
    return page, info
