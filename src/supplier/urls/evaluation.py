"""
URLs for supplier evaluation endpoints.
"""

from django.urls import path

from src.supplier.views.evaluation import (
    AddCriterionScoresView,
    EvaluationCriterionListView,
    EvaluationCriterionView,
    EvaluationSummaryView,
    SupplierEvaluationListView,
    SupplierEvaluationView,
    SupplierHistoryView,
)

urlpatterns = [
    # Evaluation Criteria
    path(
        "criteria-list/",
        EvaluationCriterionListView.as_view(),
        name="evaluation-criterion-list",
    ),
    path(
        "criteria/<int:pk>/",
        EvaluationCriterionView.as_view(),
        name="evaluation-criterion-detail",
    ),
    path(
        "criteria/",
        EvaluationCriterionView.as_view(),
        name="evaluation-criterion",
    ),
    # Supplier Evaluations
    path(
        "evaluations-list/",
        SupplierEvaluationListView.as_view(),
        name="supplier-evaluation-list",
    ),
    path(
        "evaluations/<int:pk>/",
        SupplierEvaluationView.as_view(),
        name="supplier-evaluation-detail",
    ),
    path(
        "evaluations/",
        SupplierEvaluationView.as_view(),
        name="supplier-evaluation",
    ),
    # Special Actions
    path(
        "summary/",
        EvaluationSummaryView.as_view(),
        name="supplier-evaluation-summary",
    ),
    path(
        "supplier-history/",
        SupplierHistoryView.as_view(),
        name="supplier-evaluation-supplier-history",
    ),
    path(
        "evaluations/<int:evaluation_id>/scores/",
        AddCriterionScoresView.as_view(),
        name="supplier-evaluation-add-criterion-scores",
    ),
]
