"""
Serializer for Evaluation models output.
This module provides serializers for output representations of supplier evaluation models.
"""

from django.db.models import Avg, Max, Min
from rest_framework import serializers

from src.shared.serializers import BaseSerializer
from src.supplier.models.evaluation import (
    CriterionScore,
    EvaluationCriterion,
    EvaluationPeriod,
    SupplierEvaluation,
)
from src.supplier.serializers.outbound.supplier import SupplierOutSerializer


class EvaluationCriterionSerializer(BaseSerializer):
    """
    Serializer for EvaluationCriterion model output.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the EvaluationCriterion model serializer.
        """

        model = EvaluationCriterion
        fields = ["id", "name", "description", "weight", "order"]


class EvaluationPeriodSerializer(BaseSerializer):
    """
    Serializer for EvaluationPeriod model output.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the EvaluationPeriod model serializer.
        """

        model = EvaluationPeriod
        fields = ["id", "name", "start_date", "end_date", "year", "period_number"]


class CriterionScoreSerializer(BaseSerializer):
    """
    Serializer for CriterionScore model output.
    Converts field names to camelCase representation.
    """

    criterion = EvaluationCriterionSerializer(read_only=True)

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the CriterionScore model serializer.
        """

        model = CriterionScore
        fields = ["id", "criterion", "score", "comments"]


class SupplierEvaluationSerializer(BaseSerializer):
    """
    Serializer for SupplierEvaluation model output.
    Converts field names to camelCase representation.
    """

    supplier = SupplierOutSerializer(read_only=True)
    period = EvaluationPeriodSerializer(read_only=True)

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the SupplierEvaluation model serializer.
        """

        model = SupplierEvaluation
        fields = (
            "id",
            "supplier",
            "period",
            "evaluator_name",
            "evaluation_date",
            "comments",
            "final_score",
        )


class SupplierEvaluationDetailSerializer(BaseSerializer):
    """
    Serializer for detailed SupplierEvaluation model output.
    Includes all related data for a comprehensive view.
    """

    period = EvaluationPeriodSerializer(read_only=True)
    supplier = SupplierOutSerializer(read_only=True)
    criterion_scores = CriterionScoreSerializer(many=True, read_only=True)

    # Estatísticas de avaliação
    average_score = serializers.SerializerMethodField()
    criteria_breakdown = serializers.SerializerMethodField()

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the SupplierEvaluationDetail model serializer.
        """

        model = SupplierEvaluation
        fields = "__all__"

    def get_average_score(self, obj):
        """
        Calcula a média das avaliações para este fornecedor.
        """
        supplier_evals = (
            SupplierEvaluation.objects.filter(supplier=obj.supplier)
            .exclude(id=obj.id)
            .exclude(final_score=None)
        )

        if not supplier_evals.exists():
            return {
                "previous_evaluations_count": 0,
                "average": None,
                "min": None,
                "max": None,
            }

        stats = supplier_evals.aggregate(
            avg=Avg("final_score"), min=Min("final_score"), max=Max("final_score")
        )

        return {
            "previous_evaluations_count": supplier_evals.count(),
            "average": stats["avg"],
            "min": stats["min"],
            "max": stats["max"],
        }

    def get_criteria_breakdown(self, obj):
        """
        Retorna uma análise detalhada das pontuações por categoria.
        """
        criteria_groups = {
            "quality": [
                "Qualidade do Produto/Serviço",
                "Atendimento aos Requisitos Técnicos",
            ],
            "delivery": ["Cumprimento de Prazos", "Logística e Entrega"],
            "service": ["Atendimento e Suporte", "Suporte Técnico / Pós-venda"],
            "commercial": ["Preço e Custo-benefício", "Condições de Pagamento"],
            "management": [
                "Conformidade Documental",
                "Comprometimento do Fornecedor",
                "Flexibilidade e Adaptação",
            ],
        }

        result = {}
        scores = obj.criterion_scores.all()

        if not scores:
            return result

        # Calcula médias por grupo
        for group_key, criteria_names in criteria_groups.items():
            group_scores = scores.filter(criterion__name__in=criteria_names)
            if group_scores.exists():
                weighted_sum = sum(
                    score.score * score.criterion.weight for score in group_scores
                )
                total_weight = sum(score.criterion.weight for score in group_scores)

                if total_weight > 0:
                    result[group_key] = round(weighted_sum / total_weight, 2)
                else:
                    result[group_key] = None
            else:
                result[group_key] = None

        return result


class EvaluationSummarySerializer(BaseSerializer):
    """
    Serializer for summarizing supplier evaluations.
    Provides an overview of evaluation scores for a supplier across periods.
    """

    period_name = serializers.CharField(source="period.name", read_only=True)
    period_year = serializers.IntegerField(source="period.year", read_only=True)
    period_number = serializers.IntegerField(
        source="period.period_number", read_only=True
    )
    supplier_name = serializers.CharField(source="supplier.legal_name", read_only=True)
    supplier_trade_name = serializers.CharField(
        source="supplier.trade_name", read_only=True
    )

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the EvaluationSummary model serializer.
        """

        model = SupplierEvaluation
        fields = (
            "id",
            "supplier",
            "supplier_name",
            "supplier_trade_name",
            "period_name",
            "period_year",
            "period_number",
            "final_score",
            "evaluation_date",
        )


class SupplierEvaluationHistorySerializer(BaseSerializer):
    """
    Serializer for displaying the history of evaluations for a specific supplier.
    Includes trend analysis and comparison between periods.
    """

    period = EvaluationPeriodSerializer(read_only=True)

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the SupplierEvaluationHistory serializer.
        """

        model = SupplierEvaluation
        fields = (
            "id",
            "period",
            "evaluation_date",
            "evaluator_name",
            "final_score",
            "comments",
        )


class EvaluationCriterionStatsSerializer(BaseSerializer):
    """
    Serializer for displaying statistics about evaluation criteria across suppliers.
    Helps identify common strengths and weaknesses across the supplier base.
    """

    criterion = EvaluationCriterionSerializer(read_only=True)
    average_score = serializers.FloatField()
    min_score = serializers.FloatField()
    max_score = serializers.FloatField()
    evaluations_count = serializers.IntegerField()

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the criterion statistics.
        """

        fields = (
            "criterion",
            "average_score",
            "min_score",
            "max_score",
            "evaluations_count",
        )
