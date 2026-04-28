"""Attachment schemas for Ninja v1."""

from typing import Optional, Union

from src.api.v1.schemas.common import CamelSchema
from src.supplier.models.attachments import (
    SupplierAttachment,
    SupplierAttachmentHistory,
)


class AttachmentUploadIn(CamelSchema):
    """Payload for supplier attachment upload."""

    supplier: int
    attachment_type: int
    description: Optional[str] = None


class AttachmentOut(CamelSchema):
    """Serialized supplier attachment."""

    id: int
    attachment_type_id: int
    attachment_type_name: str
    file_name: Optional[str] = None
    description: Optional[str] = None


class AttachmentVersionOut(CamelSchema):
    """Serialized attachment version (current or historical)."""

    id: int
    attachment_type_id: int
    attachment_type_name: str
    file_name: Optional[str] = None
    description: Optional[str] = None
    is_current: bool
    uploaded_at: str


class AttachmentTypeOut(CamelSchema):
    """Serialized attachment type."""

    id: int
    name: str
    risk_level: Optional[int] = None


class AttachmentTypeCreateIn(CamelSchema):
    """Payload to create an attachment type."""

    name: str
    risk_level: Optional[int] = None


class AttachmentTypePatchIn(CamelSchema):
    """Payload to partially update an attachment type."""

    name: Optional[str] = None
    risk_level: Optional[int] = None


def serialize_attachment(instance: SupplierAttachment) -> dict:
    """Map a SupplierAttachment model into API output format."""
    return AttachmentOut(
        id=instance.id,
        attachment_type_id=instance.attachment_type_id,
        attachment_type_name=instance.attachment_type.name,
        file_name=instance.file_name,
        description=instance.description,
    ).model_dump(by_alias=True)


def serialize_attachment_version(
    instance: Union[SupplierAttachment, SupplierAttachmentHistory],
    *,
    is_current: bool,
) -> dict:
    """Map current or historical attachment model into versioned API output format."""
    return AttachmentVersionOut(
        id=instance.id,
        attachment_type_id=instance.attachment_type_id,
        attachment_type_name=instance.attachment_type.name,
        file_name=instance.file_name,
        description=instance.description,
        is_current=is_current,
        uploaded_at=instance.created_at.isoformat(),
    ).model_dump(by_alias=True)
