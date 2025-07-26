from django.urls import path

from src.supplier.views.attachment import (
    SupplierAttachmentBulkUploadView,
    SupplierAttachmentDownloadView,
    SupplierAttachmentListView,
    SupplierAttachmentUploadView,
    SupplierAttachmentView,
)

urlpatterns = [
    path(
        "attachments-list/",
        SupplierAttachmentListView.as_view(),
        name="supplier-attachment-list",
    ),
    path(
        "attachments/<int:pk>/",
        SupplierAttachmentView.as_view(),
        name="supplier-attachment-detail",
    ),
    path(
        "attachments/<int:pk>/download/",
        SupplierAttachmentDownloadView.as_view(),
        name="supplier-attachment-download",
    ),
    path(
        "attachments/upload/",
        SupplierAttachmentUploadView.as_view(),
        name="supplier-attachment-upload",
    ),
    path(
        "attachments/bulk-upload/",
        SupplierAttachmentBulkUploadView.as_view(),
        name="supplier-attachment-bulk-upload",
    ),
]
