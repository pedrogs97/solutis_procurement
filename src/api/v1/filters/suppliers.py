"""Supplier list filters"""

from typing import Annotated, List, Optional

from django.db.models import OuterRef, Q, Subquery
from ninja import FilterLookup
from pydantic import Field

from src.api.v1.filters.base import BaseFilters
from src.supplier.models.supplier import SupplierSituation


class SupplierListFilters(BaseFilters):
    """Supplier list query filters for Ninja endpoints."""

    name: Annotated[Optional[str], FilterLookup("name__icontains")] = None
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

    def _status_values(self) -> List[int]:
        if not self.status:
            return []

        values: List[int] = []
        for item in self.status.split(","):
            item = item.strip()
            if not item:
                continue
            try:
                values.append(int(item))
            except ValueError:
                continue
        return values

    def filter_status(self, value: str) -> Q:
        """Filter suppliers by the latest situation status using a CSV string."""
        status_values = self._status_values()
        if not status_values:
            return Q()

        latest_situation_id_subquery = (
            SupplierSituation.objects.filter(supplier=OuterRef("supplier"))
            .order_by("-created_at")
            .values("id")[:1]
        )

        supplier_ids_with_latest_status = SupplierSituation.objects.filter(
            id=Subquery(latest_situation_id_subquery),
            status__in=status_values,
        ).values("supplier_id")

        return Q(id__in=Subquery(supplier_ids_with_latest_status))
