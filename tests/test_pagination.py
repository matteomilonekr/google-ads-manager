"""Tests for pagination utilities."""

import pytest
from google_ads_mcp.utils.pagination import paginate_results, PaginationInfo


class TestPaginateResults:
    def test_basic_pagination(self):
        items = list(range(100))
        result, info = paginate_results(items, limit=10, offset=0)
        assert len(result) == 10
        assert result == list(range(10))
        assert info.total == 100
        assert info.count == 10
        assert info.has_more is True

    def test_second_page(self):
        items = list(range(100))
        result, info = paginate_results(items, limit=10, offset=10)
        assert result == list(range(10, 20))
        assert info.has_more is True

    def test_last_page(self):
        items = list(range(25))
        result, info = paginate_results(items, limit=10, offset=20)
        assert result == [20, 21, 22, 23, 24]
        assert info.count == 5
        assert info.has_more is False

    def test_empty_input(self):
        result, info = paginate_results([], limit=10, offset=0)
        assert result == []
        assert info.total == 0
        assert info.has_more is False

    def test_offset_beyond_end(self):
        items = list(range(5))
        result, info = paginate_results(items, limit=10, offset=100)
        assert result == []
        assert info.count == 0


class TestPaginationInfo:
    def test_to_dict(self):
        info = PaginationInfo(total=100, count=10, offset=0, limit=10, has_more=True)
        d = info.to_dict()
        assert d["total"] == 100
        assert d["count"] == 10
        assert d["has_more"] is True
