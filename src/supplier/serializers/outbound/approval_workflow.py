"""
Serializer for the Approval Workflow.
"""

from rest_framework import serializers

from src.supplier.models.approval_workflow import ApprovalFlow, ApprovalStep


class ApprovalStepSerializer(serializers.ModelSerializer):
    """Serializer for the Approval Step."""

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
        ]
        read_only_fields = ["id"]


class SupplierApprovalFlowSerializer(serializers.ModelSerializer):
    """Serializer for the Supplier Approval Flow."""

    step = ApprovalStepSerializer(read_only=True)
    approver = serializers.StringRelatedField()

    class Meta:
        """Meta dados do serializer."""

        model = ApprovalFlow
        fields = [
            "id",
            "step",
            "approver",
            "approved_at",
            "reproved_at",
        ]
        read_only_fields = ["id", "approved_at", "reproved_at"]
