"""Views para o fluxo de aprovação de fornecedores."""

from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from src.shared.views import BaseAPIView
from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    StepApproval,
)
from src.supplier.models.supplier import Supplier
from src.supplier.serializers.approval_workflow import (
    ApprovalFlowSerializer,
    ApprovalStepSerializer,
    ApproveStepSerializer,
    StepApprovalSerializer,
)

ERROR_FLOW_EXISTS = "Já existe um fluxo de aprovação para este fornecedor."
ERROR_SUPPLIER_ID_REQUIRED = "O parâmetro supplier_id é obrigatório."
ERROR_SUPPLIER_NOT_FOUND = "Fornecedor não encontrado."
ERROR_FLOW_NOT_FOUND = "Fluxo de aprovação não encontrado."
ERROR_NO_CURRENT_STEP = "Este fluxo não possui um passo atual definido."
ERROR_STEP_ALREADY_EVALUATED = "Este passo já foi avaliado anteriormente."
ERROR_FLOW_COMPLETED = "Este fluxo já está concluído."
ERROR_FLOW_NOT_ADVANCED = "Não foi possível avançar o fluxo."


class ApprovalStepView(generics.ListAPIView):
    """
    View para listar os passos de aprovação.
    Somente leitura pois os passos são definidos pelo sistema.
    """

    queryset = ApprovalStep.objects.all().order_by("order")
    serializer_class = ApprovalStepSerializer


class ApprovalFlowCreateView(BaseAPIView):
    """
    View para criar um novo fluxo de aprovação.
    Utiliza a BaseAPIView para aproveitar as funcionalidades comuns.
    """

    serializer_class = ApprovalFlowSerializer

    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o método para validar se já existe um fluxo para o fornecedor.
        """
        supplier_id = request.data.get("supplier")

        if (
            supplier_id
            and ApprovalFlow.objects.filter(supplier_id=supplier_id).exists()
        ):
            return Response(
                {"detail": ERROR_FLOW_EXISTS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().post(request, *args, **kwargs)


class ApprovalFlowListView(generics.ListAPIView):
    """
    View para listar fluxos de aprovação.
    """

    queryset = ApprovalFlow.objects.all()
    serializer_class = ApprovalFlowSerializer


class ApprovalFlowDetailView(BaseAPIView):
    """
    View para operações de detalhe em um fluxo de aprovação.
    """

    queryset = ApprovalFlow.objects.all()
    serializer_class = ApprovalFlowSerializer

    def get_next_step(self, request: Request, *args, **kwargs) -> Response:
        """Avança o fluxo para o próximo passo."""
        approval_flow = self.get_object()

        if approval_flow.is_completed:
            return Response(
                {"detail": ERROR_FLOW_COMPLETED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success = approval_flow.advance_to_next_step()

        if success:
            return Response(
                {
                    "detail": "Fluxo avançado com sucesso.",
                    "current_step": (
                        approval_flow.current_step.name
                        if approval_flow.current_step
                        else None
                    ),
                    "is_completed": approval_flow.is_completed,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": ERROR_FLOW_NOT_ADVANCED},
            status=status.HTTP_400_BAD_REQUEST,
        )


class StepApprovalCreateView(BaseAPIView):
    """
    View para criar uma aprovação de passo.
    """

    serializer_class_in = ApproveStepSerializer
    serializer_class_out = StepApprovalSerializer

    def post(self, request, flow_id, *args, **kwargs):
        """Aprova ou rejeita o passo atual do fluxo."""
        try:
            approval_flow = ApprovalFlow.objects.get(pk=flow_id)
        except ApprovalFlow.DoesNotExist:
            return Response(
                {"detail": ERROR_FLOW_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not approval_flow.current_step:
            return Response(
                {"detail": ERROR_NO_CURRENT_STEP},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if StepApproval.objects.filter(
            approval_flow=approval_flow, step=approval_flow.current_step
        ).exists():
            return Response(
                {"detail": ERROR_STEP_ALREADY_EVALUATED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data=request.data,
            context={
                "flow_id": approval_flow.pk,
                "step_id": approval_flow.current_step.pk,
            },
        )

        serializer.is_valid(raise_exception=True)
        step_approval = StepApproval.objects.create(
            approval_flow=approval_flow,
            step=approval_flow.current_step,
            **serializer.validated_data,
        )

        if step_approval.is_approved:
            approval_flow.advance_to_next_step()

        return Response(
            self.get_out_serializer_class()(step_approval).data,
            status=status.HTTP_201_CREATED,
        )


class SupplierApprovalFlowView(BaseAPIView):
    """
    View para operações relacionadas ao fluxo de aprovação de um fornecedor específico.
    """

    serializer_class = ApprovalFlowSerializer

    def get(self, request, supplier_id, *args, **kwargs):
        """Obtém o fluxo de aprovação para um fornecedor específico."""
        try:
            approval_flow = ApprovalFlow.objects.get(supplier_id=supplier_id)
            serializer = self.get_serializer(approval_flow)
            return Response(serializer.data)
        except ApprovalFlow.DoesNotExist:
            return Response(
                {"detail": "Não existe fluxo de aprovação para este fornecedor."},
                status=status.HTTP_404_NOT_FOUND,
            )


class StartApprovalFlowView(BaseAPIView):
    """
    View para iniciar um fluxo de aprovação para um fornecedor.
    """

    serializer_class = ApprovalFlowSerializer

    def post(self, request, supplier_id, *args, **kwargs):
        """Inicia um fluxo de aprovação para um fornecedor."""
        try:
            supplier = Supplier.objects.get(pk=supplier_id)
        except Supplier.DoesNotExist:
            return Response(
                {"detail": ERROR_SUPPLIER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if ApprovalFlow.objects.filter(supplier_id=supplier_id).exists():
            return Response(
                {"detail": ERROR_FLOW_EXISTS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        approval_flow = ApprovalFlow.objects.create(supplier=supplier)

        approval_flow.advance_to_next_step()

        serializer = self.get_serializer(approval_flow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
