"""This module contains validators for supplier-related serializers."""

from src.shared.validation import BaseValidationError
from src.supplier.models.supplier import Supplier


def validate_supplier(value) -> Supplier:
    """Validate that the supplier exists and is active."""
    try:
        supplier = Supplier.objects.get(pk=value.pk)
        return supplier
    except Supplier.DoesNotExist as exc:
        raise BaseValidationError(
            "supplier",
            message="Fornecedor não encontrado.",
        ) from exc
