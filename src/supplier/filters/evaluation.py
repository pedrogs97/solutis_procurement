"""
FilterSet for SupplierEvaluation model.
"""

from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from src.supplier.models.evaluation import SupplierEvaluation


class SupplierEvaluationFilters(FilterSet):
    """
    FilterSet for SupplierEvaluation model to allow filtering by various fields.
    This can be extended with more filters as needed.
    """

    supplier = NumberFilter(field_name="supplier_id", lookup_expr="exact")
    evaluation_year = NumberFilter(field_name="evaluation_year", lookup_expr="exact")
    period_type = CharFilter(field_name="period_type", lookup_expr="exact")
    period_number = NumberFilter(field_name="period_number", lookup_expr="exact")

    class Meta:
        """
        Meta options for the Supplier filter.
        """

        model = SupplierEvaluation
        fields = ["supplier", "evaluation_year", "period_type", "period_number"]
