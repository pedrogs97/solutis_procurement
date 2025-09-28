"""
Testes unitários para os modelos do fluxo de aprovação de fornecedores.
"""

import pytest
from django.utils import timezone
from model_bakery import baker

from src.supplier.models.approval_workflow import (
    ApprovalFlow,
    ApprovalStep,
    Approver,
    StepApproval,
)


@pytest.mark.django_db
class TestApprovalStepModel:
    """Testes unitários para o modelo ApprovalStep."""

    def test_create_approval_step(self):
        """Teste de criação de um passo de aprovação."""
        step = baker.make(
            ApprovalStep,
            name="Teste de Passo",
            description="Descrição do passo de teste",
            order=1,
            department="Departamento Teste",
            is_mandatory=True,
        )

        assert step.pk is not None
        assert step.name == "Teste de Passo"
        assert step.order == 1
        assert step.department == "Departamento Teste"
        assert step.is_mandatory is True

    def test_str_method(self):
        """Teste do método __str__ do modelo ApprovalStep."""
        step = baker.make(
            ApprovalStep,
            name="Teste de Passo",
            order=42,
            department="Departamento Teste",
        )

        assert str(step) == "42. Teste de Passo (Departamento Teste)"

    def test_ordering(self):
        """Teste da ordenação dos passos de aprovação."""
        baker.make(ApprovalStep, name="Passo 3", order=3, department="Dep")
        baker.make(ApprovalStep, name="Passo 1", order=1, department="Dep")
        baker.make(ApprovalStep, name="Passo 2", order=2, department="Dep")

        steps = list(ApprovalStep.objects.all())
        assert steps[0].name == "Passo 1"
        assert steps[1].name == "Passo 2"
        assert steps[2].name == "Passo 3"


@pytest.mark.django_db
class TestApprovalFlowModel:
    """Testes unitários para o modelo ApprovalFlow."""

    def test_create_approval_flow(self, supplier):
        """Teste de criação de um fluxo de aprovação."""
        flow = baker.make(ApprovalFlow, supplier=supplier)

        assert flow.pk is not None
        assert flow.supplier == supplier
        assert flow.is_completed is False
        assert flow.current_step is None
        assert flow.start_date is not None
        assert flow.completion_date is None

    def test_complete_flow(self, supplier):
        """Teste do método complete_flow."""
        flow = baker.make(ApprovalFlow, supplier=supplier)

        assert flow.completion_date is None

        flow.complete_flow()

        assert flow.is_completed is True

        assert flow.completion_date is not None

        time_difference = timezone.now() - flow.completion_date
        assert time_difference.total_seconds() < 60

    def test_advance_to_next_step_with_no_steps(self, supplier):
        """Teste do método advance_to_next_step quando não há passos definidos."""
        ApprovalStep.objects.all().delete()
        flow = baker.make(ApprovalFlow, supplier=supplier)

        assert ApprovalStep.objects.count() == 0

        result = flow.advance_to_next_step()
        assert result is False
        assert flow.current_step is None

    def test_advance_to_next_step_with_first_step(self, supplier):
        """Teste do método advance_to_next_step iniciando no primeiro passo."""
        ApprovalStep.objects.all().delete()
        step1 = baker.make(ApprovalStep, name="Passo 1", order=1, department="Dep1")

        flow = baker.make(ApprovalFlow, supplier=supplier)

        result = flow.advance_to_next_step()
        assert result is True

        flow.refresh_from_db()
        assert flow.current_step == step1

    def test_advance_to_next_step_middle_step(self, supplier):
        """Teste do método advance_to_next_step avançando entre passos."""
        ApprovalStep.objects.all().delete()
        step1 = baker.make(ApprovalStep, name="Passo 1", order=1, department="Dep1")
        step2 = baker.make(ApprovalStep, name="Passo 2", order=2, department="Dep2")

        flow = baker.make(ApprovalFlow, supplier=supplier, current_step=step1)

        result = flow.advance_to_next_step()
        assert result is True

        flow.refresh_from_db()
        assert flow.current_step == step2

    def test_advance_to_next_step_final_step(self, supplier):
        """Teste do método advance_to_next_step no último passo."""
        ApprovalStep.objects.all().delete()
        baker.make(ApprovalStep, name="Passo 1", order=1, department="Dep1")
        step2 = baker.make(ApprovalStep, name="Passo 2", order=2, department="Dep2")

        flow = baker.make(ApprovalFlow, supplier=supplier, current_step=step2)

        result = flow.advance_to_next_step()
        assert result is True

        flow.refresh_from_db()
        assert flow.current_step is None
        assert flow.is_completed is True
        assert flow.completion_date is not None

    def test_advance_to_next_step_already_completed(self, supplier):
        """Teste do método advance_to_next_step quando o fluxo já está concluído."""
        flow = baker.make(
            ApprovalFlow, supplier=supplier, completion_date=timezone.now()
        )

        assert flow.is_completed is True

        result = flow.advance_to_next_step()
        assert result is False


@pytest.mark.django_db
class TestStepApprovalModel:
    """Testes unitários para o modelo StepApproval."""

    def test_create_step_approval(self, supplier):
        """Teste de criação de uma aprovação de passo."""
        step = baker.make(
            ApprovalStep, name="Passo Teste", order=1, department="Dep Teste"
        )
        flow = baker.make(ApprovalFlow, supplier=supplier, current_step=step)

        approver = baker.make(
            Approver, name="João Silva", email="joao.silva@company.com"
        )

        approval = baker.make(
            StepApproval,
            approval_flow=flow,
            step=step,
            approver=approver,
            comments="Aprovado sem ressalvas",
            is_approved=True,
        )

        assert approval.pk is not None
        assert approval.approval_flow == flow
        assert approval.step == step
        assert approval.approver == approver
        assert approval.approver.name == "João Silva"
        assert approval.approver.email == "joao.silva@company.com"
        assert approval.comments == "Aprovado sem ressalvas"
        assert approval.is_approved is True
        assert approval.approval_date is not None

    def test_unique_together_constraint(self, supplier):
        """Teste da constraint unique_together no modelo StepApproval."""
        step = baker.make(ApprovalStep, name="Passo Teste", order=1, department="Dep")
        flow = baker.make(ApprovalFlow, supplier=supplier)

        approver1 = baker.make(
            Approver, name="Aprovador", email="aprovador@company.com"
        )

        baker.make(
            StepApproval,
            approval_flow=flow,
            step=step,
            approver=approver1,
        )

        approver2 = baker.make(
            Approver, name="Outro Aprovador", email="outro.aprovador@company.com"
        )

        with pytest.raises(Exception):
            baker.make(
                StepApproval,
                approval_flow=flow,
                step=step,
                approver=approver2,
            )
