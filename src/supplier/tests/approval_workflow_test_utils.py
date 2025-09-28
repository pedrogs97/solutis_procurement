"""
Utilitários para testes do fluxo de aprovação de fornecedores.
"""

from typing import List

from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from src.supplier.models.approval_workflow import ApprovalStep


def create_approval_steps_sequence() -> List[ApprovalStep]:
    """
    Cria uma sequência de passos de aprovação para testes usando model_bakery.

    Returns:
        Lista de passos de aprovação criados em ordem.
    """
    steps = [
        baker.make(ApprovalStep, name="Passo 1", order=1, department="Dep1"),
        baker.make(ApprovalStep, name="Passo 2", order=2, department="Dep2"),
        baker.make(ApprovalStep, name="Passo 3", order=3, department="Dep3"),
    ]
    return steps


def create_standard_approval_steps() -> List[ApprovalStep]:
    """
    Cria os passos padrão de aprovação conforme definido na especificação do fluxo usando model_bakery.

    Returns:
        Lista de passos de aprovação criados em ordem.
    """
    steps = [
        baker.make(
            ApprovalStep, name="Cadastro inicial", order=1, department="Administrativo"
        ),
        baker.make(
            ApprovalStep,
            name="Validação geral do cadastro",
            order=2,
            department="Administrativo",
        ),
        baker.make(
            ApprovalStep,
            name="Validação geral do cadastro",
            order=3,
            department="Financeiro",
        ),
        baker.make(
            ApprovalStep,
            name="Avaliação do compliance | Sustentabilidade",
            order=4,
            department="Financeiro",
        ),
        baker.make(
            ApprovalStep,
            name="Avaliação do gestor",
            order=5,
            department="Administrativo",
        ),
        baker.make(
            ApprovalStep, name="Avaliação jurídica", order=6, department="Jurídico"
        ),
        baker.make(
            ApprovalStep, name="Avaliação diretoria", order=7, department="Diretoria"
        ),
        baker.make(
            ApprovalStep,
            name="Aprovação final do fluxo",
            order=8,
            department="Diretoria",
        ),
    ]
    return steps


def approve_step(
    api_client, flow_id, approver_name, department, comments="", is_approved=True
):
    """
    Utilitário para aprovar ou rejeitar um passo em um fluxo de aprovação.

    Args:
        api_client: Cliente API para fazer a requisição
        flow_id: ID do fluxo de aprovação
        approver_name: Nome do aprovador
        department: Departamento do aprovador
        comments: Comentários opcionais
        is_approved: Indica se o passo foi aprovado ou rejeitado

    Returns:
        Resposta da requisição
    """
    url = reverse("supplier:approval-flows-approve-step", kwargs={"pk": flow_id})
    data = {
        "approver_name": approver_name,
        "approver_department": department,
        "comments": comments,
        "is_approved": is_approved,
    }

    return api_client.post(url, data, format="json")


def get_flow_status(api_client, flow_id):
    """
    Utilitário para obter o status atual de um fluxo de aprovação.

    Args:
        api_client: Cliente API para fazer a requisição
        flow_id: ID do fluxo de aprovação

    Returns:
        Dados do fluxo de aprovação
    """
    url = reverse("supplier:approval-flows-detail", kwargs={"pk": flow_id})
    response = api_client.get(url)

    if response.status_code == status.HTTP_200_OK:
        return response.data

    return None
