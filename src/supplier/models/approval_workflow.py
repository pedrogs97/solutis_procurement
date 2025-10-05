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
        verbose_name=_("Email"), help_text=_("Email do aprovador"), unique=True
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

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="approval_flow_history",
        verbose_name=_("Fornecedor"),
    )
    step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.PROTECT,
        related_name="current_flows",
        verbose_name=_("Passo Atual"),
        help_text=_("Passo atual no fluxo de aprovação"),
    )
    approver = models.ForeignKey(
        Approver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_flows",
        verbose_name=_("Aprovador Atual"),
        help_text=_("Aprovador responsável pelo passo atual"),
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Aprovação"),
        help_text=_("Data em que o fluxo foi aprovado"),
    )
    reproved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Reprovação"),
        help_text=_("Data em que o fluxo foi reprovado"),
    )

    def approve(self):
        """Mark the approval flow as approved."""
        self.approved_at = timezone.now()
        self.reproved_at = None
        self.save()

    def reprove(self):
        """Mark the approval flow as reproved."""
        self.reproved_at = timezone.now()
        self.approved_at = None
        self.save()

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for ApprovalFlow model.
        """

        db_table = "approval_flow"
        verbose_name = _("Fluxo de Aprovação")
        verbose_name_plural = _("Fluxos de Aprovação")
        abstract = False
