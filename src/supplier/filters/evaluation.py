"""
FilterSet for SupplierEvaluation model.
"""

from django_filters.rest_framework import FilterSet, NumberFilter

from src.supplier.models.evaluation import SupplierEvaluation


class SupplierEvaluationFilters(FilterSet):
    """
    FilterSet for SupplierEvaluation model to allow filtering by various fields.
    This can be extended with more filters as needed.
    """

    period = NumberFilter(field_name="period_id", lookup_expr="exact")
    supplier = NumberFilter(field_name="supplier_id", lookup_expr="exact")

    class Meta:
        """
        Meta options for the Supplier filter.
        """

        model = SupplierEvaluation
        fields = ["period", "supplier"]
