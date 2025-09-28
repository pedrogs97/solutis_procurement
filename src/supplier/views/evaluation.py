"""
Views for supplier evaluations.
This module provides views for managing supplier evaluations.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
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
    EvaluationCriterionSerializer,
    EvaluationSummarySerializer,
    SupplierEvaluationDetailSerializer,
    SupplierEvaluationHistorySerializer,
    SupplierEvaluationSerializer,
)


class EvaluationCriterionListView(ListAPIView):
    """
    View for listing evaluation criteria.
    """

    queryset = EvaluationCriterion.objects.all().order_by("order")
    serializer_class = EvaluationCriterionSerializer


class EvaluationCriterionView(BaseAPIView):
    """
    View for managing evaluation criteria CRUD operations.
    """

    queryset = EvaluationCriterion.objects.all().order_by("order")
    serializer_class_in = EvaluationCriterionInSerializer
    serializer_class_out = EvaluationCriterionSerializer


class SupplierEvaluationListView(ListAPIView):
    """
    View for listing supplier evaluations.
    """

    queryset = SupplierEvaluation.objects.all().select_related("supplier", "period")
    serializer_class = SupplierEvaluationSerializer
    filterset_class = SupplierEvaluationFilters


class SupplierEvaluationView(BaseAPIView):
    """
    View for managing supplier evaluations CRUD operations.
    """

    queryset = SupplierEvaluation.objects.all().select_related("supplier", "period")
    serializer_class_in = SupplierEvaluationInSerializer
    serializer_class_out = SupplierEvaluationSerializer

    def get(self, request, pk=None, *args, **kwargs):
        """
        Get a single evaluation with detailed information or handle list.
        """
        if pk:
            instance = self.get_object()
            serializer = SupplierEvaluationDetailSerializer(instance)
            return Response(serializer.data)
        return super().get(request, *args, **kwargs)


class EvaluationSummaryView(BaseAPIView):
    """
    View for getting evaluation summaries.
    """

    def get(self, request, *args, **kwargs):
        """
        Get a summary of all evaluations.
        """
        queryset = SupplierEvaluation.objects.all().select_related("supplier", "period")
        serializer = EvaluationSummarySerializer(queryset, many=True)
        return Response(serializer.data)


class SupplierHistoryView(BaseAPIView):
    """
    View for getting supplier evaluation history.
    """

    def get(self, request, *args, **kwargs):
        """
        Get evaluation history for a specific supplier.
        """
        supplier_id = request.query_params.get("supplier")
        if not supplier_id:
            return Response(
                {"message": "É necessário fornecer um ID de fornecedor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supplier = get_object_or_404(Supplier, pk=supplier_id)
        evaluations = SupplierEvaluation.objects.filter(supplier=supplier).order_by(
            "-evaluation_date"
        )

        serializer = SupplierEvaluationHistorySerializer(evaluations, many=True)
        return Response(serializer.data)


class AddCriterionScoresView(BaseAPIView):
    """
    View for adding criterion scores to an evaluation.
    """

    def post(self, request, evaluation_id, *args, **kwargs):
        """
        Add criterion scores to an existing evaluation.
        """
        evaluation = get_object_or_404(SupplierEvaluation, pk=evaluation_id)
        serializer = CriterionScoreInSerializer(
            data=request.data, many=True, context={"request": request}
        )

        if serializer.is_valid():
            for score_data in serializer.validated_data:
                CriterionScore.objects.create(evaluation=evaluation, **score_data)

            evaluation.save()

            return Response(
                SupplierEvaluationDetailSerializer(evaluation).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
