"""
Serializer for Evaluation models.
This module provides serializers for input representations of supplier evaluation models.
"""

from typing import Dict

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.transaction import atomic
from rest_framework import serializers

from src.shared.serializers import BaseSerializer
from src.supplier.models.evaluation import (
    CriterionScore,
    EvaluationCriterion,
    EvaluationPeriodType,
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
        fields = ["criterion", "score", "comments"]
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

    def validate(self, attrs):
        """
        Validate the supplier evaluation data.
        """
        period_type = attrs.get("period_type")
        period_number = attrs.get("period_number")
        if period_type and period_number is not None:
            valid = (
                period_type == EvaluationPeriodType.QUADRIMESTER
                and period_number in [1, 2, 3]
            ) or (
                period_type == EvaluationPeriodType.SEMESTER and period_number in [1, 2]
            )
            if not valid:
                raise serializers.ValidationError(
                    {
                        "period_number": "Combinação inválida para tipo e número do período."
                    }
                )
        return attrs

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

        try:
            supplier_evaluation = SupplierEvaluation.objects.create(**validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            ) from exc

        CriterionScore.objects.bulk_create(
            [
                CriterionScore(evaluation=supplier_evaluation, **score_data)
                for score_data in criterion_scores_data
            ]
        )
        try:
            supplier_evaluation.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            ) from exc
        supplier_evaluation.refresh_from_db()

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

        try:
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            ) from exc

        return instance
