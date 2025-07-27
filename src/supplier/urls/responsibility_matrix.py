"""
URL patterns for responsibility matrix-related views.
"""

from django.urls import path

from src.supplier.views.responsibility_matrix import ResponsibilityMatrixView

urlpatterns = [
    path(
        "responsibility-matrix/",
        ResponsibilityMatrixView.as_view(),
        name="responsibility-matrix",
    ),
    path(
        "responsibility-matrix/<int:pk>/",
        ResponsibilityMatrixView.as_view(),
        name="responsibility-matrix-detail",
    ),
]
