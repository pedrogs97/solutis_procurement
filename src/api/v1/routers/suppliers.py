"""Supplier endpoints for Ninja API v1."""
# pylint: disable=duplicate-code

from typing import Optional

from django.core.paginator import EmptyPage, Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError

from src.api.v1.pagination import build_page_link
from src.api.v1.schemas.suppliers import (
    SupplierCreateIn,
    SupplierListOut,
    SupplierUpdateIn,
    apply_supplier_payload,
    serialize_supplier,
)
from src.supplier.filters.supplier import SupplierFilters
from src.supplier.models.approval_workflow import Approver
from src.supplier.models.supplier import Supplier
from src.supplier.services.approval_workflow import ApprovalWorkflowService

router = Router(tags=["suppliers"])


def _paginate(request, queryset, page: int, size: int):
    paginator = Paginator(queryset, size)
    try:
        current_page = paginator.page(page)
    except EmptyPage:
        current_page = (
            paginator.page(paginator.num_pages) if paginator.num_pages else []
        )

    results = (
        [serialize_supplier(item) for item in current_page.object_list]
        if paginator.count
        else []
    )

    return SupplierListOut(
        count=paginator.count,
        next=build_page_link(
            request,
            current_page.next_page_number() if current_page.has_next() else None,
            size,
        )
        if paginator.count
        else None,
        previous=build_page_link(
            request,
            current_page.previous_page_number()
            if current_page.has_previous()
            else None,
            size,
        )
        if paginator.count
        else None,
        results=results,
    ).model_dump(by_alias=True)


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
            {
                "detail": "UsuÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¡rio autenticado sem e-mail para iniciar aprovaÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â§ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â£o."
            },
            status=403,
        )

    with transaction.atomic():
        try:
            new_instance = apply_supplier_payload(None, payload)
        except Exception as exc:  # pragma: no cover - defensive fallback
            raise HttpError(400, str(exc)) from exc

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
            raise HttpError(400, {"approvalWorkflow": [str(exc)]}) from exc

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
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
):
    """List suppliers with filters, search, and pagination."""
    queryset = Supplier.objects.all()
    filtered_qs = SupplierFilters(request.GET, queryset=queryset).qs

    if search:
        search_filter = Q(trade_name__icontains=search)
        search_filter.add(Q(legal_name__icontains=search), Q.OR)
        search_filter.add(Q(tax_id__icontains=search), Q.OR)
        filtered_qs = filtered_qs.filter(search_filter)

    filtered_qs = filtered_qs.distinct().order_by("id")
    return _paginate(request, filtered_qs, page, size)
