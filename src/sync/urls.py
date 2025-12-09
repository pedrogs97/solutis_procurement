"""
URLs relacionadas a sincronização de fornecedores.
"""

from django.urls import path

from src.sync.views import SupplierSyncView

app_name = "sync"

urlpatterns = [
    path("suppliers/", SupplierSyncView.as_view(), name="sync-suppliers"),
]
