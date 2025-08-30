"""
URLs for supplier evaluation endpoints.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from src.supplier.views.evaluation import (
    CriterionScoreViewSet,
    EvaluationCriterionListViewSet,
    EvaluationCriterionViewSet,
    SupplierEvaluationListViewSet,
    SupplierEvaluationViewSet,
)

router = DefaultRouter()
router.register(r"evaluations", SupplierEvaluationViewSet)
router.register(r"scores", CriterionScoreViewSet)

urlpatterns = [
    path(
        "criteria-list/",
        EvaluationCriterionListViewSet.as_view(),
        name="evaluation-criterion-list",
    ),
    path(
        "criteria/<int:pk>/",
        EvaluationCriterionViewSet.as_view(),
        name="evaluation-criterion-detail",
    ),
    path(
        "criteria/",
        EvaluationCriterionViewSet.as_view(),
        name="evaluation-criterion",
    ),
    path(
        "evaluations-list/",
        SupplierEvaluationListViewSet.as_view(),
        name="supplier-evaluation-list",
    ),
]
