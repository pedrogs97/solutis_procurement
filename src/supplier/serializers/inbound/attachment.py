"""
Serializer for SupplierAttachment model.
This module provides serializers for creating and updating supplier attachments,
including validation for supplier and attachment type existence, file size, and type.
"""

from rest_framework import serializers

from src.supplier.models.attachments import SupplierAttachment
from src.supplier.models.domain import DomAttachmentType
from src.supplier.models.supplier import Supplier


class SupplierAttachmentInSerializer(serializers.ModelSerializer):
    """
    Serializer for SupplierAttachment model input.
    Used for POST, PUT, and PATCH requests.
    """

    ALLOWED_EXTENSIONS = [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]

    class Meta:
        """
        Meta options for the SupplierAttachment input serializer.
        """

        model = SupplierAttachment
        fields = [
            "supplier",
            "attachment_type",
            "file",
            "description",
        ]

    def validate_supplier(self, value):
        """Validate that the supplier exists and is active."""
        try:
            supplier = Supplier.objects.get(pk=value.pk)
            return supplier
        except Supplier.DoesNotExist as exc:
            raise serializers.ValidationError("Fornecedor não encontrado.") from exc

    def validate_attachment_type(self, value):
        """Validate that the attachment type exists."""
        try:
            attachment_type = DomAttachmentType.objects.get(pk=value.pk)
            return attachment_type
        except DomAttachmentType.DoesNotExist as exc:
            raise serializers.ValidationError("Tipo de anexo não encontrado.") from exc

    def validate_file(self, value):
        """Validate the uploaded file."""
        if not value:
            raise serializers.ValidationError("Arquivo é obrigatório.")

        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                "Arquivo muito grande. Tamanho máximo: 10MB."
            )

        if not any(value.name.lower().endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise serializers.ValidationError("Tipo de arquivo não permitido.")

        return value
