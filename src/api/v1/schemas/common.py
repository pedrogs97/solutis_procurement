"""Shared schema primitives for Ninja v1."""

from typing import Any, Union

from ninja import Schema
from pydantic import ConfigDict

from src.utils.parse import to_camel_case


class CamelSchema(Schema):
    """Schema that exposes camelCase fields in API payloads."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel_case,
        extra="allow",
    )


class DomainRefOut(CamelSchema):
    """Simple domain reference output."""

    id: int
    name: str


def dump_schema(data: Union[CamelSchema, dict[str, Any]]) -> dict[str, Any]:
    """Dump schema to a camelCase dict."""
    if isinstance(data, CamelSchema):
        return data.model_dump(by_alias=True, exclude_none=True)
    return data
