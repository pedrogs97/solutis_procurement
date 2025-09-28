"""
Testes de integração do fluxo de aprovação de fornecedores.
Este arquivo contém testes que simulam o fluxo completo de aprovação.
"""

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    StepApproval,
)


@pytest.fixture
def default_approval_steps():
    """Fixture que cria os passos de aprovação padrão."""
    steps = [
        baker.make(
            ApprovalStep,
            name="Cadastro inicial",
            order=1,
            department="Administrativo",
            is_mandatory=True,
        ),
        baker.make(
            ApprovalStep,
            name="Validação geral do cadastro",
            order=2,
            department="Administrativo",
            is_mandatory=True,
        ),
        baker.make(
            ApprovalStep,
            name="Validação geral do cadastro",
            order=3,
            department="Financeiro",
            is_mandatory=True,
        ),
        baker.make(
            ApprovalStep,
            name="Avaliação do compliance | Sustentabilidade",
            order=4,
            department="Financeiro",
            is_mandatory=True,
        ),
        baker.make(
            ApprovalStep,
            name="Avaliação do gestor",
            order=5,
            department="Administrativo",
            is_mandatory=True,
        ),
        baker.make(
            ApprovalStep,
            name="Avaliação jurídica",
            order=6,
            department="Jurídico",
            is_mandatory=True,
        ),
        baker.make(
            ApprovalStep,
            name="Avaliação diretoria",
            order=7,
            department="Diretoria",
            is_mandatory=True,
        ),
        baker.make(
            ApprovalStep,
            name="Aprovação final do fluxo",
            order=8,
            department="Diretoria",
            is_mandatory=True,
        ),
    ]
    return steps


@pytest.mark.django_db
class TestCompleteApprovalFlow:
    """Testes de integração simulando um fluxo de aprovação completo."""

    def test_complete_approval_workflow(
        self, api_client, supplier, default_approval_steps
    ):
        """
        Testa o fluxo de aprovação completo de um fornecedor,
        desde o início até a aprovação final.
        """
        start_url = reverse("approval-flow-start", kwargs={"supplier_id": supplier.pk})
        response = api_client.post(start_url, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        flow_id = response.data["id"]

        flow = ApprovalFlow.objects.get(pk=flow_id)
        assert flow.current_step == default_approval_steps[0]

        def get_approve_url():
            flow.refresh_from_db()
            return reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Taion",
            "approver_email": "taion@company.com",
            "comments": "Cadastro inicial realizado com sucesso.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[1]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Beatriz Cunha",
            "approver_email": "beatriz.cunha@company.com",
            "comments": "Validação administrativa concluída.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[2]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Claudia Cavalcante",
            "approver_email": "claudia.cavalcante@company.com",
            "comments": "Validação financeira concluída.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[3]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Analista de Compliance",
            "approver_email": "analista.compliance@company.com",
            "comments": "Análise de compliance e sustentabilidade concluída.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[4]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Gestor Administrativo",
            "approver_email": "gestor.administrativo@company.com",
            "comments": "Avaliação do gestor concluída.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[5]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Advogado Responsável",
            "approver_email": "advogado.responsavel@company.com",
            "comments": "Avaliação jurídica concluída.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[6]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Diretor de Operações",
            "approver_email": "diretor.operacoes@company.com",
            "comments": "Aprovado pela diretoria.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[7]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Diretor Presidente",
            "approver_email": "diretor.presidente@company.com",
            "comments": "Aprovação final concedida.",
            "is_approved": True,
        }
        response = api_client.post(approve_url, approval_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        flow.refresh_from_db()
        assert flow.is_completed is True
        assert flow.current_step is None
        assert flow.completion_date is not None

        approvals = StepApproval.objects.filter(approval_flow=flow)
        assert approvals.count() == 8
        assert all(approval.is_approved for approval in approvals)

    def test_rejection_in_approval_workflow(
        self, api_client, supplier, default_approval_steps
    ):
        """
        Testa o fluxo de aprovação com rejeição em um dos passos.
        """
        start_url = reverse("approval-flow-start", kwargs={"supplier_id": supplier.pk})
        response = api_client.post(start_url, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        flow_id = response.data["id"]

        flow = ApprovalFlow.objects.get(pk=flow_id)

        def get_approve_url():
            flow.refresh_from_db()
            return reverse("approval-flow-approve", kwargs={"flow_id": flow.pk})

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Taion",
            "approver_email": "taion@company.com",
            "comments": "Cadastro inicial realizado.",
            "is_approved": True,
        }
        api_client.post(approve_url, approval_data, format="json")

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Beatriz Cunha",
            "approver_email": "beatriz.cunha@company.com",
            "comments": "Validação administrativa concluída.",
            "is_approved": True,
        }
        api_client.post(approve_url, approval_data, format="json")

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[2]

        approve_url = get_approve_url()
        approval_data = {
            "approver_name": "Claudia Cavalcante",
            "approver_email": "claudia.cavalcante@company.com",
            "comments": "Documentação financeira incompleta. Fornecedor não aprovado.",
            "is_approved": False,
        }
        response = api_client.post(approve_url, approval_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_approved"] is False

        flow.refresh_from_db()
        assert flow.current_step == default_approval_steps[2]
        assert flow.is_completed is False
