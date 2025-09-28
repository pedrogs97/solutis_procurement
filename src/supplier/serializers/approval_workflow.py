"""
Serializadores para fluxo de aprovação de fornecedores.
"""

from rest_framework import serializers

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    Approver,
    StepApproval,
)


class ApprovalStepSerializer(serializers.ModelSerializer):
    """Serializer para os passos de aprovação."""

    class Meta:
        """Meta dados do serializer."""

        model = ApprovalStep
        fields = [
            "id",
            "name",
            "description",
            "order",
            "department",
            "is_mandatory",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ApproverSerializer(serializers.ModelSerializer):
    """Serializer para aprovadores."""

    class Meta:
        """Meta dados do serializer."""

        model = Approver
        fields = [
            "id",
            "name",
            "email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StepApprovalSerializer(serializers.ModelSerializer):
    """Serializer para aprovações de passos."""

    step_name = serializers.CharField(source="step.name", read_only=True)
    step_department = serializers.CharField(source="step.department", read_only=True)
    approver_detail = ApproverSerializer(source="approver", read_only=True)

    class Meta:
        """Meta dados do serializer."""

        model = StepApproval
        fields = [
            "id",
            "step",
            "step_name",
            "step_department",
            "approver",
            "approver_detail",
            "approval_date",
            "comments",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ApprovalFlowSerializer(serializers.ModelSerializer):
    """Serializer para fluxos de aprovação."""

    current_step_detail = ApprovalStepSerializer(source="current_step", read_only=True)
    step_approvals = StepApprovalSerializer(many=True, read_only=True)

    class Meta:
        """Meta dados do serializer."""

        model = ApprovalFlow
        fields = [
            "id",
            "supplier",
            "is_completed",
            "start_date",
            "completion_date",
            "current_step",
            "current_step_detail",
            "step_approvals",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_completed",
            "completion_date",
        ]


class ApproveStepSerializer(serializers.Serializer):
    """Serializer para aprovar ou rejeitar um passo do fluxo."""

    approver_name = serializers.CharField(max_length=255)
    approver_email = serializers.EmailField()
    comments = serializers.CharField(required=False, allow_blank=True)
    is_approved = serializers.BooleanField(default=True)

    def validate(self, attrs):
        """Validação geral do serializer."""
        approver_name = attrs.get("approver_name")
        approver_email = attrs.get("approver_email")

        if approver_name and approver_email:
            approver, _ = Approver.objects.get_or_create(
                email=approver_email, defaults={"name": approver_name}
            )
            attrs["approver"] = approver

            attrs.pop("approver_name", None)
            attrs.pop("approver_email", None)

        return attrs
