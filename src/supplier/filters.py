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

    status = CharFilter(method="filter_status")
    name = CharFilter(field_name="legal_name", lookup_expr="icontains")
    cnpj = CharFilter(field_name="tax_id", lookup_expr="icontains")

    def filter_status(self, queryset, name, value):
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
