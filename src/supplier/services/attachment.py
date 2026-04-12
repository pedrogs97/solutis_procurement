"""Service for handling supplier attachment operations."""

from typing import Any, Dict

from django.db.transaction import atomic
from rest_framework import serializers

from src.supplier.models.attachments import (
    SupplierAttachment,
    SupplierAttachmentHistory,
)


class AttachmentService:
    """
    Service class for handling supplier attachment operations.
    """

    @staticmethod
    @atomic
    def create_attachment(
        serializer_class: type[serializers.ModelSerializer], data: Dict
    ) -> Any:
        """
        Create a new supplier attachment.
        If an existing attachment with the same supplier and attachment type exists,
        it will be deleted before creating the new one.

        Args:
            serializer_class (type[serializers.ModelSerializer]): The serializer class to use.
            data (Dict): The data to create the attachment.
        Returns:
            Any: The created attachment instance.
        """
        supplier_id = data.get("supplier")
        attachment_type_id = data.get("attachment_type")

        existing_attachment = SupplierAttachment.objects.filter(
            supplier_id=supplier_id,
            attachment_type_id=attachment_type_id,
        ).first()
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        if existing_attachment:
            if existing_attachment.file:
                SupplierAttachmentHistory.objects.create(
                    supplier_id=existing_attachment.supplier_id,
                    attachment_type_id=existing_attachment.attachment_type_id,
                    file=existing_attachment.file.name,
                    description=existing_attachment.description,
                    source_attachment=existing_attachment,
                )

            existing_attachment.description = serializer.validated_data.get(
                "description"
            )
            existing_attachment.file = serializer.validated_data.get("file")
            existing_attachment.save()
            return existing_attachment

        return serializer.save()
