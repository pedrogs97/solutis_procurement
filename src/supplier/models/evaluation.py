"""Evaluation models for supplier assessments."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from src.shared.models import TimestampedModel
from src.supplier.models.supplier import Supplier


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
        """
        Meta configuration for EvaluationCriterion model.
        """

        db_table = "evaluation_criterion"
        verbose_name = _("Critério de Avaliação")
        verbose_name_plural = _("Critérios de Avaliação")
        ordering = ["order"]
        abstract = False


class EvaluationPeriod(TimestampedModel):
    """
    Model representing evaluation periods for supplier assessments.
    Defines the time period for supplier evaluations.
    """

    name = models.CharField(max_length=100, verbose_name=_("Nome do Período"))
    start_date = models.DateField(verbose_name=_("Data Início"))
    end_date = models.DateField(verbose_name=_("Data Fim"))
    year = models.PositiveSmallIntegerField(
        verbose_name=_("Ano"),
        editable=False,  # Ano será gerado automaticamente
    )
    period_number = models.PositiveSmallIntegerField(
        verbose_name=_("Número do Período"),
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        help_text=_("Número do período no ano (1-3)"),
    )

    def save(self, *args, **kwargs):
        """Set the year based on the start_date if not provided."""
        if not self.year and self.start_date:
            self.year = self.start_date.year

        elif not self.year:
            self.year = timezone.now().year

        super().save(*args, **kwargs)

    @classmethod
    def get_current_evaluation_period(cls) -> Optional["EvaluationPeriod"]:
        """
        Gets the current evaluation period based on today's date.

        Returns:
            The current EvaluationPeriod or None if not found.
        """
        today = date.today()

        current_period = EvaluationPeriod.objects.filter(
            start_date__lte=today, end_date__gte=today
        ).first()

        return current_period

    @classmethod
    def create_evaluation_periods_for_year(
        cls,
        year: Optional[int] = None,
    ) -> List["EvaluationPeriod"]:
        """
        Creates the three evaluation periods for a given year.
        If no year is provided, uses the current year.

        Args:
            year: The year to create periods for.

        Returns:
            List of created EvaluationPeriod instances.
        """
        if year is None:
            year = datetime.now().year

        period_dates = [
            {
                "name": f"Primeiro Quadrimestre {year}",
                "start_date": date(year, 1, 1),
                "end_date": date(year, 4, 30),
                "period_number": 1,
            },
            {
                "name": f"Segundo Quadrimestre {year}",
                "start_date": date(year, 5, 1),
                "end_date": date(year, 8, 31),
                "period_number": 2,
            },
            {
                "name": f"Terceiro Quadrimestre {year}",
                "start_date": date(year, 9, 1),
                "end_date": date(year, 12, 31),
                "period_number": 3,
            },
        ]

        created_periods = []

        period_number_list = [
            period_data["period_number"] for period_data in period_dates
        ]
        existing = EvaluationPeriod.objects.filter(
            period_number__in=period_number_list, start_date__year=year
        ).exists()

        if not existing:
            created_periods = EvaluationPeriod.objects.bulk_create(
                [
                    EvaluationPeriod(**period_data, year=year)
                    for period_data in period_dates
                ]
            )

        return created_periods

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for EvaluationPeriod model.
        """

        db_table = "evaluation_period"
        verbose_name = _("Período de Avaliação")
        verbose_name_plural = _("Períodos de Avaliação")
        ordering = ["-year", "period_number"]
        unique_together = [["year", "period_number"]]
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
    period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name=_("Período"),
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
        """Calculate the final weighted score for this evaluation"""
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

    def save(self, *args, **kwargs):
        """
        Override save method to set final_score before saving.
        """
        self.final_score = self.calculate_final_score()
        super().save(*args, **kwargs)

    def get_last_criterion_score(self) -> Optional[EvaluationPeriod]:
        """
        Get the last criterion score for the supplier evaluation.
        """
        current_period = EvaluationPeriod.get_current_evaluation_period()

        if not current_period:
            EvaluationPeriod.create_evaluation_periods_for_year(datetime.now().year)
            current_period = EvaluationPeriod.get_current_evaluation_period()

        return (
            self.criterion_scores.select_related("period")
            .filter(period=current_period)
            .first()
        )

    def __str__(self):
        return f"Avaliação de {self.supplier} - {self.period} ({self.final_score}%)"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for SupplierEvaluation model.
        """

        db_table = "supplier_evaluation"
        verbose_name = _("Avaliação de Fornecedor")
        verbose_name_plural = _("Avaliações de Fornecedores")
        ordering = ["-evaluation_date"]
        unique_together = [["supplier", "period"]]
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
        """
        Meta configuration for CriterionScore model.
        """

        db_table = "criterion_score"
        verbose_name = _("Nota de Critério")
        verbose_name_plural = _("Notas de Critérios")
        unique_together = [["evaluation", "criterion"]]
        abstract = False
