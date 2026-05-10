"""Supplier list filters"""

from typing import Annotated, List, Optional

from django.db.models import OuterRef, Q, Subquery
from ninja import FilterLookup
from pydantic import Field

from src.api.v1.filters.base import BaseFilters
from src.supplier.models.supplier import SupplierSituation


class SupplierListFilters(BaseFilters):
    """Supplier list query filters for Ninja endpoints."""

    name: Annotated[
        Optional[str],
        FilterLookup(["legal_name__icontains", "trade_name__icontains"]),
    ] = None
    cnpj: Annotated[Optional[str], FilterLookup("tax_id__icontains")] = None
    risk_level_id: Optional[int] = Field(
        default=None, ge=0, description="Risk level ID", alias="risk"
    )
    status: Optional[str] = None
    search: Annotated[
        Optional[str],
        FilterLookup(
            ["trade_name__icontains", "legal_name__icontains", "tax_id__icontains"]
        ),
    ] = None

    def _status_names(self) -> List[str]:
        if not self.status:
            return []
        return [s.strip().upper() for s in self.status.split(",") if s.strip()]

    def filter_status(self, value: str) -> Q:
        """Filter suppliers by the latest situation status name (CSV)."""
        status_names = self._status_names()
        if not status_names:
            return Q()

        latest_situation_id_subquery = (
            SupplierSituation.objects.filter(supplier=OuterRef("supplier"))
            .order_by("-created_at")
            .values("id")[:1]
        )

        supplier_ids_with_latest_status = SupplierSituation.objects.filter(
            id=Subquery(latest_situation_id_subquery),
            status__name__in=status_names,
        ).values("supplier_id")

        return Q(id__in=Subquery(supplier_ids_with_latest_status))
