"""
Views for supplier evaluations.
This module provides views for managing supplier evaluations.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.shared.views import BaseAPIView
from src.supplier.filters.evaluation import SupplierEvaluationFilters
from src.supplier.models.evaluation import (
    CriterionScore,
    EvaluationCriterion,
    SupplierEvaluation,
)
from src.supplier.models.supplier import Supplier
from src.supplier.serializers.inbound.evaluation import (
    CriterionScoreInSerializer,
    EvaluationCriterionInSerializer,
    SupplierEvaluationInSerializer,
)
from src.supplier.serializers.outbound.evaluation import (
    CriterionScoreSerializer,
    EvaluationCriterionSerializer,
    EvaluationSummarySerializer,
    SupplierEvaluationDetailSerializer,
    SupplierEvaluationHistorySerializer,
    SupplierEvaluationSerializer,
)


class EvaluationCriterionListViewSet(ListAPIView):
    """
    ViewSet for listing evaluation criteria.
    """

    queryset = EvaluationCriterion.objects.all().order_by("order")
    serializer_class = EvaluationCriterionSerializer


class EvaluationCriterionViewSet(BaseAPIView):
    """
    ViewSet for managing evaluation criteria.
    """

    queryset = EvaluationCriterion.objects.all().order_by("order")
    serializer_class_in = EvaluationCriterionInSerializer
    serializer_class_out = EvaluationCriterionSerializer


class SupplierEvaluationListViewSet(ListAPIView):
    """
    ViewSet for listing evaluation criteria.
    """

    queryset = SupplierEvaluation.objects.all().select_related("supplier", "period")
    serializer_class = SupplierEvaluationSerializer
    filterset_class = SupplierEvaluationFilters


class SupplierEvaluationViewSet(BaseAPIView):
    """
    ViewSet for managing supplier evaluations.
    """

    queryset = SupplierEvaluation.objects.all().select_related("supplier", "period")
    serializer_class_in = SupplierEvaluationInSerializer
    serializer_class_out = SupplierEvaluationSerializer

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Get a summary of all evaluations.
        """
        queryset = self.get_queryset()
        serializer = EvaluationSummarySerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def supplier_history(self, request):
        """
        Get evaluation history for a specific supplier.
        """
        supplier_id = request.query_params.get("supplier")
        if not supplier_id:
            return Response(
                {"message": "É necessário fornecer um ID de fornecedor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supplier = get_object_or_404(Supplier, id=supplier_id)
        evaluations = SupplierEvaluation.objects.filter(supplier=supplier).order_by(
            "-evaluation_date"
        )

        serializer = SupplierEvaluationHistorySerializer(evaluations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_criterion_scores(self, request, pk=None):
        """
        Add criterion scores to an existing evaluation.
        """
        evaluation = self.get_object()
        serializer = CriterionScoreInSerializer(
            data=request.data, many=True, context={"request": request}
        )

        if serializer.is_valid():
            for score_data in serializer.validated_data:
                CriterionScore.objects.create(evaluation=evaluation, **score_data)

            # Recalculate final score
            evaluation.save()

            return Response(
                SupplierEvaluationDetailSerializer(evaluation).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CriterionScoreViewSet(BaseAPIView):
    """
    ViewSet for managing criterion scores.
    """

    queryset = CriterionScore.objects.all().select_related("criterion", "evaluation")
    serializer_class_in = CriterionScoreInSerializer
    serializer_class_out = CriterionScoreSerializer
