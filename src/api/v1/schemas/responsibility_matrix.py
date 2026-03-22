"""Responsibility matrix schemas for Ninja v1."""

from typing import Optional

from src.api.v1.schemas.common import CamelSchema
from src.utils.parse import to_camel_case


class ResponsibilityMatrixIn(CamelSchema):
    """Payload for responsibility matrix create/update operations."""

    supplier: Optional[int] = None


def serialize_responsibility_matrix(instance) -> dict:
    """Serialize a ResponsibilityMatrix model to camelCase response."""
    data = {}
    for field in instance._meta.fields:  # pylint: disable=protected-access
        if field.name == "supplier":
            continue
        value = getattr(instance, field.name)
        camel_key = to_camel_case(field.name)
        data[camel_key] = value.isoformat() if hasattr(value, "isoformat") else value
    return data
