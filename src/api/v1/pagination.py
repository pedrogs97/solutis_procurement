"""Pagination helpers for Ninja v1 routers."""

from typing import Optional


def build_page_link(request, page_number: Optional[int], size: int) -> Optional[str]:
    """Build a pagination link preserving current query params."""
    if page_number is None:
        return None
    base_url = request.build_absolute_uri(request.path)
    query = request.GET.copy()
    query["page"] = page_number
    query["size"] = size
    return f"{base_url}?{query.urlencode()}"
