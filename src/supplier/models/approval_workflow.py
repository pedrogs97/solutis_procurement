"""
Supplier approval workflow models.
This module defines the approval workflow model for supplier approval process.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from src.shared.models import TimestampedModel
from src.supplier.models.supplier import Supplier


class Approver(TimestampedModel):
    """
    Model representing an approver in the approval workflow.
    Stores information about users who can approve steps.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("Nome"),
        help_text=_("Nome completo do aprovador"),
    )
    email = models.EmailField(
        verbose_name=_("Email"), help_text=_("Email do aprovador")
    )

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for Approver model.
        """

        db_table = "approver"
        verbose_name = _("Aprovador")
        verbose_name_plural = _("Aprovadores")
        ordering = ["name"]
        abstract = False


class ApprovalStep(TimestampedModel):
    """
    Model representing a step in the supplier approval workflow.
    Each step has a name, description, and order.
    """

    name = models.CharField(max_length=100, verbose_name=_("Nome do Passo"))
    description = models.TextField(verbose_name=_("Descrição"), blank=True)
    order = models.PositiveSmallIntegerField(
        verbose_name=_("Ordem"), help_text=_("Ordem de execução do passo no fluxo")
    )
    department = models.CharField(
        max_length=100,
        verbose_name=_("Departamento"),
        help_text=_("Departamento responsável por este passo"),
    )
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name=_("Obrigatório"),
        help_text=_("Indica se este passo é obrigatório no fluxo de aprovação"),
    )

    def __str__(self):
        return f"{self.order}. {self.name} ({self.department})"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for ApprovalStep model.
        """

        db_table = "approval_step"
        verbose_name = _("Passo de Aprovação")
        verbose_name_plural = _("Passos de Aprovação")
        ordering = ["order"]
        abstract = False


class ApprovalFlow(TimestampedModel):
    """
    Model representing the approval flow for a supplier.
    Tracks the approval process through various steps.
    """

    supplier = models.OneToOneField(
        Supplier,
        on_delete=models.CASCADE,
        related_name="approval_flow",
        verbose_name=_("Fornecedor"),
    )
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Data de Início"),
        help_text=_("Data de início do fluxo de aprovação"),
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Conclusão"),
        help_text=_("Data de conclusão do fluxo de aprovação"),
    )
    current_step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_flows",
        verbose_name=_("Passo Atual"),
        help_text=_("Passo atual no fluxo de aprovação"),
    )

    @property
    def is_completed(self):
        """Check if the flow is completed by verifying if completion_date is set."""
        return self.completion_date is not None

    def complete_flow(self):
        """Mark the approval flow as completed."""
        self.completion_date = timezone.now()
        self.current_step = None
        self.save()

    def advance_to_next_step(self):
        """Advance to the next step in the approval flow."""
        if self.is_completed:
            return False

        if not self.current_step:
            first_step = ApprovalStep.objects.order_by("order").first()
            if first_step:
                self.current_step = first_step
                self.save()
                return True
            return False

        next_step = (
            ApprovalStep.objects.filter(order__gt=self.current_step.order)
            .order_by("order")
            .first()
        )

        if next_step:
            self.current_step = next_step
            self.save()
            return True

        self.complete_flow()
        return True

    def __str__(self):
        status = "Concluído" if self.is_completed else "Em andamento"
        return f"Fluxo de aprovação - {self.supplier} - {status}"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for ApprovalFlow model.
        """

        db_table = "approval_flow"
        verbose_name = _("Fluxo de Aprovação")
        verbose_name_plural = _("Fluxos de Aprovação")
        abstract = False


class StepApproval(TimestampedModel):
    """
    Model representing the approval of a specific step in the approval flow.
    Contains information about who approved the step and when.
    """

    approval_flow = models.ForeignKey(
        ApprovalFlow,
        on_delete=models.CASCADE,
        related_name="step_approvals",
        verbose_name=_("Fluxo de Aprovação"),
    )
    step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.PROTECT,
        related_name="approvals",
        verbose_name=_("Passo de Aprovação"),
    )
    approver = models.ForeignKey(
        Approver,
        on_delete=models.PROTECT,
        related_name="step_approvals",
        verbose_name=_("Aprovador"),
        help_text=_("Usuário que realizou a aprovação"),
    )
    approval_date = models.DateTimeField(
        default=timezone.now, verbose_name=_("Data da Aprovação")
    )
    comments = models.TextField(blank=True, verbose_name=_("Observações"))
    is_approved = models.BooleanField(
        default=True,
        verbose_name=_("Aprovado"),
        help_text=_("Indica se o passo foi aprovado ou rejeitado"),
    )

    def __str__(self):
        status = "aprovado" if self.is_approved else "rejeitado"
        return f"{self.step.name} - {status} por {self.approver.name}"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for StepApproval model.
        """

        db_table = "step_approval"
        verbose_name = _("Aprovação de Passo")
        verbose_name_plural = _("Aprovações de Passos")
        ordering = ["approval_flow", "step__order"]
        unique_together = [["approval_flow", "step"]]
        abstract = False
