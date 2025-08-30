"""
Utils for evaluation management.
"""

from datetime import date, datetime
from typing import List, Optional

from src.supplier.models.evaluation import EvaluationPeriod


def create_evaluation_periods_for_year(
    year: Optional[int] = None,
) -> List[EvaluationPeriod]:
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

    period_number_list = [period_data["period_number"] for period_data in period_dates]
    existing = EvaluationPeriod.objects.filter(
        period_number__in=period_number_list, start_date__year=year
    ).exists()

    if not existing:
        created_periods = EvaluationPeriod.objects.bulk_create(
            [EvaluationPeriod(**period_data, year=year) for period_data in period_dates]
        )

    return created_periods


def get_current_evaluation_period() -> Optional[EvaluationPeriod]:
    """
    Gets the current evaluation period based on today's date.

    Returns:
        The current EvaluationPeriod or None if not found.
    """
    today = date.today()

    # Try to find a period that includes today's date
    current_period = EvaluationPeriod.objects.filter(
        start_date__lte=today, end_date__gte=today
    ).first()

    return current_period
