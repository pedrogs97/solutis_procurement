"""
Signals for the evaluation app.
"""

import logging

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone

from src.supplier.models.evaluation import EvaluationPeriod

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_current_year_evaluation_periods(sender, **kwargs):
    """
    Creates evaluation periods for the current year after migrations.
    """
    if sender.name == "src.supplier":
        current_year = timezone.now().year
        EvaluationPeriod.create_evaluation_periods_for_year(current_year)
