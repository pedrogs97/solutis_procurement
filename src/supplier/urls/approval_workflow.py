"""
URLs relacionadas ao fluxo de aprovação de fornecedores.
"""

from django.urls import path

from src.supplier.views.approval_workflow import (
    ApprovalFlowCreateView,
    ApprovalFlowDetailView,
    ApprovalFlowListView,
    ApprovalStepView,
    StartApprovalFlowView,
    StepApprovalCreateView,
    SupplierApprovalFlowView,
)

app_name = "supplier"

urlpatterns = [
    path("steps/", ApprovalStepView.as_view(), name="approval-steps"),
    path("flows/", ApprovalFlowListView.as_view(), name="approval-flows-list"),
    path(
        "flows/create/", ApprovalFlowCreateView.as_view(), name="approval-flows-create"
    ),
    path(
        "flows/<int:pk>/", ApprovalFlowDetailView.as_view(), name="approval-flow-detail"
    ),
    path(
        "flows/<int:flow_id>/approve/",
        StepApprovalCreateView.as_view(),
        name="approval-flow-approve",
    ),
    path(
        "supplier/<int:supplier_id>/",
        SupplierApprovalFlowView.as_view(),
        name="approval-flow-for-supplier",
    ),
    path(
        "supplier/<int:supplier_id>/start/",
        StartApprovalFlowView.as_view(),
        name="approval-flow-start",
    ),
]
