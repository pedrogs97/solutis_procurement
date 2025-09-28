"""
Testes unitários para os serializadores do fluxo de aprovação de fornecedores.
"""

import pytest
from model_bakery import baker

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    Approver,
    StepApproval,
)
from src.supplier.serializers.approval_workflow import (
    ApprovalFlowSerializer,
    ApprovalStepSerializer,
    ApproverSerializer,
    ApproveStepSerializer,
    StepApprovalSerializer,
)


@pytest.mark.django_db
class TestApproverSerializer:
    """Testes unitários para o serializador ApproverSerializer."""

    def test_serialization(self):
        """Teste de serialização de um aprovador."""
        approver = baker.make(
            Approver, name="João Silva", email="joao.silva@company.com"
        )

        serializer = ApproverSerializer(instance=approver)
        data = serializer.data

        assert data["id"] == approver.id
        assert data["name"] == "João Silva"
        assert data["email"] == "joao.silva@company.com"
        assert "created_at" in data
        assert "updated_at" in data

    def test_deserialization(self):
        """Teste de deserialização de um aprovador."""
        data = {"name": "Maria Santos", "email": "maria.santos@company.com"}

        serializer = ApproverSerializer(data=data)
        assert serializer.is_valid()

        approver = serializer.save()
        assert approver.name == "Maria Santos"
        assert approver.email == "maria.santos@company.com"


@pytest.mark.django_db
class TestApprovalStepSerializer:
    """Testes unitários para o serializador ApprovalStepSerializer."""

    def test_serialization(self):
        """Teste de serialização de um passo de aprovação."""
        step = baker.make(
            ApprovalStep,
            name="Passo Teste",
            description="Descrição do passo",
            order=1,
            department="Departamento Teste",
            is_mandatory=True,
        )

        serializer = ApprovalStepSerializer(instance=step)
        data = serializer.data

        assert data["id"] == step.id
        assert data["name"] == "Passo Teste"
        assert data["description"] == "Descrição do passo"
        assert data["order"] == 1
        assert data["department"] == "Departamento Teste"
        assert data["is_mandatory"] is True

    def test_deserialization(self):
        """Teste de deserialização de um passo de aprovação."""
        data = {
            "name": "Novo Passo",
            "description": "Nova descrição",
            "order": 5,
            "department": "Novo Departamento",
            "is_mandatory": False,
        }

        serializer = ApprovalStepSerializer(data=data)
        assert serializer.is_valid()

        step = serializer.save()
        assert step.name == "Novo Passo"
        assert step.description == "Nova descrição"
        assert step.order == 5
        assert step.department == "Novo Departamento"
        assert step.is_mandatory is False


@pytest.mark.django_db
class TestStepApprovalSerializer:
    """Testes unitários para o serializador StepApprovalSerializer."""

    def test_serialization(self, supplier):
        """Teste de serialização de uma aprovação de passo."""
        step = baker.make(
            ApprovalStep, name="Passo de Aprovação", order=1, department="Departamento"
        )
        flow = baker.make(ApprovalFlow, supplier=supplier)

        approver = baker.make(
            Approver, name="Nome do Aprovador", email="aprovador@company.com"
        )

        approval = baker.make(
            StepApproval,
            approval_flow=flow,
            step=step,
            approver=approver,
            comments="Comentários da aprovação",
            is_approved=True,
        )

        serializer = StepApprovalSerializer(instance=approval)
        data = serializer.data

        assert data["id"] == approval.id
        assert data["step"] == step.id
        assert data["step_name"] == "Passo de Aprovação"
        assert data["step_department"] == "Departamento"
        assert data["approver"] == approver.id
        assert data["approver_detail"]["name"] == "Nome do Aprovador"
        assert data["approver_detail"]["email"] == "aprovador@company.com"
        assert data["comments"] == "Comentários da aprovação"
        assert data["is_approved"] is True
        assert "approval_date" in data
        assert "created_at" in data
        assert "updated_at" in data


@pytest.mark.django_db
class TestApprovalFlowSerializer:
    """Testes unitários para o serializador ApprovalFlowSerializer."""

    def test_serialization(self, supplier):
        """Teste de serialização de um fluxo de aprovação."""
        step = baker.make(
            ApprovalStep, name="Passo do Fluxo", order=1, department="Departamento"
        )
        flow = baker.make(ApprovalFlow, supplier=supplier, current_step=step)

        approver = baker.make(
            Approver, name="Aprovador Teste", email="aprovador@company.com"
        )

        baker.make(
            StepApproval,
            approval_flow=flow,
            step=step,
            approver=approver,
        )

        serializer = ApprovalFlowSerializer(instance=flow)
        data = serializer.data

        assert data["id"] == flow.id
        assert data["supplier"] == supplier.id
        assert data["is_completed"] is False
        assert data["current_step"] == step.id
        assert data["current_step_detail"]["name"] == "Passo do Fluxo"
        assert len(data["step_approvals"]) == 1
        assert "start_date" in data
        assert "completion_date" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_deserialization(self, supplier):
        """Teste de deserialização de um fluxo de aprovação."""
        step = baker.make(
            ApprovalStep, name="Passo para o Fluxo", order=1, department="Departamento"
        )

        data = {"supplier": supplier.id, "current_step": step.id}

        serializer = ApprovalFlowSerializer(data=data)
        assert serializer.is_valid()

        flow = serializer.save()
        assert flow.supplier == supplier
        assert flow.current_step == step
        assert flow.is_completed is False


@pytest.mark.django_db
class TestApproveStepSerializer:
    """Testes unitários para o serializador ApproveStepSerializer."""

    def test_validation_valid_data(self, supplier):
        """Teste de validação com dados válidos."""
        step = baker.make(
            ApprovalStep, name="Passo para Aprovar", order=1, department="Financeiro"
        )
        flow = baker.make(ApprovalFlow, supplier=supplier, current_step=step)

        data = {
            "approver_name": "João Silva",
            "approver_email": "joao.silva@company.com",
            "comments": "Tudo certo",
            "is_approved": True,
        }

        serializer = ApproveStepSerializer(
            data=data, context={"flow_id": flow.id, "step_id": step.id}
        )

        assert serializer.is_valid()
        validated_data = serializer.validated_data
        assert "approver" in validated_data
        assert validated_data["approver"].name == "João Silva"
        assert validated_data["approver"].email == "joao.silva@company.com"

    def test_validation_creates_approver(self):
        """Teste que verifica se o aprovador é criado automaticamente."""
        data = {
            "approver_name": "Maria Santos",
            "approver_email": "maria.santos@company.com",
            "comments": "Aprovado",
            "is_approved": True,
        }

        serializer = ApproveStepSerializer(data=data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert "approver" in validated_data
        assert validated_data["approver"].name == "Maria Santos"
        assert validated_data["approver"].email == "maria.santos@company.com"

        # Verificar se o aprovador foi criado no banco
        assert Approver.objects.filter(email="maria.santos@company.com").exists()

    def test_validation_reuses_existing_approver(self):
        """Teste que verifica se o aprovador existente é reutilizado."""
        existing_approver = baker.make(
            Approver, name="Carlos Silva", email="carlos.silva@company.com"
        )

        data = {
            "approver_name": "Carlos Silva Atualizado",  # Nome diferente
            "approver_email": "carlos.silva@company.com",  # Email igual
            "comments": "Aprovado",
            "is_approved": True,
        }

        serializer = ApproveStepSerializer(data=data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert validated_data["approver"] == existing_approver
        # O nome não deve ser alterado, pois o aprovador já existe
        assert validated_data["approver"].name == "Carlos Silva"

    def test_validation_without_context(self):
        """Teste de validação sem contexto."""
        data = {
            "approver_name": "Ana Costa",
            "approver_email": "ana.costa@company.com",
            "comments": "Sem contexto",
            "is_approved": True,
        }

        serializer = ApproveStepSerializer(data=data)
        assert serializer.is_valid()
