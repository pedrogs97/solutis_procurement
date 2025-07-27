"""
Serializer for ResponsibilityMatrix model.
This module provides serializers for output representations of the ResponsibilityMatrix model.
"""

from src.shared.serializers import BaseSerializer
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix


class ResponsibilityMatrixOutSerializer(BaseSerializer):
    """
    Serializer for ResponsibilityMatrix model output.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for ResponsibilityMatrixOutSerializer.
        """

        model = ResponsibilityMatrix
        fields = None
        exclude = ("supplier",)
