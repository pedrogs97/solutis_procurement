"""Service to send a request to the approval workflow."""

from logging import getLogger
from typing import Optional

from django.conf import settings
from jwt import encode

from src.shared.backends import Email365Client
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
        return encode(content_to_hash, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def __generate_reject_token(approval_flow_step_id: int) -> str:
        """
        Creates a unique token for the approver to reject the approval request.
        """
        content_to_hash = {
            "approvalFlowStepId": approval_flow_step_id,
            "action": "reject",
        }
        return encode(content_to_hash, settings.SECRET_KEY, algorithm="HS256")

    @classmethod
    def execute(cls, supplier: Supplier, approval_flow: ApprovalFlow):
        """
        Envia a solicitação para o próximo passo do fluxo de aprovação.
        """

        if not approval_flow.approver:
            logger.warning("Aprovador não definido para o fluxo de aprovação.")
            return
        accept_token = cls.__generate_accept_token(approval_flow.pk)
        reject_token = cls.__generate_reject_token(approval_flow.pk)
        context_email = {
            "supplier": supplier.trade_name,
            "approver_name": approval_flow.approver.name,
            "step": approval_flow.step.name,
            "observations": approval_flow.observations,
            "approval_link": f"{settings.APP_URL}/approval?token={accept_token}",
            "reprove_link": f"{settings.APP_URL}/approval?token={reject_token}",
        }

        email_client = Email365Client(
            mail_to=approval_flow.approver.email,
            mail_subject=f"Aprovação de Fornecedor - {supplier.trade_name}",
            type_message="approval",
            extra=context_email,
        )
        email_client.send_message()


class ApprovalWorkflowService:
    """
    Service to manage the approval workflow.
    """

    @staticmethod
    def get_next_approval_step(current_step: ApprovalStep) -> Optional[ApprovalStep]:
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
            observations="",
        )
        approval_flow.approve()
        return approval_flow
