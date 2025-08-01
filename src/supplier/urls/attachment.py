"""
URL patterns for supplier attachment-related views.
"""

from django.urls import path

from src.supplier.views.attachment import (
    SupplierAttachmentDownloadView,
    SupplierAttachmentListView,
    SupplierAttachmentTypeView,
    SupplierAttachmentUploadView,
)

urlpatterns = [
    path(
        "attachments-list/<int:supplier_id>/",
        SupplierAttachmentListView.as_view(),
        name="supplier-attachment-list",
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
        "attachment-types/",
        SupplierAttachmentTypeView.as_view(),
        name="supplier-attachment-type",
    ),
]
