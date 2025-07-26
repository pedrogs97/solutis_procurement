import mimetypes
import os

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from src.shared.views import BaseAPIView
from src.supplier.filters import SupplierAttachmentFilters
from src.supplier.models.attachments import SupplierAttachment
from src.supplier.serializers.inbound.attachment import SupplierAttachmentInSerializer
from src.supplier.serializers.outbound.attachment import SupplierAttachmentOutSerializer


class SupplierAttachmentView(BaseAPIView):
    """
    A view for handling supplier attachment CRUD operations.
    """

    queryset = SupplierAttachment.objects.all()
    serializer_class_out = SupplierAttachmentOutSerializer
    serializer_class_in = SupplierAttachmentInSerializer
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        """
        Replace an existing attachment file completely.
        """
        attachment = self.get_object()

        # Remove o arquivo anterior se existir
        if attachment.file:
            try:
                attachment.file.delete(save=False)
            except Exception:
                pass  # Ignora erros ao deletar arquivo anterior

        serializer = self.get_serializer(attachment, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_attachment = serializer.save()

        return_data = self.serializer_class_out(updated_attachment).data
        return Response(return_data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Update attachment metadata or replace file.
        PATCH /api/supplier-attachments/{id}/
        """
        attachment = self.get_object()

        # Se um novo arquivo foi enviado, remove o anterior
        if "file" in request.data and attachment.file:
            try:
                attachment.file.delete(save=False)
            except Exception:
                pass  # Ignora erros ao deletar arquivo anterior

        serializer = self.get_serializer(attachment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_attachment = serializer.save()

        return_data = self.serializer_class_out(updated_attachment).data
        return Response(return_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Delete attachment and its file.
        DELETE /api/supplier-attachments/{id}/
        """
        attachment = self.get_object()

        # Remove o arquivo do sistema de arquivos
        if attachment.file:
            try:
                attachment.file.delete(save=False)
            except Exception:
                pass  # Ignora erros ao deletar arquivo

        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupplierAttachmentListView(ListAPIView):
    """
    A view to list all supplier attachments with filtering support.
    GET /api/supplier-attachments/
    """

    queryset = SupplierAttachment.objects.all()
    serializer_class = SupplierAttachmentOutSerializer
    filterset_class = SupplierAttachmentFilters
    search_fields = ["description", "file", "attachment_type__name"]
    ordering_fields = ["created_at", "updated_at", "attachment_type"]
    ordering = ["-created_at"]


class SupplierAttachmentUploadView(BaseAPIView):
    """
    Specialized view for file upload operations.
    """

    queryset = SupplierAttachment.objects.all()
    serializer_class_out = SupplierAttachmentOutSerializer
    serializer_class_in = SupplierAttachmentInSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, supplier_id=None, *args, **kwargs):
        """
        Upload a new attachment file.
        POST /api/supplier-attachments/upload/
        POST /api/suppliers/{supplier_id}/attachments/
        """
        # Adiciona o supplier_id aos dados se fornecido na URL
        data = request.data.copy()
        if supplier_id:
            data["supplier"] = supplier_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save()

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


class SupplierAttachmentBulkUploadView(APIView):
    """
    View for bulk upload of attachments.
    """

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """
        Upload multiple attachments at once.
        POST /api/supplier-attachments/bulk-upload/

        Expected format:
        {
            "attachments": [
                {
                    "supplier": 1,
                    "attachment_type": 1,
                    "file": file1,
                    "description": "Description 1"
                },
                {
                    "supplier": 1,
                    "attachment_type": 2,
                    "file": file2,
                    "description": "Description 2"
                }
            ]
        }
        """
        attachments_data = request.data.get("attachments", [])

        if not attachments_data:
            return Response(
                {"error": "Campo 'attachments' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_attachments = []
        errors = []

        for i, attachment_data in enumerate(attachments_data):
            serializer = SupplierAttachmentInSerializer(data=attachment_data)
            if serializer.is_valid():
                attachment = serializer.save()
                created_attachments.append(
                    SupplierAttachmentOutSerializer(attachment).data
                )
            else:
                errors.append({"index": i, "errors": serializer.errors})

        response_data = {
            "created": created_attachments,
            "errors": errors,
            "total_created": len(created_attachments),
            "total_errors": len(errors),
        }

        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

        return Response(response_data, status=status.HTTP_201_CREATED)
