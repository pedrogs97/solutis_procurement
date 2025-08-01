"""
View for handling supplier attachments in a procurement service.
This module provides views for creating, updating, deleting, listing, downloading,
"""

import mimetypes
import os

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from src.shared.views import BaseAPIView
from src.supplier.models.attachments import SupplierAttachment
from src.supplier.serializers.inbound.attachment import (
    SupplierAttachmentInSerializer,
    SupplierAttachmentTypeSerializer,
)
from src.supplier.serializers.outbound.attachment import SupplierAttachmentOutSerializer
from src.supplier.services.attachment import AttachmentService


class SupplierAttachmentListView(ListAPIView):
    """
    A view to list all supplier attachments.
    """

    queryset = SupplierAttachment.objects.all()
    serializer_class = SupplierAttachmentOutSerializer

    def get(self, request, supplier_id=None, *args, **kwargs):
        """
        Handle GET requests for listing attachments.
        If `supplier_id` is provided, filter attachments by supplier.
        """
        queryset = self.get_queryset()

        if not supplier_id:
            return Response(
                {"error": "supplier_id is required for this endpoint"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.filter(supplier_id=supplier_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SupplierAttachmentUploadView(CreateAPIView):
    """
    Specialized view for file upload operations.
    """

    queryset = SupplierAttachment.objects.all()
    serializer_class_out = SupplierAttachmentOutSerializer
    serializer_class = SupplierAttachmentInSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """
        Upload a new attachment file.
        """
        attachment = AttachmentService.create_attachment(
            serializer_class=self.get_serializer_class(),
            data=request.data,
        )

        return_data = self.serializer_class_out(attachment).data
        return Response(return_data, status=status.HTTP_201_CREATED)


class SupplierAttachmentDownloadView(APIView):
    """
    View for downloading attachment files.
    """

    def get(self, request, pk):
        """
        Download the attachment file.
        GET /api/supplier-attachments/{id}/download/
        """
        attachment = get_object_or_404(SupplierAttachment, pk=pk)

        if not attachment.file:
            return Response(
                {"error": "Arquivo não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Verifica se o arquivo existe no sistema de arquivos
            if attachment.storage_path and not os.path.exists(attachment.storage_path):
                return Response(
                    {"error": "Arquivo não existe no servidor"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Determina o tipo de conteúdo
            content_type, _ = mimetypes.guess_type(attachment.file.name)
            if not content_type:
                content_type = "application/octet-stream"

            # Nome do arquivo para download
            filename = attachment.file_name or "download"

            # Retorna o arquivo
            response = FileResponse(
                attachment.file.open("rb"),
                content_type=content_type,
                as_attachment=True,
                filename=filename,
            )
            return response

        except Exception as e:
            return Response(
                {"error": f"Erro ao baixar arquivo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SupplierAttachmentTypeView(BaseAPIView):
    """
    View for handling supplier attachment types.
    """

    serializer_class = SupplierAttachmentTypeSerializer
