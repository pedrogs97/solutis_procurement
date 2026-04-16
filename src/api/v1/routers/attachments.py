"""Attachment endpoints for Ninja API v1."""

import mimetypes
import os
from typing import Optional

from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from loguru import logger
from ninja import File, Form, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile

from src.api.v1.schemas.attachments import (
    AttachmentTypeCreateIn,
    AttachmentTypePatchIn,
    AttachmentTypeOut,
    AttachmentUploadIn,
    AttachmentVersionOut,
    serialize_attachment,
    serialize_attachment_version,
)
from src.supplier.models.attachments import (
    DomAttachmentType,
    SupplierAttachment,
    SupplierAttachmentHistory,
)
from src.supplier.models.domain import DomRiskLevel
from src.supplier.models.supplier import Supplier

router = Router(tags=["attachments"])

ALLOWED_EXTENSIONS = [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
MAX_FILE_SIZE = 10 * 1024 * 1024


def _validate_upload(payload: AttachmentUploadIn, file: UploadedFile) -> None:
    if not Supplier.objects.filter(pk=payload.supplier).exists():
        raise HttpError(400, "Fornecedor nao encontrado.")

    if not DomAttachmentType.objects.filter(pk=payload.attachment_type).exists():
        raise HttpError(400, "Tipo de anexo nao encontrado.")

    if not file:
        raise HttpError(400, "Arquivo e obrigatorio.")

    if file.size > MAX_FILE_SIZE:
        raise HttpError(400, "Arquivo muito grande. Tamanho maximo: 10MB.")

    if not any(file.name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HttpError(400, "Tipo de arquivo nao permitido.")


def _serialize_attachment_type(item: DomAttachmentType) -> dict:
    return AttachmentTypeOut(
        id=item.id,
        name=item.name,
        risk_level=item.risk_level_id,
    ).model_dump(by_alias=True)


def _validate_risk_level(risk_level_id: Optional[int]) -> None:
    if risk_level_id is None:
        return
    if not DomRiskLevel.objects.filter(pk=risk_level_id).exists():
        raise HttpError(400, "Nivel de risco nao encontrado.")


@router.get("/attachments-list/{supplier_id}/", url_name="supplier-attachment-list-v1")
def list_attachments(request, supplier_id: int):
    """List attachments for a supplier."""
    queryset = SupplierAttachment.objects.filter(
        supplier_id=supplier_id
    ).select_related("attachment_type")
    return [serialize_attachment(item) for item in queryset]


@router.post("/attachments/upload/", url_name="supplier-attachment-upload-v1")
def upload_attachment(
    request,
    supplier: int = Form(...),
    attachment_type: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadedFile = File(...),
):
    """Upload or replace a supplier attachment."""
    if attachment_type is None:
        raw_attachment_type = request.POST.get("attachmentType")
        attachment_type = int(raw_attachment_type) if raw_attachment_type else None
    if attachment_type is None:
        raise HttpError(400, "attachmentType: este campo e obrigatorio.")

    payload = AttachmentUploadIn(
        supplier=supplier,
        attachment_type=attachment_type,
        description=description,
    )
    _validate_upload(payload, file)

    with transaction.atomic():
        existing = (
            SupplierAttachment.objects.select_for_update()
            .filter(
                supplier_id=payload.supplier,
                attachment_type_id=payload.attachment_type,
            )
            .first()
        )

        if existing:
            if existing.file:
                SupplierAttachmentHistory.objects.create(
                    supplier_id=existing.supplier_id,
                    attachment_type_id=existing.attachment_type_id,
                    file=existing.file.name,
                    description=existing.description,
                    source_attachment=existing,
                )
            existing.description = payload.description
            existing.file = file
            existing.save()
            created = existing
        else:
            created = SupplierAttachment.objects.create(
                supplier_id=payload.supplier,
                attachment_type_id=payload.attachment_type,
                description=payload.description,
                file=file,
            )

    return JsonResponse(serialize_attachment(created), status=201)


@router.get(
    "/attachments/history/{supplier_id}/{attachment_type_id}/",
    url_name="supplier-attachment-history-v1",
)
def list_attachment_history(request, supplier_id: int, attachment_type_id: int):
    """List full attachment version history for supplier and attachment type."""
    current = (
        SupplierAttachment.objects.filter(
            supplier_id=supplier_id,
            attachment_type_id=attachment_type_id,
        )
        .select_related("attachment_type")
        .first()
    )

    history = SupplierAttachmentHistory.objects.filter(
        supplier_id=supplier_id,
        attachment_type_id=attachment_type_id,
    ).order_by("-created_at")

    versions = [
        serialize_attachment_version(item, is_current=False) for item in history
    ]
    if current:
        versions.insert(0, serialize_attachment_version(current, is_current=True))

    return [AttachmentVersionOut(**item).model_dump(by_alias=True) for item in versions]


@router.get(
    "/attachments/history-download/{pk}/",
    url_name="supplier-attachment-history-download-v1",
)
def download_attachment_history(request, pk: int):
    """Download an attachment file from history."""
    attachment = get_object_or_404(SupplierAttachmentHistory, pk=pk)

    if not attachment.file:
        return JsonResponse({"detail": "Arquivo nao encontrado"}, status=404)

    try:
        content_type, _ = mimetypes.guess_type(attachment.file.name)
        if not content_type:
            content_type = "application/octet-stream"

        filename = attachment.file_name or "download"
        return FileResponse(
            attachment.file.open("rb"),
            content_type=content_type,
            as_attachment=True,
            filename=filename,
        )
    except Exception:  # pragma: no cover - file IO branch
        logger.exception("Falha ao baixar anexo historico", extra={"history_id": pk})
        return JsonResponse({"detail": "Erro interno ao baixar arquivo."}, status=500)


@router.get("/attachments/{pk}/download/", url_name="supplier-attachment-download-v1")
def download_attachment(request, pk: int):
    """Download an attachment file."""
    attachment = get_object_or_404(SupplierAttachment, pk=pk)

    if not attachment.file:
        return JsonResponse({"detail": "Arquivo nao encontrado"}, status=404)

    if attachment.storage_path and not os.path.exists(attachment.storage_path):
        return JsonResponse({"detail": "Arquivo nao existe no servidor"}, status=404)

    try:
        content_type, _ = mimetypes.guess_type(attachment.file.name)
        if not content_type:
            content_type = "application/octet-stream"

        filename = attachment.file_name or "download"
        return FileResponse(
            attachment.file.open("rb"),
            content_type=content_type,
            as_attachment=True,
            filename=filename,
        )
    except Exception:  # pragma: no cover - file IO branch
        logger.exception("Falha ao baixar anexo", extra={"attachment_id": pk})
        return JsonResponse({"detail": "Erro interno ao baixar arquivo."}, status=500)


@router.get("/attachment-types/", url_name="supplier-attachment-type-v1")
def list_attachment_types(request):
    """List attachment types optionally filtered by risk level."""
    queryset = DomAttachmentType.objects.select_related("risk_level").all()
    risk_level = request.GET.get("risk_level")
    if risk_level:
        queryset = queryset.filter(
            Q(risk_level=risk_level) | Q(risk_level__isnull=True)
        )
    return [_serialize_attachment_type(item) for item in queryset]


@router.get("/attachment-types/{pk}/", url_name="supplier-attachment-type-detail-v1")
def get_attachment_type(request, pk: int):
    """Get a single attachment type by id."""
    attachment_type = get_object_or_404(
        DomAttachmentType.objects.select_related("risk_level"),
        pk=pk,
    )
    return _serialize_attachment_type(attachment_type)


@router.post("/attachment-types/", url_name="supplier-attachment-type-create-v1")
def create_attachment_type(request, payload: AttachmentTypeCreateIn):
    """Create an attachment type."""
    data = payload.model_dump(by_alias=False, exclude_none=False)
    risk_level_id = data.pop("risk_level", None)
    _validate_risk_level(risk_level_id)
    data["risk_level_id"] = risk_level_id

    created = DomAttachmentType.objects.create(**data)
    return JsonResponse(_serialize_attachment_type(created), status=201)


@router.patch("/attachment-types/{pk}/", url_name="supplier-attachment-type-update-v1")
def patch_attachment_type(request, pk: int, payload: AttachmentTypePatchIn):
    """Partially update an attachment type."""
    attachment_type = get_object_or_404(DomAttachmentType, pk=pk)

    data = payload.model_dump(by_alias=False, exclude_unset=True)
    if "risk_level" in data:
        _validate_risk_level(data["risk_level"])
        data["risk_level_id"] = data.pop("risk_level")

    for key, value in data.items():
        setattr(attachment_type, key, value)
    attachment_type.save()

    return _serialize_attachment_type(attachment_type)


@router.delete(
    "/attachment-types/{pk}/",
    url_name="supplier-attachment-type-delete-v1",
)
def delete_attachment_type(request, pk: int):
    """Delete an attachment type."""
    attachment_type = get_object_or_404(DomAttachmentType, pk=pk)
    try:
        attachment_type.delete()
    except ProtectedError as exc:
        raise HttpError(
            400,
            "Nao e possivel excluir o tipo de anexo pois ele esta em uso.",
        ) from exc
    return HttpResponse(status=204)
