"""
Testes para o fluxo de aprovação de fornecedores.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    StepApproval,
)
from src.supplier.models.supplier import Supplier


@pytest.mark.django_db
class TestApprovalWorkflow:
    """Testes para o fluxo de aprovação de fornecedores."""

    def test_create_approval_flow(self, api_client: APIClient, supplier: Supplier):
        """Teste de criação de um fluxo de aprovação."""
        url = reverse("approval-flows-create")

        data = {"supplier": supplier.pk}

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] is not None
        assert response.data["supplier"] == supplier.pk

        assert ApprovalFlow.objects.filter(supplier=supplier).exists()

    def test_duplicate_approval_flow(self, api_client: APIClient, supplier: Supplier):
        """Teste de tentativa de criar um fluxo duplicado."""
        ApprovalFlow.objects.create(supplier=supplier)

        url = reverse("approval-flows-create")
        data = {"supplier": supplier.pk}

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_start_approval_flow_for_supplier(
        self, api_client: APIClient, supplier: Supplier
    ):
        """Teste de início de fluxo para um fornecedor específico."""
        url = reverse("approval-flow-start", kwargs={"supplier_id": supplier.pk})

        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["supplier"] == supplier.pk

        assert ApprovalFlow.objects.filter(supplier=supplier).exists()

    def test_approve_current_step(self, api_client: APIClient, supplier: Supplier):
        """Teste de aprovação do passo atual."""
        step1 = ApprovalStep.objects.create(name="Passo 1", order=1, department="Dep1")
        ApprovalStep.objects.create(name="Passo 2", order=2, department="Dep2")

        flow = ApprovalFlow.objects.create(supplier=supplier, current_step=step1)

        url = reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})
        data = {
            "approver_name": "Aprovador Teste",
            "approver_email": "aprovador.teste@company.com",
            "comments": "Tudo ok",
            "is_approved": True,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_approved"] is True
        assert response.data["approver_detail"]["name"] == "Aprovador Teste"

        assert StepApproval.objects.filter(
            approval_flow=flow, step=step1, is_approved=True
        ).exists()

    def test_complete_flow(self, api_client: APIClient, supplier: Supplier):
        """Teste de conclusão do fluxo após o último passo."""
        step1 = ApprovalStep.objects.create(
            name="Passo Único", order=1, department="Dep1"
        )

        flow = ApprovalFlow.objects.create(supplier=supplier, current_step=step1)

        url = reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})
        data = {
            "approver_name": "Aprovador Teste",
            "approver_email": "aprovador.teste@company.com",
            "is_approved": True,
        }

        api_client.post(url, data, format="json")

        flow.refresh_from_db()
        assert flow.is_completed
        assert flow.current_step is None
        assert flow.completion_date is not None
