"""
FilterSet for Supplier and SupplierAttachment models.
This module provides filtering capabilities for supplier-related data.
"""

from django_filters.rest_framework import CharFilter, FilterSet

from src.supplier.models.supplier import Supplier


class SupplierFilters(FilterSet):
    """
    FilterSet for Supplier model to allow filtering by various fields.
    This can be extended with more filters as needed.
    """

    situation = CharFilter(method="filter_situation")

    def filter_situation(self, queryset, name, value):
        """
        Custom filter method for situation field.
        Accepts both single value and comma-separated list of values.
        """
        if not value:
            return queryset

        if "," in value:
            values = [int(v.strip()) for v in value.split(",") if v.strip()]
            return queryset.filter(situation__in=values)

        return queryset.filter(situation=int(value))

    class Meta:
        """
        Meta options for the Supplier filter.
        """

        model = Supplier
        fields = ["situation"]
