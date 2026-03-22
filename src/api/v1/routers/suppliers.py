"""Supplier endpoints for Ninja API v1."""

# pylint: disable=duplicate-code

from typing import Optional

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from loguru import logger
from ninja import Router
from ninja.errors import HttpError

from src.api.v1.pagination import paginate
from src.api.v1.schemas.suppliers import (
    SupplierCreateIn,
    SupplierUpdateIn,
    apply_supplier_payload,
    serialize_supplier,
)
from src.supplier.filters.supplier import SupplierFilters
from src.supplier.models.approval_workflow import Approver
from src.supplier.models.supplier import Supplier
from src.supplier.services.approval_workflow import ApprovalWorkflowService

router = Router(tags=["suppliers"])


@router.post("/suppliers/", url_name="supplier-v1")
def create_supplier(request, payload: SupplierCreateIn):
    """Create a supplier and initialize its approval workflow."""
    user_email = str(getattr(request.user, "email", "") or "").strip()
    user_full_name = (
        str(request.user.get_full_name()).strip()
        if hasattr(request.user, "get_full_name")
        else ""
    )

    if not user_email:
        return JsonResponse(
            {"detail": "Usuario autenticado sem e-mail para iniciar aprovacao."},
            status=403,
        )

    with transaction.atomic():
        try:
            new_instance = apply_supplier_payload(None, payload)
        except (TypeError, ValueError, IntegrityError) as exc:
            logger.exception("Falha ao criar fornecedor")
            raise HttpError(400, "Dados do fornecedor invalidos.") from exc

        initial_approver, _ = Approver.objects.get_or_create(
            email=user_email,
            defaults={"name": user_full_name or user_email},
        )

        if not initial_approver.name:
            initial_approver.name = user_full_name or user_email
            initial_approver.save(update_fields=["name"])

        try:
            ApprovalWorkflowService().initialize_approval_flow(
                new_instance, initial_approver
            )
        except ValueError as exc:
            raise HttpError(400, str(exc)) from exc

    return JsonResponse(serialize_supplier(new_instance), status=201)


@router.get("/suppliers/{pk}/", url_name="supplier-detail-v1")
def get_supplier(request, pk: int):
    """Get supplier details by id."""
    supplier = get_object_or_404(Supplier, pk=pk)
    return serialize_supplier(supplier)


@router.put("/suppliers/{pk}/", url_name="supplier-update-v1")
def put_supplier(request, pk: int, payload: SupplierUpdateIn):
    """Update a supplier with full payload semantics."""
    supplier = get_object_or_404(Supplier, pk=pk)
    updated = apply_supplier_payload(supplier, payload)
    return serialize_supplier(updated)


@router.patch("/suppliers/{pk}/", url_name="supplier-partial-update-v1")
def patch_supplier(request, pk: int, payload: SupplierUpdateIn):
    """Partially update a supplier."""
    supplier = get_object_or_404(Supplier, pk=pk)
    updated = apply_supplier_payload(supplier, payload)
    return serialize_supplier(updated)


@router.delete("/suppliers/{pk}/", url_name="supplier-delete-v1")
def delete_supplier(request, pk: int):
    """Delete a supplier by id."""
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return HttpResponse(status=204)


@router.get("/suppliers-list/", url_name="supplier-list-v1")
def list_suppliers(
    request,
    page: int = 1,
    size: int = 12,
    search: Optional[str] = None,
) -> JsonResponse:
    """List suppliers with filters, search, and pagination."""
    queryset = Supplier.objects.all()
    filtered_qs = SupplierFilters(request.GET, queryset=queryset).qs

    if search:
        search_filter = Q(trade_name__icontains=search)
        search_filter.add(Q(legal_name__icontains=search), Q.OR)
        search_filter.add(Q(tax_id__icontains=search), Q.OR)
        filtered_qs = filtered_qs.filter(search_filter)

    filtered_qs = filtered_qs.order_by("id")
    return JsonResponse(
        paginate(request, filtered_qs, page, size, serialize_supplier),
        status=200,
    )
