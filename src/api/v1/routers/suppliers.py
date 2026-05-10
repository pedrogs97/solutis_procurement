"""Supplier endpoints for Ninja API v1."""

from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from loguru import logger
from ninja import Query, Router, Status
from ninja.errors import HttpError

from src.api.v1.controllers.suppliers import (
    apply_supplier_payload,
    serialize_supplier_list,
)
from src.api.v1.filters.suppliers import SupplierListFilters
from src.api.v1.pagination import paginate
from src.api.v1.schemas.common import ErrorOut
from src.api.v1.schemas.suppliers import (
    PaginatedSupplierListOut,
    SupplierCreateIn,
    SupplierOut,
    SupplierUpdateIn,
    serialize_supplier,
)
from src.supplier.models.approval_workflow import Approver
from src.supplier.models.supplier import Supplier
from src.supplier.services.approval_workflow import ApprovalWorkflowService

router = Router(tags=["suppliers"])

_SUPPLIER_UNIQUE_FIELD_ERRORS = {
    "tax_id": ("taxId", "CPF/CNPJ já cadastrado."),
    "legal_name": ("legalName", "Razão Social já cadastrada."),
}


def _supplier_integrity_error_response(exc: IntegrityError) -> JsonResponse:
    """Return a 400 with field-level error for known unique constraint violations."""
    error_text = str(exc).lower()
    for db_field, (api_field, message) in _SUPPLIER_UNIQUE_FIELD_ERRORS.items():
        if db_field in error_text:
            return JsonResponse(
                {"detail": "Dados inválidos.", "errors": [{"field": api_field, "message": message}]},
                status=400,
            )
    return JsonResponse({"detail": "Dados do fornecedor invalidos."}, status=400)


@router.post(
    "/suppliers/",
    response={201: SupplierOut, 400: ErrorOut, 403: ErrorOut, 422: ErrorOut},
    operation_id="createSupplier",
    by_alias=True,
    url_name="supplier-v1",
)
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

    try:
        with transaction.atomic():
            try:
                new_instance = apply_supplier_payload(None, payload)
            except (TypeError, ValueError) as exc:
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

    except IntegrityError as exc:
        logger.exception("Falha ao criar fornecedor — IntegrityError")
        return _supplier_integrity_error_response(exc)

    return Status(201, serialize_supplier(new_instance))


@router.get(
    "/suppliers/{pk}/",
    response={200: SupplierOut, 404: ErrorOut},
    operation_id="getSupplier",
    by_alias=True,
    url_name="supplier-detail-v1",
)
def get_supplier(request, pk: int):
    """Get supplier details by id."""
    supplier = get_object_or_404(Supplier, pk=pk)
    return serialize_supplier(supplier)


@router.put(
    "/suppliers/{pk}/",
    response={200: SupplierOut, 400: ErrorOut, 404: ErrorOut, 422: ErrorOut},
    operation_id="updateSupplier",
    by_alias=True,
    url_name="supplier-update-v1",
)
def put_supplier(request, pk: int, payload: SupplierUpdateIn):
    """Update a supplier with full payload semantics."""
    supplier = get_object_or_404(Supplier, pk=pk)
    try:
        updated = apply_supplier_payload(supplier, payload)
    except IntegrityError as exc:
        logger.exception("Falha ao atualizar fornecedor — IntegrityError")
        return _supplier_integrity_error_response(exc)
    return serialize_supplier(updated)


@router.patch(
    "/suppliers/{pk}/",
    response={200: SupplierOut, 400: ErrorOut, 404: ErrorOut, 422: ErrorOut},
    operation_id="patchSupplier",
    by_alias=True,
    url_name="supplier-partial-update-v1",
)
def patch_supplier(request, pk: int, payload: SupplierUpdateIn):
    """Partially update a supplier."""
    supplier = get_object_or_404(Supplier, pk=pk)
    try:
        updated = apply_supplier_payload(supplier, payload)
    except IntegrityError as exc:
        logger.exception("Falha ao atualizar fornecedor — IntegrityError")
        return _supplier_integrity_error_response(exc)
    return serialize_supplier(updated)


@router.delete(
    "/suppliers/{pk}/",
    response={204: None, 404: ErrorOut},
    operation_id="deleteSupplier",
    url_name="supplier-delete-v1",
)
def delete_supplier(request, pk: int):
    """Delete a supplier by id."""
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return HttpResponse(status=204)


@router.get(
    "/suppliers-list/",
    response={200: PaginatedSupplierListOut, 422: ErrorOut},
    operation_id="listSuppliers",
    by_alias=True,
    url_name="supplier-list-v1",
)
def list_suppliers(
    request,
    filters: Query[SupplierListFilters],
    page: int = 1,
    size: int = 12,
):
    """List suppliers with filters, search, and pagination."""
    filtered_qs = filters.filter(Supplier.objects.all()).order_by("id")
    return paginate(request, filtered_qs, page, size, serialize_supplier_list)
