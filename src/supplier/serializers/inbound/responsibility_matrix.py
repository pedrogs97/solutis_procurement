"""
Serializer for ResponsibilityMatrix model.
This module provides serializers for creating and updating supplier responsibility matrices,
including validation for supplier existence and RACI values.
"""

from src.shared.serializers import BaseSerializer
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import Supplier
from src.supplier.serializers.validators import validate_supplier


class ResponsibilityMatrixInSerializer(BaseSerializer):
    """
    Serializer for ResponsibilityMatrix model input.
    Used for POST, PUT, and PATCH requests.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the ResponsibilityMatrix input serializer.
        """

        model = ResponsibilityMatrix

    def validate_supplier(self, value) -> Supplier:
        """Validate that the supplier exists and is active."""
        return validate_supplier(value)
