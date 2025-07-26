from django_filters.rest_framework import CharFilter, FilterSet

from src.supplier.models.attachments import SupplierAttachment
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
        else:
            return queryset.filter(situation=int(value))

    class Meta:
        model = Supplier
        fields = ["situation"]


class SupplierAttachmentFilters(FilterSet):
    """
    FilterSet for SupplierAttachment model to allow filtering by various fields.
    """

    class Meta:
        model = SupplierAttachment
        fields = {
            "supplier": ["exact"],
            "attachment_type": ["exact"],
            "created_at": ["gte", "lte", "exact"],
            "updated_at": ["gte", "lte", "exact"],
        }
