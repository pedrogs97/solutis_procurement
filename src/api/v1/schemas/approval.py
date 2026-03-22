"""Approval schemas for Ninja v1."""

from typing import Optional

from src.api.v1.schemas.common import CamelSchema


class StartApprovalIn(CamelSchema):
    """Payload to start an approval workflow."""

    supplier_id: int
    approver_name: str
    approver_email: str


class SetResponsibleApproverIn(CamelSchema):
    """Payload to set the responsible approver for a step."""

    name: str
    email: str
    workflow_id: int
    step_id: int
    observations: Optional[str] = ""


class ApproveCurrentStepIn(CamelSchema):
    """Payload to approve or reprove a workflow step."""

    workflow_id: int
    is_approved: bool = True


class ApprovalStepOut(CamelSchema):
    """Serialized approval step."""

    id: int
    name: str
    description: str
    order: int
    department: str
    is_mandatory: bool


class ApproverOut(CamelSchema):
    """Serialized approver."""

    id: int
    name: str
    email: str


class ApprovalFlowOut(CamelSchema):
    """Serialized approval flow item."""

    id: int
    step: ApprovalStepOut
    supplier: int
    approver_id: Optional[int] = None
    approver: Optional[ApproverOut] = None
    is_approved: bool
    is_reproved: bool
    approved_at: Optional[str] = None
    reproved_at: Optional[str] = None
    observations: str
    next_step: Optional[int] = None
