"""
Views for responsibility matrix-related operations in the procurement service.
This module defines views for managing responsibility matrices, including creating, retrieving and updating.
"""

from rest_framework.exceptions import MethodNotAllowed
from django.shortcuts import get_object_or_404

from src.shared.views import BaseAPIView
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import Supplier
from src.supplier.serializers.inbound.responsibility_matrix import (
    ResponsibilityMatrixInSerializer,
)
from src.supplier.serializers.outbound.responsibility_matrix import (
    ResponsibilityMatrixOutSerializer,
)


class ResponsibilityMatrixView(BaseAPIView):
    """
    A view for handling responsibility matrix-related operations.
    Supports GET (retrieve), POST (create), PUT (update), and PATCH (partial update).
    Does not support DELETE or list operations.
    """

    queryset = ResponsibilityMatrix.objects.all()
    serializer_class_out = ResponsibilityMatrixOutSerializer
    serializer_class_in = ResponsibilityMatrixInSerializer

    def delete(self, request, *args, **kwargs):
        """
        Override delete method to disable DELETE operations.
        """
        raise MethodNotAllowed(
            "DELETE",
            detail="Operação DELETE não permitida para matrizes de responsabilidade.",
        )

    def get_object(self):
        """
        Retrieve the responsibility matrix associated with the supplier.
        """
        supplier: Supplier = get_object_or_404(Supplier, pk=self.kwargs.get("pk"))
        self.kwargs["pk"] = supplier.responsibility_matrix.pk
        return super().get_object()

    def get_queryset(self):
        """
        Override get_queryset to disable list operations.
        Only allows retrieve operations (with pk).
        """
        if "pk" not in self.kwargs:
            raise MethodNotAllowed(
                "GET",
                detail="Listagem não permitida. Use GET com ID específico para recuperar uma matriz.",
            )
        return super().get_queryset()
