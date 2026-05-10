"""Shared schema primitives for Ninja v1."""

from ninja import Schema
from pydantic import ConfigDict

from src.utils.parse import to_camel_case


class CamelSchema(Schema):
    """Schema that exposes camelCase fields in API payloads."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel_case,
        extra="ignore",
    )


class DomainRefOut(CamelSchema):
    """Simple domain reference output."""

    id: int
    name: str


class FieldErrorOut(CamelSchema):
    """Field-level error returned by API validation."""

    field: str | None = None
    message: str


class ErrorOut(CamelSchema):
    """Standard error response for documented API operations."""

    detail: str
    errors: list[FieldErrorOut] | None = None
