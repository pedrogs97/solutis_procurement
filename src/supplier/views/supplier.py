"""
Views for supplier-related operations in the procurement service.
This module defines views for managing suppliers, including listing and retrieving supplier details.
"""

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from src.shared.views import BaseAPIView
from src.supplier.filters import SupplierFilters
from src.supplier.models.supplier import Supplier
from src.supplier.serializers.inbound.supplier import SupplierInSerializer
from src.supplier.serializers.outbound.supplier import SupplierOutSerializer


class SupplierView(BaseAPIView):
    """
    A view for handling supplier-related operations.
    This class can be extended to implement specific supplier functionalities.
    """

    queryset = Supplier.objects.all()
    serializer_class_out = SupplierOutSerializer
    serializer_class_in = SupplierInSerializer


class SupplierListView(ListAPIView):
    """
    A view to list all suppliers.
    This view uses the BaseAPIView for common functionalities.
    """

    queryset = Supplier.objects.all()
    serializer_class = SupplierOutSerializer

    pagination_class = PageNumberPagination
    filterset_class = SupplierFilters
    search_fields = ["trade_name", "legal_name", "tax_id"]

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
