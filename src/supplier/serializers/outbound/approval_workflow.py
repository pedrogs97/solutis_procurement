"""
Serializer for the Approval Workflow.
"""

from rest_framework import serializers

from src.shared.serializers import BaseSerializer
from src.supplier.models.approval_workflow import ApprovalFlow, ApprovalStep, Approver


class ApprovalStepSerializer(BaseSerializer):
    """Serializer for the Approval Step."""

    class Meta(BaseSerializer.Meta):
        """Meta dados do serializer."""

        model = ApprovalStep
        fields = [
            "id",
            "name",
            "description",
            "order",
            "department",
            "is_mandatory",
        ]
        read_only_fields = ["id"]


class ApproverSerializer(BaseSerializer):
    """Serializer for the Approver."""

    class Meta(BaseSerializer.Meta):
        """Meta dados do serializer."""

        model = Approver
        fields = ["id", "name", "email"]


class SupplierApprovalFlowSerializer(BaseSerializer):
    """Serializer for the Supplier Approval Flow."""

    step = ApprovalStepSerializer(read_only=True)
    approver = ApproverSerializer(read_only=True)
    is_approved = serializers.SerializerMethodField()
    is_reproved = serializers.SerializerMethodField()
    next_step = serializers.SerializerMethodField()
    approver_id = serializers.IntegerField(source="approver.id", read_only=True)

    class Meta(BaseSerializer.Meta):
        """Meta dados do serializer."""

        model = ApprovalFlow
        fields = [
            "id",
            "step",
            "supplier",
            "approver_id",
            "approver",
            "is_approved",
            "is_reproved",
            "approved_at",
            "reproved_at",
            "next_step",
        ]
        read_only_fields = ["id", "approved_at", "reproved_at"]

    def get_is_approved(self, obj: ApprovalFlow) -> bool:
        """Indicates if the approval flow step is approved."""
        return obj.approved_at is not None

    def get_is_reproved(self, obj: ApprovalFlow) -> bool:
        """Indicates if the approval flow step is reproved."""
        return obj.reproved_at is not None

    def get_next_step(self, obj: ApprovalFlow) -> ApprovalStepSerializer | None:
        """Returns the next step in the approval flow, if any."""
        next_flow = (
            ApprovalStep.objects.filter(order__gt=obj.step.order)
            .order_by("order")
            .first()
        )
        if next_flow:
            return next_flow.pk
        return None
