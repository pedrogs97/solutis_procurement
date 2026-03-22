"""Pagination helpers for Ninja v1 routers."""

from typing import Any, Dict, Optional

from django.core.paginator import EmptyPage, Paginator
from django.db.models import QuerySet

from src.shared.schemas import PaginatedResponse


def build_page_link(request, page_number: Optional[int], size: int) -> Optional[str]:
    """Build a pagination link preserving current query params."""
    if page_number is None:
        return None
    base_url = request.build_absolute_uri(request.path)
    query = request.GET.copy()
    query["page"] = page_number
    query["size"] = size
    return f"{base_url}?{query.urlencode()}"


def paginate(
    request, queryset: QuerySet, page: int, size: int, serializer_class
) -> Dict[str, Any]:
    """Paginate a queryset and return a structured response."""
    paginator = Paginator(queryset, size)

    try:
        current_page = paginator.page(page)
    except EmptyPage:
        return PaginatedResponse(
            count=paginator.count,
            next=None,
            previous=None,
            results=[],
        ).model_dump(by_alias=True)

    results = (
        [serializer_class(item) for item in current_page.object_list]
        if paginator.count
        else []
    )

    next_page_number = (
        current_page.next_page_number() if current_page.has_next() else None
    )
    previous_page_number = (
        current_page.previous_page_number() if current_page.has_previous() else None
    )
    return PaginatedResponse(
        count=paginator.count,
        next=(
            build_page_link(
                request,
                next_page_number,
                size,
            )
            if paginator.count
            else None
        ),
        previous=(
            build_page_link(
                request,
                previous_page_number,
                size,
            )
            if paginator.count
            else None
        ),
        results=results,
    ).model_dump(by_alias=True)
