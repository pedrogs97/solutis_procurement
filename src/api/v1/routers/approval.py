"""Approval workflow endpoints for Ninja API v1."""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from rest_framework.exceptions import NotFound

from src.api.v1.schemas.approval import (
    ApprovalFlowOut,
    ApprovalStepOut,
    ApproveCurrentStepIn,
    ApproverOut,
    SetResponsibleApproverIn,
    StartApprovalIn,
)
from src.supplier.models.approval_workflow import ApprovalFlow, ApprovalStep, Approver
from src.supplier.models.supplier import Supplier
from src.supplier.services.approval_workflow import (
    ApprovalWorkflowService,
    SendRequestToApprovalWorkflowService,
)

router = Router(tags=["approval"])


def _serialize_flow(flow: ApprovalFlow) -> dict:
    next_step = (
        ApprovalStep.objects.filter(order__gt=flow.step.order).order_by("order").first()
        if flow.step
        else None
    )
    return ApprovalFlowOut(
        id=flow.id,
        step=ApprovalStepOut.model_validate(flow.step),
        supplier=flow.supplier_id,
        approver_id=flow.approver_id,
        approver=ApproverOut.model_validate(flow.approver) if flow.approver else None,
        is_approved=flow.approved_at is not None,
        is_reproved=flow.reproved_at is not None,
        approved_at=flow.approved_at.isoformat() if flow.approved_at else None,
        reproved_at=flow.reproved_at.isoformat() if flow.reproved_at else None,
        observations=flow.observations or "",
        next_step=next_step.id if next_step else None,
    ).model_dump(by_alias=True)


@router.get("/steps/", url_name="approval-steps-v1")
def list_steps(request):
    """Return all configured approval steps."""
    queryset = ApprovalStep.objects.all()
    return [
        ApprovalStepOut.model_validate(step).model_dump(by_alias=True)
        for step in queryset
    ]


@router.post("/start/", url_name="approval-start-v1")
def start_approval_flow(request, payload: StartApprovalIn):
    """Start an approval flow for a supplier."""
    supplier = get_object_or_404(Supplier, id=payload.supplier_id)
    approver, _ = Approver.objects.get_or_create(
        email=payload.approver_email,
        defaults={"name": payload.approver_name},
    )
    try:
        ApprovalWorkflowService.initialize_approval_flow(supplier, approver)
    except ValueError as exc:
        raise HttpError(400, str(exc)) from exc

    return JsonResponse(payload.model_dump(by_alias=True), status=201)


@router.post("/steps/responsible/", url_name="approval-step-responsible-v1")
def set_step_responsible(request, payload: SetResponsibleApproverIn):
    """Assign the responsible approver for the next workflow step."""
    try:
        step = ApprovalStep.objects.get(id=payload.step_id)
    except ApprovalStep.DoesNotExist as exc:
        raise HttpError(400, "Passo de aprovacao nao encontrado.") from exc

    next_step = (
        ApprovalStep.objects.filter(order__gt=step.order).order_by("order").first()
    )
    if not next_step:
        raise HttpError(400, "Nao ha proximo passo definido no fluxo de aprovacao.")

    try:
        workflow = ApprovalFlow.objects.get(id=payload.workflow_id, step=step)
    except ApprovalFlow.DoesNotExist as exc:
        raise HttpError(400, "Fluxo de aprovacao nao encontrado.") from exc

    approver, _ = Approver.objects.get_or_create(
        email=payload.email,
        defaults={"name": payload.name},
    )
    new_flow = ApprovalFlow.objects.create(
        supplier=workflow.supplier,
        approver=approver,
        step=next_step,
        observations=payload.observations or "",
    )
    SendRequestToApprovalWorkflowService.execute(workflow.supplier, new_flow)

    return JsonResponse(
        {
            "name": payload.name,
            "email": payload.email,
            "workflowId": new_flow.pk,
            "stepId": next_step.pk,
            "observations": payload.observations or "",
        },
        status=201,
    )


@router.post("/step/approve/", url_name="approval-current-step-v1")
def approve_current_step(request, payload: ApproveCurrentStepIn):
    """Approve or reprove a workflow step."""
    try:
        workflow = ApprovalFlow.objects.get(id=payload.workflow_id)
    except ApprovalFlow.DoesNotExist as exc:
        raise HttpError(400, "Fluxo de aprovacao nao encontrado.") from exc

    if payload.is_approved:
        workflow.approve()
    else:
        workflow.reprove()

    return JsonResponse(
        {
            "workflowId": workflow.pk,
            "isApproved": payload.is_approved,
        },
        status=201,
    )


@router.get("/supplier/{supplier_id}/flows/", url_name="approval-supplier-flows-v1")
def supplier_approval_flows(request, supplier_id: int):
    """List approval flow history for a supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if not ApprovalFlow.objects.filter(supplier=supplier).exists():
        raise NotFound("Nenhum fluxo de aprovacao encontrado para este fornecedor.")

    approve_flow = (
        supplier.approval_flow_history.select_related("step", "approver")
        .all()
        .order_by("step__order")
    )
    return [_serialize_flow(flow) for flow in approve_flow]
