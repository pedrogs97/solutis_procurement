"""
Serializer for Evaluation models.
This module provides serializers for input representations of supplier evaluation models.
"""

from typing import Dict

from django.db.transaction import atomic

from src.shared.serializers import BaseSerializer
from src.supplier.models.evaluation import (
    CriterionScore,
    EvaluationCriterion,
    EvaluationPeriod,
    SupplierEvaluation,
)


class EvaluationCriterionInSerializer(BaseSerializer):
    """
    Serializer for EvaluationCriterion model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the EvaluationCriterion model serializer.
        """

        model = EvaluationCriterion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EvaluationPeriodInSerializer(BaseSerializer):
    """
    Serializer for EvaluationPeriod model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the EvaluationPeriod model serializer.
        """

        model = EvaluationPeriod
        fields = "__all__"
        read_only_fields = ("id", "year", "created_at", "updated_at")


class CriterionScoreInSerializer(BaseSerializer):
    """
    Serializer for CriterionScore model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the CriterionScore model serializer.
        """

        model = CriterionScore
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SupplierEvaluationInSerializer(BaseSerializer):
    """
    Serializer for SupplierEvaluation model.
    Converts field names to camelCase representation.
    """

    criterion_scores = CriterionScoreInSerializer(many=True, required=False)

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the SupplierEvaluation model serializer.
        """

        model = SupplierEvaluation
        fields = "__all__"
        read_only_fields = ("id", "final_score", "created_at", "updated_at")

    @atomic
    def create(self, validated_data: Dict) -> SupplierEvaluation:
        """
        Create a new SupplierEvaluation instance with related criterion scores.
        This method handles the creation of related CriterionScore objects.

        Args:
            validated_data (Dict): The validated data for the SupplierEvaluation.
        Returns:
            SupplierEvaluation: The created SupplierEvaluation instance.
        """
        criterion_scores_data = validated_data.pop("criterion_scores", [])

        supplier_evaluation = SupplierEvaluation.objects.create(**validated_data)

        supplier_evaluation.save()
        supplier_evaluation.refresh_from_db()
        CriterionScore.objects.bulk_create(
            [
                CriterionScore(evaluation=supplier_evaluation, **score_data)
                for score_data in criterion_scores_data
            ]
        )

        return supplier_evaluation

    @atomic
    def update(
        self, instance: SupplierEvaluation, validated_data: Dict
    ) -> SupplierEvaluation:
        """
        Update an existing SupplierEvaluation instance with related criterion scores.
        This method handles the update of related CriterionScore objects.

        Args:
            instance (SupplierEvaluation): The existing SupplierEvaluation instance to update.
            validated_data (Dict): The validated data for the SupplierEvaluation.
        Returns:
            SupplierEvaluation: The updated SupplierEvaluation instance.
        """
        criterion_scores_data = validated_data.pop("criterion_scores", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if criterion_scores_data is not None:
            instance.criterion_scores.all().delete()

            CriterionScore.objects.bulk_create(
                [
                    CriterionScore(evaluation=instance, **score_data)
                    for score_data in criterion_scores_data
                ]
            )

        instance.save()

        return instance
