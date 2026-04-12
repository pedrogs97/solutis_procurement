"""Base list filters"""

from django.db.models import Q
from ninja import FilterConfigDict, FilterSchema


class BaseFilters(FilterSchema):
    """Base filters for Ninja endpoints."""

    model_config = FilterConfigDict(ignore_none=False)

    def custom_expression(self) -> Q:
        """Allow subclasses to extend filter expressions without changing API behavior."""
        return Q()
