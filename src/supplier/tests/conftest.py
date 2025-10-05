"""
Fixtures para os testes do fluxo de aprovação de fornecedores.
"""

import pytest
from django.utils import timezone
from model_bakery import baker
from rest_framework.test import APIClient

from src.supplier.models.approval_workflow import ApprovalFlow, ApprovalStep, Approver
from src.supplier.models.domain import DomPendencyType, DomSupplierSituation
from src.supplier.models.supplier import Supplier
from supplier.enums import DomPendecyTypeEnum


@pytest.fixture
def api_client():
    """Fixture para criar um cliente API para testes."""
    return APIClient()


@pytest.fixture
def supplier():
    """Fixture para criar um fornecedor para testes usando model_bakery."""
    supplier = baker.make(
        Supplier,
        trade_name="Fornecedor Teste",
        legal_name="Fornecedor Teste LTDA",
    )

    return supplier


@pytest.fixture
def approval_step():
    """Fixture para criar um passo de aprovação para testes usando model_bakery."""
    return baker.make(
        ApprovalStep,
        name="Passo Teste",
        description="Descrição do passo de teste",
        order=1,
        department="Departamento Teste",
        is_mandatory=True,
    )


@pytest.fixture
def basic_approval_flow(supplier, approval_step):
    """Fixture básica para criar um fluxo de aprovação simples para testes usando model_bakery."""
    return baker.make(ApprovalFlow, supplier=supplier, current_step=approval_step)


@pytest.fixture(autouse=True)
def setup_supplier_situation():
    """Fixture para garantir que exista pelo menos uma situação de fornecedor."""
    if (
        not DomSupplierSituation.objects.exists()
        and not DomPendencyType.objects.exists()
    ):
        baker.make(
            DomPendencyType,
            id=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
            name="PENDÊNCIA DE CADASTRO",
        )
        baker.make(
            DomPendencyType,
            id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
            name="PENDÊNCIA DE DOCUMENTAÇÃO",
        )
        baker.make(
            DomPendencyType,
            id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
            name="PENDÊNCIA MATRIZ DE RESPONSABILIDADE",
        )
        baker.make(
            DomPendencyType,
            id=DomPendecyTypeEnum.PENDENCIA_AVALIACAO.value,
            name="PENDÊNCIA DE AVALIAÇÃO",
        )
        baker.make(
            DomSupplierSituation,
            name="ATIVO",
            pendency_type=None,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_AVALIACAO.value,
        )


@pytest.fixture
def approval_steps():
    """Fixture para criar os passos de aprovação baseados no fluxo da empresa."""
    steps_data = [
        {
            "name": "Cadastro inicial",
            "description": "Cadastro inicial do fornecedor no sistema",
            "order": 1,
            "department": "Administrativo",
            "is_mandatory": True,
        },
        {
            "name": "Validação geral do cadastro",
            "description": "Validação administrativa dos dados cadastrais do fornecedor",
            "order": 2,
            "department": "Administrativo",
            "is_mandatory": True,
        },
        {
            "name": "Validação geral do cadastro",
            "description": "Validação financeira dos dados cadastrais do fornecedor",
            "order": 3,
            "department": "Financeiro",
            "is_mandatory": True,
        },
        {
            "name": "Avaliação do compliance | Sustentabilidade",
            "description": "Avaliação de compliance e critérios de sustentabilidade do fornecedor",
            "order": 4,
            "department": "Financeiro",
            "is_mandatory": True,
        },
        {
            "name": "Avaliação do gestor",
            "description": "Avaliação e aprovação do gestor responsável",
            "order": 5,
            "department": "Administrativo",
            "is_mandatory": True,
        },
        {
            "name": "Avaliação jurídica",
            "description": "Análise jurídica dos contratos e documentação legal",
            "order": 6,
            "department": "Jurídico",
            "is_mandatory": True,
        },
        {
            "name": "Avaliação diretoria",
            "description": "Avaliação e decisão da diretoria",
            "order": 7,
            "department": "Diretoria",
            "is_mandatory": True,
        },
        {
            "name": "Aprovação final do fluxo",
            "description": "Aprovação final e conclusão do processo de aprovação",
            "order": 8,
            "department": "Diretoria",
            "is_mandatory": True,
        },
    ]

    steps = []
    for step_data in steps_data:
        step = baker.make(ApprovalStep, **step_data)
        steps.append(step)

    return steps


@pytest.fixture
def approval_flow(supplier, approval_steps):
    """Fixture para criar um fluxo de aprovação completo."""
    flow = baker.make(
        ApprovalFlow,
        supplier=supplier,
        current_step=approval_steps[0],  # Começa no primeiro passo
    )
    return flow


@pytest.fixture
def sample_approver():
    """Fixture para criar um aprovador de exemplo."""
    return baker.make(Approver, name="João Silva", email="joao.silva@company.com")


@pytest.fixture
def completed_approval_flow(supplier, approval_steps):
    """Fixture para criar um fluxo de aprovação completamente processado."""
    flow = baker.make(
        ApprovalFlow,
        supplier=supplier,
        current_step=None,  # Fluxo completado
        completion_date=timezone.now(),
    )

    # Criar aprovações para todos os passos
    for step in approval_steps:
        # Criar um aprovador específico para cada departamento
        approver = baker.make(
            Approver,
            name=f"Aprovador {step.department}",
            email=f"aprovador.{step.department.lower()}@company.com",
        )

    return flow
