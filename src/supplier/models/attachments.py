import os

from django.conf import settings
from django.db import models

from src.shared.models import TimestampedModel
from src.supplier.models.domain import DomAttachmentType
from src.supplier.models.supplier import Supplier
from src.utils.upload import supplier_attachment_upload_path


class SupplierAttachment(TimestampedModel):
    attachment_type = models.ForeignKey(
        DomAttachmentType,
        on_delete=models.DO_NOTHING,
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

    class Meta(TimestampedModel.Meta):
        db_table = "supplier_attachment"
        verbose_name = "Supplier Attachment"
        verbose_name_plural = "Supplier Attachments"
        abstract = False
