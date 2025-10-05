"""Views to manage supplier approval workflows."""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from src.supplier.models.approval_workflow import ApprovalFlow
from src.supplier.models.supplier import Supplier
from src.supplier.serializers.inbound.approval_workflow import (
    ApproveApprovalFlowStepSerializer,
    SetResponsibleApproverSerializer,
    StartApprovalFlowSerializer,
)
from src.supplier.serializers.outbound.approval_workflow import (
    SupplierApprovalFlowSerializer,
)
from src.supplier.services.approval_workflow import SendRequestToApprovalWorkflowService


class StartApprovalFlowView(generics.CreateAPIView):
    """View para iniciar um fluxo de aprovação para um fornecedor."""

    serializer_class = StartApprovalFlowSerializer


class StepResponsibleApproverView(generics.CreateAPIView):
    """
    View para gerenciar o aprovador responsável por um step específico.
    """

    serializer_class = SetResponsibleApproverSerializer

    def post(self, request: Request) -> Response:
        """
        Method to assign a responsible approver to a specific step in the approval workflow.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        SendRequestToApprovalWorkflowService.execute(instance.supplier, instance)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ApproveCurrentStepView(generics.UpdateAPIView):
    """View para aprovar ou rejeitar o passo atual do fluxo de aprovação."""

    serializer_class = ApproveApprovalFlowStepSerializer


class SupplierApprovalFlowsView(generics.RetrieveAPIView):
    """View para listar os fluxos de aprovação de um fornecedor."""

    serializer_class = SupplierApprovalFlowSerializer

    def get_object(self) -> Supplier:
        """
        Get the supplier object for the specified supplier ID.
        """
        supplier_id = self.kwargs.get("supplier_id")
        supplier = get_object_or_404(Supplier, id=supplier_id)
        if not ApprovalFlow.objects.filter(supplier=supplier).exists():
            raise NotFound("Nenhum fluxo de aprovação encontrado para este fornecedor.")
        return supplier

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the approval flows associated with the supplier.
        """
        instance = self.get_object()
        approve_flow = (
            instance.approval_flow_history.select_related("step")
            .all()
            .order_by("step__order")
        )
        serializer = self.get_serializer(approve_flow, many=True)
        return Response(serializer.data)
