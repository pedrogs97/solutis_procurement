"""
URL configuration for supplier app.
This module aggregates all URL patterns for the supplier application.
"""

from django.urls import include, path

app_name = "supplier"

urlpatterns = [
    path("attachments/", include("src.supplier.urls.attachment")),
    path("responsibility-matrix/", include("src.supplier.urls.responsibility_matrix")),
    path("suppliers/", include("src.supplier.urls.supplier")),
    path("domain/", include("src.supplier.urls.domain")),
    path("evaluations/", include("src.supplier.urls.evaluation")),
]
