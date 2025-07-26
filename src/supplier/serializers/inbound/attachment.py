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

    class Meta:
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
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Fornecedor não encontrado.")

    def validate_attachment_type(self, value):
        """Validate that the attachment type exists."""
        try:
            attachment_type = DomAttachmentType.objects.get(pk=value.pk)
            return attachment_type
        except DomAttachmentType.DoesNotExist:
            raise serializers.ValidationError("Tipo de anexo não encontrado.")

    def validate_file(self, value):
        """Validate the uploaded file."""
        if not value:
            raise serializers.ValidationError("Arquivo é obrigatório.")

        # Validação de tamanho máximo (ex: 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                "Arquivo muito grande. Tamanho máximo: 10MB."
            )

        # Validação de tipos de arquivo permitidos (opcional)
        # allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        # if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
        #     raise serializers.ValidationError("Tipo de arquivo não permitido.")

        return value

    def validate(self, attrs):
        """Cross-field validation."""
        # Exemplo: Verificar se já existe um anexo deste tipo para este fornecedor
        # (descomente se quiser esta validação)
        # supplier = attrs.get('supplier')
        # attachment_type = attrs.get('attachment_type')
        #
        # if supplier and attachment_type:
        #     existing = SupplierAttachment.objects.filter(
        #         supplier=supplier,
        #         attachment_type=attachment_type
        #     ).exclude(pk=self.instance.pk if self.instance else None)
        #
        #     if existing.exists():
        #         raise serializers.ValidationError(
        #             "Já existe um anexo deste tipo para este fornecedor."
        #         )

        return attrs


class SupplierAttachmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating SupplierAttachment.
    Allows partial updates and optional file replacement.
    """

    file = serializers.FileField(required=False)

    class Meta:
        model = SupplierAttachment
        fields = [
            "attachment_type",
            "file",
            "description",
        ]

    def validate_file(self, value):
        """Validate the uploaded file if provided."""
        if value:
            # Validação de tamanho máximo (ex: 10MB)
            max_size = 10 * 1024 * 1024  # 10MB in bytes
            if value.size > max_size:
                raise serializers.ValidationError(
                    "Arquivo muito grande. Tamanho máximo: 10MB."
                )

        return value
