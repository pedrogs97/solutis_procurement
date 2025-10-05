"""Service to send a request to the approval workflow."""

from logging import getLogger

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    Approver,
    Supplier,
)

logger = getLogger(__name__)


class SendRequestToApprovalWorkflowService:
    """
    Service to send a request to the approval workflow.
    """

    @staticmethod
    def __generate_accept_token(approval_flow_step_id: int) -> str:
        """
        Creates a unique token for the approver to accept the approval request.
        """
        content_to_hash = {
            "approvalFlowStepId": approval_flow_step_id,
            "action": "accept",
        }
        return str(hash(frozenset(content_to_hash.items())))

    @staticmethod
    def __generate_reject_token(approval_flow_step_id: int) -> str:
        """
        Creates a unique token for the approver to reject the approval request.
        """
        content_to_hash = {
            "approvalFlowStepId": approval_flow_step_id,
            "action": "reject",
        }
        return str(hash(frozenset(content_to_hash.items())))

    @classmethod
    def execute(cls, supplier: Supplier, approval_flow: ApprovalFlow):
        """
        Envia a solicitação para o próximo passo do fluxo de aprovação.
        """

        if not approval_flow.approver:
            logger.warning("Aprovador não definido para o fluxo de aprovação.")
            return
        context_email = {  # pylint: disable=unused-variable
            "supplier": supplier.trade_name,
            "approver_email": approval_flow.approver.email,
            "approver_name": approval_flow.approver.name,
            "step": approval_flow.step.name,
            "accept_token": cls.__generate_accept_token(approval_flow.pk),
            "reject_token": cls.__generate_reject_token(approval_flow.pk),
        }
        # Aqui você integraria com o serviço de envio de email


class ApprovalWorkflowService:
    """
    Service to manage the approval workflow.
    """

    @staticmethod
    def get_next_approval_step(current_step: ApprovalStep) -> ApprovalStep | None:
        """
        Retrieves the next approval step based on the current step's order.
        """
        return (
            ApprovalStep.objects.filter(order__gt=current_step.order)
            .order_by("order")
            .first()
        )

    @classmethod
    def initialize_approval_flow(
        cls, supplier: Supplier, approver: Approver
    ) -> ApprovalFlow:
        """
        Initializes an approval flow for a given supplier.
        """
        if ApprovalFlow.objects.filter(supplier=supplier).exists():
            raise ValueError("Um fluxo de aprovação já existe para este fornecedor.")

        first_step = ApprovalStep.objects.order_by("order").first()
        if not first_step:
            raise ValueError("Nenhum passo de aprovação definido.")

        approval_flow = ApprovalFlow.objects.create(
            supplier=supplier,
            step=first_step,
            approver=approver,
        )
        approval_flow.approve()
        return approval_flow
