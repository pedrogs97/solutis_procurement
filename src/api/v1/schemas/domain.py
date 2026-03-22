"""Domain schemas for Ninja v1."""

from typing import Optional

from src.api.v1.schemas.common import CamelSchema, DomainRefOut


class DomainItemOut(CamelSchema):
    """Basic domain item output."""

    id: int
    name: str


class SupplierSituationOut(CamelSchema):
    """Supplier situation output with optional pendency type."""

    id: int
    name: str
    pendency_type: Optional[DomainRefOut] = None
