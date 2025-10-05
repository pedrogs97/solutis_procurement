"""
URLs relacionadas ao fluxo de aprovação de fornecedores.
"""

from django.urls import path

from src.supplier.views.approval_workflow import (
    ApproveCurrentStepView,
    StartApprovalFlowView,
    StepResponsibleApproverView,
    SupplierApprovalFlowsView,
)

app_name = "supplier"

urlpatterns = [
    path("start/", StartApprovalFlowView.as_view(), name="start-approval-flow"),
    path(
        "steps/responsible/",
        StepResponsibleApproverView.as_view(),
        name="step-responsible-approver",
    ),
    path(
        "step/approve/",
        ApproveCurrentStepView.as_view(),
        name="approve-current-step",
    ),
    path(
        "supplier/<int:supplier_id>/flows/",
        SupplierApprovalFlowsView.as_view(),
        name="supplier-approval-flows",
    ),
]
