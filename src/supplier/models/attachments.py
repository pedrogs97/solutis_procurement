"""
Attachment model for supplier management in procurement service.
This model represents attachments related to suppliers, including file storage and metadata.
It includes fields for attachment type, file, description, and the supplier it is associated with.
"""

import os

from django.db import models

from src.shared.models import TimestampedModel
from src.supplier.models.domain import DomAttachmentType
from src.supplier.models.supplier import Supplier
from src.utils.upload import supplier_attachment_upload_path


class SupplierAttachment(TimestampedModel):
    """
    Model representing an attachment for a supplier.
    """

    attachment_type = models.ForeignKey(
        DomAttachmentType,
        on_delete=models.PROTECT,
        related_name="attachments",
        help_text="Tipo de Anexo",
    )
    file = models.FileField(
        upload_to=supplier_attachment_upload_path, help_text="Arquivo do Anexo"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Descrição do Anexo"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text="Fornecedor relacionado ao anexo",
    )

    def __str__(self):
        return f"{self.attachment_type} - {self.description or 'No Description'}"

    @property
    def file_name(self):
        """Returns only the file name without the path."""
        if self.file:
            return os.path.basename(self.file.name)
        return None

    def get_file_url(self):
        """Returns the file URL if available."""
        if self.file:
            return self.file.url
        return None

    @property
    def storage_path(self):
        """Returns the full path of the file in storage."""
        if self.file:
            return self.file.path
        return None

    @property
    def is_completed_files(self):
        """Checks if all required files are uploaded."""
        total_supplier_attachs = self.supplier.attachments.all().count()
        total_needed_attachs = (
            SupplierAttachment.objects.select_related("attachment_type")
            .filter(attachment_type__risk_level=self.supplier.risk_level)
            .count()
        )
        return total_supplier_attachs >= total_needed_attachs

    class Meta(TimestampedModel.Meta):
        """
        Meta options for the SupplierAttachment model.
        """

        db_table = "supplier_attachment"
        verbose_name = "Anexo de Fornecedor"
        verbose_name_plural = "Anexos de Fornecedor"
        abstract = False
        unique_together = (
            "supplier",
            "attachment_type",
        )
