"""Evaluation period type choices for supplier evaluation."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EvaluationPeriodType(models.TextChoices):  # pylint: disable=too-many-ancestors
    """Supported fixed period types for supplier evaluation."""

    QUADRIMESTER = "QUADRIMESTER", _("Quadrimestre")
    SEMESTER = "SEMESTER", _("Semestre")
