"""Supplier endpoints for Ninja API v1."""

from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from loguru import logger
from ninja import Query, Router
from ninja.errors import HttpError

from src.api.v1.controllers.suppliers import (
    apply_supplier_payload,
    serialize_supplier_list,
)
from src.api.v1.filters.suppliers import SupplierListFilters
from src.api.v1.pagination import paginate
from src.api.v1.schemas.suppliers import (
    SupplierCreateIn,
    SupplierUpdateIn,
    serialize_supplier,
)
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
    filters: Query[SupplierListFilters],
    page: int = 1,
    size: int = 12,
) -> JsonResponse:
    """List suppliers with filters, search, and pagination."""
    filtered_qs = filters.filter(Supplier.objects.all()).order_by("id")
    return JsonResponse(
        paginate(request, filtered_qs, page, size, serialize_supplier_list),
        status=200,
    )
