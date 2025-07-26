"""
URL patterns for supplier-related views.
"""

from django.urls import path

from src.supplier.views.supplier import SupplierListView, SupplierView

urlpatterns = [
    path("suppliers/", SupplierView.as_view(), name="supplier"),
    path("suppliers/<int:pk>/", SupplierView.as_view(), name="supplier-detail"),
    path("suppliers-list/", SupplierListView.as_view(), name="supplier-list"),
]
