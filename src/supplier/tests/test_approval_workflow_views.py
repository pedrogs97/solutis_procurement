"""
Testes unitários para as views do fluxo de aprovação de fornecedores.
"""

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    Approver,
    StepApproval,
)


@pytest.fixture
def approval_steps():
    """Fixture para criar passos de aprovação."""
    step1 = baker.make(
        ApprovalStep,
        name="Cadastro inicial",
        description="Cadastro inicial do fornecedor",
        order=1,
        department="Administrativo",
    )
    step2 = baker.make(
        ApprovalStep,
        name="Validação geral",
        description="Validação geral do cadastro",
        order=2,
        department="Administrativo",
    )
    step3 = baker.make(
        ApprovalStep,
        name="Validação financeira",
        description="Validação financeira do fornecedor",
        order=3,
        department="Financeiro",
    )
    return [step1, step2, step3]


@pytest.mark.django_db
class TestApprovalStepView:
    """Testes para o viewset ApprovalStepView."""

    def test_list_steps(self, api_client, approval_steps):
        """Teste de listagem dos passos de aprovação."""
        url = reverse("approval-steps")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
        assert response.data["results"][0]["name"] == "Cadastro inicial"


@pytest.mark.django_db
class TestApprovalFlowCreateView:
    """Testes para criação de fluxos de aprovação."""

    def test_create_flow(self, api_client, supplier, approval_steps):
        """Teste de criação de fluxo de aprovação."""
        url = reverse("approval-flows-create")
        data = {"supplier": supplier.pk, "current_step": approval_steps[0].pk}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["supplier"] == supplier.pk
        assert response.data["current_step"] == approval_steps[0].pk
        assert response.data["is_completed"] is False

    def test_create_duplicate_flow(self, api_client, supplier, approval_steps):
        """Teste de criação de fluxo duplicado para o mesmo fornecedor."""
        baker.make(ApprovalFlow, supplier=supplier)

        url = reverse("approval-flows-create")
        data = {"supplier": supplier.pk}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Já existe um fluxo" in response.data["detail"]


@pytest.mark.django_db
class TestApprovalFlowDetailView:
    """Testes para detalhamento de fluxos de aprovação."""

    def test_get_flow(self, api_client, supplier, approval_steps):
        """Teste de obtenção de um fluxo específico."""
        flow = baker.make(
            ApprovalFlow, supplier=supplier, current_step=approval_steps[0]
        )

        url = reverse("approval-flow-detail", kwargs={"pk": flow.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == flow.pk
        assert response.data["supplier"] == supplier.pk

    def test_get_nonexistent_flow(self, api_client):
        """Teste de obtenção de fluxo inexistente."""
        url = reverse("approval-flow-detail", kwargs={"pk": 999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestStepApprovalCreateView:
    """Testes para aprovação de passos."""

    def test_approve_step(self, api_client, supplier, approval_steps):
        """Teste de aprovação de um passo."""
        flow = baker.make(
            ApprovalFlow, supplier=supplier, current_step=approval_steps[0]
        )

        url = reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})
        data = {
            "approver_name": "João Silva",
            "approver_email": "joao.silva@company.com",
            "comments": "Aprovado conforme documentação",
            "is_approved": True,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["approver_detail"]["name"] == "João Silva"
        assert response.data["approver_detail"]["email"] == "joao.silva@company.com"
        assert response.data["is_approved"] is True

        flow.refresh_from_db()
        assert flow.current_step == approval_steps[1]

        # Verificar se o aprovador foi criado
        assert Approver.objects.filter(email="joao.silva@company.com").exists()

    def test_reject_step(self, api_client, supplier, approval_steps):
        """Teste de rejeição de um passo."""
        flow = baker.make(
            ApprovalFlow, supplier=supplier, current_step=approval_steps[0]
        )

        url = reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})
        data = {
            "approver_name": "Maria Santos",
            "approver_email": "maria.santos@company.com",
            "comments": "Documentação incompleta",
            "is_approved": False,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_approved"] is False

        flow.refresh_from_db()
        assert flow.current_step == approval_steps[0]

    def test_approve_nonexistent_flow(self, api_client):
        """Teste de aprovação de fluxo inexistente."""
        url = reverse("approval-flow-approve", kwargs={"flow_id": 999})
        data = {
            "approver_name": "João Silva",
            "approver_email": "joao.silva@company.com",
            "is_approved": True,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "não encontrado" in response.data["detail"]

    def test_approve_step_already_evaluated(self, api_client, supplier, approval_steps):
        """Teste de aprovação de passo já avaliado."""
        flow = baker.make(
            ApprovalFlow, supplier=supplier, current_step=approval_steps[0]
        )

        approver = baker.make(
            Approver, name="João Silva", email="joao.silva@company.com"
        )

        baker.make(
            StepApproval,
            approval_flow=flow,
            step=approval_steps[0],
            approver=approver,
            is_approved=True,
        )

        url = reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})
        data = {
            "approver_name": "Maria Santos",
            "approver_email": "maria.santos@company.com",
            "is_approved": True,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já foi avaliado" in response.data["detail"]

    def test_reuse_existing_approver(self, api_client, supplier, approval_steps):
        """Teste de reutilização de aprovador existente."""
        existing_approver = baker.make(
            Approver, name="Carlos Silva", email="carlos.silva@company.com"
        )

        flow = baker.make(
            ApprovalFlow, supplier=supplier, current_step=approval_steps[0]
        )

        url = reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})
        data = {
            "approver_name": "Carlos Silva Atualizado",  # Nome diferente
            "approver_email": "carlos.silva@company.com",  # Email igual
            "comments": "Aprovado",
            "is_approved": True,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # Deve usar o aprovador existente
        assert response.data["approver"] == existing_approver.pk
        assert (
            response.data["approver_detail"]["name"] == "Carlos Silva"
        )  # Nome original


@pytest.mark.django_db
class TestSupplierApprovalFlowView:
    """Testes para operações específicas por fornecedor."""

    def test_get_flow_for_supplier(self, api_client, supplier, approval_steps):
        """Teste de obtenção do fluxo de um fornecedor específico."""
        flow = baker.make(
            ApprovalFlow, supplier=supplier, current_step=approval_steps[0]
        )

        url = reverse("approval-flow-for-supplier", kwargs={"supplier_id": supplier.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == flow.pk
        assert response.data["supplier"] == supplier.pk

    def test_get_flow_for_supplier_without_flow(self, api_client, supplier):
        """Teste de obtenção do fluxo de fornecedor sem fluxo."""
        url = reverse("approval-flow-for-supplier", kwargs={"supplier_id": supplier.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestStartApprovalFlowView:
    """Testes para inicialização de fluxos de aprovação."""

    def test_start_approval_flow(self, api_client, supplier, approval_steps):
        """Teste de inicialização de fluxo de aprovação."""
        url = reverse("approval-flow-start", kwargs={"supplier_id": supplier.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["supplier"] == supplier.pk
        assert response.data["current_step"] == approval_steps[0].pk

    def test_start_approval_flow_duplicate(self, api_client, supplier, approval_steps):
        """Teste de inicialização de fluxo duplicado."""
        baker.make(ApprovalFlow, supplier=supplier)

        url = reverse("approval-flow-start", kwargs={"supplier_id": supplier.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Já existe um fluxo" in response.data["detail"]

    def test_start_approval_flow_nonexistent_supplier(self, api_client):
        """Teste de inicialização de fluxo para fornecedor inexistente."""
        url = reverse("approval-flow-start", kwargs={"supplier_id": 999})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "não encontrado" in response.data["detail"]
