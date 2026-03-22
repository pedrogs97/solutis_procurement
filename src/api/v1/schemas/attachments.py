"""Attachment schemas for Ninja v1."""

from src.api.v1.schemas.common import CamelSchema, DomainRefOut
from src.supplier.models.attachments import SupplierAttachment


class AttachmentUploadIn(CamelSchema):
    """Payload for supplier attachment upload."""

    supplier: int
    attachment_type: int
    description: str | None = None


class AttachmentOut(CamelSchema):
    """Serialized supplier attachment."""

    id: int
    attachment_type_id: int
    attachment_type_name: str
    file_name: str | None = None
    description: str | None = None


class AttachmentTypeOut(CamelSchema):
    """Serialized attachment type."""

    id: int
    name: str
    risk_level: DomainRefOut | None = None


def serialize_attachment(instance: SupplierAttachment) -> dict:
    """Map a SupplierAttachment model into API output format."""
    return AttachmentOut(
        id=instance.id,
        attachment_type_id=instance.attachment_type_id,
        attachment_type_name=instance.attachment_type.name,
        file_name=instance.file_name,
        description=instance.description,
    ).model_dump(by_alias=True)
