"""Evaluation models for supplier assessments."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from src.shared.models import TimestampedModel
from src.supplier.models.supplier import Supplier


class EvaluationPeriodType(models.TextChoices):
    """Supported fixed period types for supplier evaluation."""

    QUADRIMESTER = "QUADRIMESTER", _("Quadrimestre")
    SEMESTER = "SEMESTER", _("Semestre")


MIXED_PERIOD_TYPE_ERROR = _(
    "Já existe avaliação para este fornecedor nesse ano com outro tipo de período."
)


class EvaluationCriterion(TimestampedModel):
    """
    Model representing evaluation criteria for supplier assessments.
    Contains the criteria name, description, and weight for supplier evaluations.
    """

    name = models.CharField(max_length=100, verbose_name=_("Nome do Critério"))
    description = models.TextField(verbose_name=_("Descrição"))
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Peso (%)"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Ordem"))

    def __str__(self):
        return f"{self.name} - {self.weight}%"

    class Meta(TimestampedModel.Meta):
        """Meta configuration for EvaluationCriterion model."""

        db_table = "evaluation_criterion"
        verbose_name = _("Critério de Avaliação")
        verbose_name_plural = _("Critérios de Avaliação")
        ordering = ["order"]
        abstract = False


class SupplierEvaluationYearCycle(TimestampedModel):
    """
    One period-type lock per supplier and year.
    Prevents mixing quadrimester and semester in the same supplier/year.
    """

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="evaluation_year_cycles",
        verbose_name=_("Fornecedor"),
    )
    evaluation_year = models.PositiveSmallIntegerField(verbose_name=_("Ano"))
    period_type = models.CharField(
        max_length=20,
        choices=EvaluationPeriodType.choices,
        verbose_name=_("Tipo de Período"),
    )

    class Meta(TimestampedModel.Meta):
        """Meta configuration for SupplierEvaluationYearCycle model."""

        db_table = "supplier_evaluation_year_cycle"
        verbose_name = _("Ciclo Anual de Avaliação")
        verbose_name_plural = _("Ciclos Anuais de Avaliação")
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "evaluation_year"],
                name="supplier_eval_year_cycle_unique",
            )
        ]
        abstract = False


class SupplierEvaluation(TimestampedModel):
    """
    Model representing a complete evaluation for a supplier in a specific period.
    """

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name=_("Fornecedor"),
    )
    evaluation_year = models.PositiveSmallIntegerField(verbose_name=_("Ano"))
    period_type = models.CharField(
        max_length=20,
        choices=EvaluationPeriodType.choices,
        verbose_name=_("Tipo de Período"),
    )
    period_number = models.PositiveSmallIntegerField(
        verbose_name=_("Número do Período"),
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )
    evaluator_name = models.CharField(
        max_length=255, verbose_name=_("Nome do Avaliador")
    )
    evaluation_date = models.DateField(
        default=timezone.now, verbose_name=_("Data da Avaliação")
    )
    comments = models.TextField(blank=True, verbose_name=_("Observações"))
    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Pontuação Final (%)"),
        editable=False,
        null=True,
        blank=True,
    )

    def calculate_final_score(self):
        """Calculate the final weighted score for this evaluation."""
        criterion_scores = (
            self.criterion_scores.all() if hasattr(self, "pk") and self.pk else []
        )

        if not criterion_scores:
            return None

        total_weight = Decimal("0.00")
        weighted_sum = Decimal("0.00")

        for score in criterion_scores:
            total_weight += score.criterion.weight
            weighted_sum += score.score * score.criterion.weight

        if total_weight <= 0:
            return Decimal("0.00")

        result = weighted_sum / total_weight

        if not isinstance(result, Decimal):
            result = Decimal(str(result))

        return result.quantize(Decimal("0.01"))

    @staticmethod
    def _resolve_period_label(period_type: str, period_number: int) -> str:
        if period_type == EvaluationPeriodType.QUADRIMESTER:
            return f"{period_number}º Quadrimestre"
        if period_type == EvaluationPeriodType.SEMESTER:
            return f"{period_number}º Semestre"
        return ""

    @property
    def period_label(self) -> str:
        """Human-readable period label."""
        return self._resolve_period_label(self.period_type, self.period_number)

    @classmethod
    def sync_year_cycle_lock(cls, supplier_id: int, evaluation_year: int) -> None:
        """
        Keep lock table in sync with existing evaluations for supplier/year.
        """
        existing_period_types = list(
            cls.objects.filter(supplier_id=supplier_id, evaluation_year=evaluation_year)
            .values_list("period_type", flat=True)
            .distinct()
        )

        if not existing_period_types:
            SupplierEvaluationYearCycle.objects.filter(
                supplier_id=supplier_id, evaluation_year=evaluation_year
            ).delete()
            return

        locked_period_type = existing_period_types[0]
        SupplierEvaluationYearCycle.objects.update_or_create(
            supplier_id=supplier_id,
            evaluation_year=evaluation_year,
            defaults={"period_type": locked_period_type},
        )

    def _ensure_year_cycle_lock(self) -> None:
        lock, created = SupplierEvaluationYearCycle.objects.get_or_create(
            supplier_id=self.supplier_id,
            evaluation_year=self.evaluation_year,
            defaults={"period_type": self.period_type},
        )
        if not created and lock.period_type != self.period_type:
            raise ValidationError({"period_type": MIXED_PERIOD_TYPE_ERROR})

    def save(self, *args, **kwargs):
        """
        Override save method to set final_score and enforce annual cycle lock.
        """
        previous_state = None
        if self.pk:
            previous_state = (
                SupplierEvaluation.objects.filter(pk=self.pk)
                .values("supplier_id", "evaluation_year")
                .first()
            )

        self.final_score = self.calculate_final_score()

        with transaction.atomic():
            self._ensure_year_cycle_lock()
            super().save(*args, **kwargs)
            self.sync_year_cycle_lock(self.supplier_id, self.evaluation_year)

            if previous_state and (
                previous_state["supplier_id"] != self.supplier_id
                or previous_state["evaluation_year"] != self.evaluation_year
            ):
                self.sync_year_cycle_lock(
                    previous_state["supplier_id"], previous_state["evaluation_year"]
                )

    def delete(self, *args, **kwargs):
        """
        Override delete method to keep annual cycle locks consistent.
        """
        previous_supplier_id = self.supplier_id
        previous_evaluation_year = self.evaluation_year

        with transaction.atomic():
            result = super().delete(*args, **kwargs)
            self.sync_year_cycle_lock(previous_supplier_id, previous_evaluation_year)

        return result

    def __str__(self):
        return (
            f"Avaliação de {self.supplier} - {self.period_label}/{self.evaluation_year} "
            f"({self.final_score}%)"
        )

    class Meta(TimestampedModel.Meta):
        """Meta configuration for SupplierEvaluation model."""

        db_table = "supplier_evaluation"
        verbose_name = _("Avaliação de Fornecedor")
        verbose_name_plural = _("Avaliações de Fornecedores")
        ordering = [
            "-evaluation_year",
            "period_type",
            "-period_number",
            "-evaluation_date",
            "-id",
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    period_type__in=[
                        EvaluationPeriodType.QUADRIMESTER,
                        EvaluationPeriodType.SEMESTER,
                    ]
                ),
                name="supplier_eval_period_type_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        period_type=EvaluationPeriodType.QUADRIMESTER,
                        period_number__in=[1, 2, 3],
                    )
                    | Q(
                        period_type=EvaluationPeriodType.SEMESTER,
                        period_number__in=[1, 2],
                    )
                ),
                name="supplier_eval_period_number_by_type_valid",
            ),
            models.UniqueConstraint(
                fields=["supplier", "evaluation_year", "period_type", "period_number"],
                name="supplier_eval_supplier_year_type_number_uniq",
            ),
        ]
        abstract = False


class CriterionScore(TimestampedModel):
    """
    Model representing an individual criterion score within a supplier evaluation.
    """

    evaluation = models.ForeignKey(
        SupplierEvaluation,
        on_delete=models.CASCADE,
        related_name="criterion_scores",
        verbose_name=_("Avaliação"),
    )
    criterion = models.ForeignKey(
        EvaluationCriterion,
        on_delete=models.PROTECT,
        related_name="scores",
        verbose_name=_("Critério"),
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Nota (%)"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    comments = models.TextField(blank=True, verbose_name=_("Comentários"))

    def __str__(self):
        return f"{self.criterion.name}: {self.score}%"

    class Meta(TimestampedModel.Meta):
        """Meta configuration for CriterionScore model."""

        db_table = "criterion_score"
        verbose_name = _("Nota de Critério")
        verbose_name_plural = _("Notas de Critérios")
        unique_together = [["evaluation", "criterion"]]
        abstract = False
