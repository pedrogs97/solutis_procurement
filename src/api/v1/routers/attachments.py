"""Attachment endpoints for Ninja API v1."""

import mimetypes
import os
from typing import Optional

from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from ninja import File, Form, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile

from src.api.v1.schemas.attachments import (
    AttachmentOut,
    AttachmentTypeOut,
    AttachmentUploadIn,
    serialize_attachment,
)
from src.api.v1.schemas.common import DomainRefOut
from src.supplier.models.attachments import DomAttachmentType, SupplierAttachment
from src.supplier.models.supplier import Supplier

router = Router(tags=["attachments"])

ALLOWED_EXTENSIONS = [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
MAX_FILE_SIZE = 10 * 1024 * 1024


def _validate_upload(payload: AttachmentUploadIn, file: UploadedFile) -> None:
    if not Supplier.objects.filter(pk=payload.supplier).exists():
        raise HttpError(400, {"supplier": ["Fornecedor nÃ£o encontrado."]})

    if not DomAttachmentType.objects.filter(pk=payload.attachment_type).exists():
        raise HttpError(400, {"attachmentType": ["Tipo de anexo nÃ£o encontrado."]})

    if not file:
        raise HttpError(400, {"file": ["Arquivo Ã© obrigatÃ³rio."]})

    if file.size > MAX_FILE_SIZE:
        raise HttpError(400, {"file": ["Arquivo muito grande. Tamanho mÃ¡ximo: 10MB."]})

    if not any(file.name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HttpError(400, {"file": ["Tipo de arquivo nÃ£o permitido."]})


@router.get("/attachments-list/{supplier_id}/", url_name="supplier-attachment-list-v1")
def list_attachments(request, supplier_id: int):
    """List attachments for a supplier."""
    queryset = SupplierAttachment.objects.filter(
        supplier_id=supplier_id
    ).select_related("attachment_type")
    return [
        AttachmentOut.model_validate(serialize_attachment(item)).model_dump(
            by_alias=True
        )
        for item in queryset
    ]


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
        raise HttpError(400, {"attachmentType": ["Este campo Ã© obrigatÃ³rio."]})

    payload = AttachmentUploadIn(
        supplier=supplier,
        attachment_type=attachment_type,
        description=description,
    )
    _validate_upload(payload, file)

    existing = SupplierAttachment.objects.filter(
        supplier_id=payload.supplier,
        attachment_type_id=payload.attachment_type,
    ).first()
    if existing:
        existing.file.delete(save=False)
        existing.delete()

    created = SupplierAttachment.objects.create(
        supplier_id=payload.supplier,
        attachment_type_id=payload.attachment_type,
        description=payload.description,
        file=file,
    )
    return JsonResponse(serialize_attachment(created), status=201)


@router.get("/attachments/{pk}/download/", url_name="supplier-attachment-download-v1")
def download_attachment(request, pk: int):
    """Download an attachment file."""
    attachment = get_object_or_404(SupplierAttachment, pk=pk)

    if not attachment.file:
        return JsonResponse({"error": "Arquivo nÃ£o encontrado"}, status=404)

    if attachment.storage_path and not os.path.exists(attachment.storage_path):
        return JsonResponse({"error": "Arquivo nÃ£o existe no servidor"}, status=404)

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
    except Exception as exc:  # pragma: no cover - file IO branch
        return JsonResponse({"error": f"Erro ao baixar arquivo: {exc}"}, status=500)


@router.get("/attachment-types/", url_name="supplier-attachment-type-v1")
def list_attachment_types(request):
    """List attachment types optionally filtered by risk level."""
    queryset = DomAttachmentType.objects.select_related("risk_level").all()
    risk_level = request.GET.get("risk_level")
    if risk_level:
        queryset = queryset.filter(
            Q(risk_level=risk_level) | Q(risk_level__isnull=True)
        )
    return [
        AttachmentTypeOut(
            id=item.id,
            name=item.name,
            risk_level=DomainRefOut.model_validate(item.risk_level)
            if item.risk_level
            else None,
        ).model_dump(by_alias=True)
        for item in queryset
    ]


@router.get("/attachment-types/{pk}/", url_name="supplier-attachment-type-detail-v1")
def get_attachment_type(request, pk: int):
    """Get a single attachment type by id."""
    attachment_type = get_object_or_404(
        DomAttachmentType.objects.select_related("risk_level"),
        pk=pk,
    )
    return AttachmentTypeOut(
        id=attachment_type.id,
        name=attachment_type.name,
        risk_level=DomainRefOut.model_validate(attachment_type.risk_level)
        if attachment_type.risk_level
        else None,
    ).model_dump(by_alias=True)
