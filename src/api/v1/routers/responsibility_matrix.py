"""Responsibility matrix endpoints for Ninja API v1."""

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from src.api.v1.request import get_request_data
from src.api.v1.schemas.responsibility_matrix import (
    ResponsibilityMatrixIn,
    serialize_responsibility_matrix,
)
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import Supplier
from src.utils.parse import to_snake_case

router = Router(tags=["responsibility-matrix"])


def _get_matrix_by_supplier_id(supplier_id: int) -> ResponsibilityMatrix:
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    if (
        not hasattr(supplier, "responsibility_matrix")
        or not supplier.responsibility_matrix
    ):
        raise Http404
    return supplier.responsibility_matrix


def _update_matrix(instance: ResponsibilityMatrix, data: dict):
    matrix_fields = {
        field.name for field in ResponsibilityMatrix._meta.fields
    }  # pylint: disable=protected-access
    for key, value in data.items():
        if key in {"supplier"}:
            continue
        normalized_key = key if key in matrix_fields else to_snake_case(key)
        if normalized_key in matrix_fields:
            setattr(instance, normalized_key, value)
    instance.save()
    return instance


@router.post("/responsibility-matrix/", url_name="responsibility-matrix-v1")
def create_responsibility_matrix(request):
    """Create a responsibility matrix for a supplier."""
    raw_data = get_request_data(request)
    payload = ResponsibilityMatrixIn.model_validate(raw_data)
    if not payload.supplier:
        raise HttpError(400, {"supplier": ["Este campo é obrigatório."]})

    supplier = get_object_or_404(Supplier, pk=payload.supplier)
    if hasattr(supplier, "responsibility_matrix") and supplier.responsibility_matrix:
        raise HttpError(
            400, "Matriz de responsabilidade já existe para este fornecedor."
        )

    matrix = ResponsibilityMatrix.objects.create(supplier=supplier)
    matrix = _update_matrix(matrix, raw_data)
    return JsonResponse(serialize_responsibility_matrix(matrix), status=201)


@router.get("/responsibility-matrix/{pk}/", url_name="responsibility-matrix-detail-v1")
def get_responsibility_matrix(request, pk: int):
    """Retrieve a supplier responsibility matrix."""
    matrix = _get_matrix_by_supplier_id(pk)
    return serialize_responsibility_matrix(matrix)


@router.put("/responsibility-matrix/{pk}/", url_name="responsibility-matrix-update-v1")
def put_responsibility_matrix(request, pk: int):
    """Fully update a supplier responsibility matrix."""
    raw_data = get_request_data(request)
    ResponsibilityMatrixIn.model_validate(raw_data)
    matrix = _get_matrix_by_supplier_id(pk)
    updated = _update_matrix(matrix, raw_data)
    return serialize_responsibility_matrix(updated)


@router.patch(
    "/responsibility-matrix/{pk}/", url_name="responsibility-matrix-partial-v1"
)
def patch_responsibility_matrix(request, pk: int):
    """Partially update a supplier responsibility matrix."""
    raw_data = get_request_data(request)
    ResponsibilityMatrixIn.model_validate(raw_data)
    matrix = _get_matrix_by_supplier_id(pk)
    updated = _update_matrix(matrix, raw_data)
    return serialize_responsibility_matrix(updated)
