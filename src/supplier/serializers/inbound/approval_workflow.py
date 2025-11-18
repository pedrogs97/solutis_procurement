"""
Inbound Approval Workflow Serializers
"""

from typing import Dict

from rest_framework import serializers

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    Approver,
    Supplier,
)
from src.supplier.services.approval_workflow import ApprovalWorkflowService


class StartApprovalFlowSerializer(serializers.Serializer):
    """Serializer to start an approval workflow for a supplier."""

    supplier_id = serializers.IntegerField()
    approver_name = serializers.CharField(max_length=255)
    approver_email = serializers.EmailField()

    class Meta:
        """Meta dados do serializer."""

        fields = [
            "supplier_id",
            "approver_name",
            "approver_email",
        ]

    def validate(self, data: Dict):
        """
        Validate the input data to ensure the supplier exists.
        """
        data = super().validate(data)
        supplier_id = data.get("supplier_id")

        try:
            supplier = Supplier.objects.get(id=supplier_id)
            data["supplier"] = supplier
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Fornecedor não encontrado.")

        return data

    def create(self, validated_data):
        """
        Create and start the approval workflow for the supplier.
        """
        supplier = validated_data["supplier"]
        approver, _ = Approver.objects.get_or_create(
            email=validated_data["approver_email"],
            defaults={"name": validated_data["approver_name"]},
        )
        return ApprovalWorkflowService.initialize_approval_flow(supplier, approver)


class SetResponsibleApproverSerializer(serializers.Serializer):
    """Serializer to set the responsible approver for a specific step in an approval workflow."""

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    workflow_id = serializers.IntegerField()
    step_id = serializers.IntegerField()
    observations = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        """Meta dados do serializer."""

        fields = [
            "name",
            "email",
            "workflow_id",
            "step_id",
            "observations",
        ]

    def validate(self, data: Dict):
        """
        Validate the input data to ensure the workflow and step exist.
        """
        data = super().validate(data)
        workflow_id = data.get("workflow_id")
        step_id = data.get("step_id")

        try:
            step = ApprovalStep.objects.get(id=step_id)
            next_step = (
                ApprovalStep.objects.filter(order__gt=step.order)
                .order_by("order")
                .first()
            )

            if not next_step:
                raise serializers.ValidationError(
                    "Não há próximo passo definido no fluxo de aprovação."
                )
            data["next_step"] = next_step
        except ApprovalStep.DoesNotExist:
            raise serializers.ValidationError("Passo de aprovação não encontrado.")

        try:
            workflow = ApprovalFlow.objects.get(id=workflow_id, step=step)
            data["workflow"] = workflow
        except ApprovalFlow.DoesNotExist:
            raise serializers.ValidationError("Fluxo de aprovação não encontrado.")

        return data

    def create(self, validated_data: Dict):
        """
        Set the responsible approver for the specified step in the workflow.
        """
        workflow = validated_data["workflow"]
        approver, _ = Approver.objects.get_or_create(
            email=validated_data["email"],
            defaults={"name": validated_data["name"]},
        )

        new_approval_flow = ApprovalFlow.objects.create(
            supplier=workflow.supplier,
            approver=approver,
            step=validated_data["next_step"],
            observations=validated_data.get("observations", ""),
        )

        return {
            "name": validated_data["name"],
            "email": validated_data["email"],
            "workflow": new_approval_flow,
            "supplier": workflow.supplier,
            "workflow_id": new_approval_flow.pk,
            "step_id": validated_data["next_step"].pk,
            "observations": validated_data.get("observations", ""),
        }


class ApproveApprovalFlowStepSerializer(serializers.Serializer):
    """Serializer to approve or reject a step in the approval workflow."""

    workflow_id = serializers.IntegerField()
    is_approved = serializers.BooleanField(default=True)

    class Meta:
        """Meta dados do serializer."""

        fields = [
            "workflow_id",
            "is_approved",
        ]

    def validate(self, data: Dict):
        """
        Validate the input data to ensure the workflow and step exist.
        """
        data = super().validate(data)
        workflow_id = data.get("workflow_id")
        try:
            workflow = ApprovalFlow.objects.get(id=workflow_id)
            data["workflow"] = workflow
        except ApprovalFlow.DoesNotExist:
            raise serializers.ValidationError("Fluxo de aprovação não encontrado.")

        return data

    def create(self, validated_data):
        """
        Approve or reject a step in the approval workflow.
        """
        workflow: ApprovalFlow = validated_data["workflow"]
        is_approved = validated_data["is_approved"]

        if is_approved:
            workflow.approve()
            return {
                "workflow_id": workflow.pk,
                "workflow": workflow,
                "is_approved": True,
            }

        workflow.reprove()

        return {
            "workflow_id": workflow.pk,
            "workflow": workflow,
            "is_approved": False,
        }
