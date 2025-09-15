"""
Tests for evaluation views and signals.
This module contains tests for all evaluation-related views and signals including
EvaluationCriterionViewSet, EvaluationPeriodViewSet, SupplierEvaluationViewSet,
and the signal for automatic period creation.
"""

import json
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from src.supplier.enums import DomPendecyTypeEnum
from src.supplier.models.domain import (
    DomCategory,
    DomPendencyType,
    DomSupplierSituation,
    DomTypeSupplier,
)
from src.supplier.models.evaluation import (
    CriterionScore,
    EvaluationCriterion,
    EvaluationPeriod,
    SupplierEvaluation,
)
from src.supplier.models.supplier import Supplier
from src.supplier.signals.evaluation import create_current_year_evaluation_periods


def setup_situation():
    """Set up supplier situation."""
    DomPendencyType.objects.create(name="PENDENCIA_CADASTRO")
    DomPendencyType.objects.create(name="PENDENCIA_DOCUMENTACAO")
    DomPendencyType.objects.create(name="PENDENCIA_MATRIZ_RESPONSABILIDADE")
    DomPendencyType.objects.create(name="PENDENCIA_AVALIACAO")
    DomSupplierSituation.objects.create(name="ATIVO")
    DomSupplierSituation.objects.create(
        name="PENDENTE",
        pendency_type_id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
    )
    DomSupplierSituation.objects.create(
        name="PENDENTE",
        pendency_type_id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
    )
    DomSupplierSituation.objects.create(
        name="PENDENTE",
        pendency_type_id=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
    )


class EvaluationSignalTestCase(TestCase):
    """
    Tests for the evaluation signals.
    """

    def setUp(self):
        """Set up test data."""
        self.current_year = timezone.now().year
        EvaluationPeriod.objects.all().delete()

    @patch(
        "src.supplier.models.evaluation.EvaluationPeriod.create_evaluation_periods_for_year"
    )
    def test_post_migrate_signal(self, mock_create_periods):
        """Test that post_migrate signal creates periods for current year."""
        mock_create_periods.return_value = [
            EvaluationPeriod(
                name=f"Test Period {i}", period_number=i, year=self.current_year
            )
            for i in range(1, 3)
        ]

        class SenderMock:
            name = "src.supplier"

        sender_mock = SenderMock()

        create_current_year_evaluation_periods(sender=sender_mock)

        mock_create_periods.assert_called_once_with(self.current_year)


class EvaluationUtilsTestCase(TestCase):
    """
    Tests for the evaluation utilities.
    """

    def setUp(self):
        """Set up test data."""
        self.current_year = timezone.now().year
        EvaluationPeriod.objects.all().delete()

    def test_create_evaluation_periods_for_year(self):
        """Test creating evaluation periods for a specific year."""
        created_periods = EvaluationPeriod.create_evaluation_periods_for_year(
            self.current_year
        )

        self.assertEqual(len(created_periods), 3)

        db_periods = EvaluationPeriod.objects.filter(year=self.current_year)
        self.assertEqual(db_periods.count(), 3)

        first_period = db_periods.get(period_number=1)
        self.assertEqual(first_period.start_date, date(self.current_year, 1, 1))
        self.assertEqual(first_period.end_date, date(self.current_year, 4, 30))

        second_period = db_periods.get(period_number=2)
        self.assertEqual(second_period.start_date, date(self.current_year, 5, 1))
        self.assertEqual(second_period.end_date, date(self.current_year, 8, 31))

        third_period = db_periods.get(period_number=3)
        self.assertEqual(third_period.start_date, date(self.current_year, 9, 1))
        self.assertEqual(third_period.end_date, date(self.current_year, 12, 31))

    def test_create_periods_idempotent(self):
        """Test that creating periods for the same year is idempotent."""
        first_creation = EvaluationPeriod.create_evaluation_periods_for_year(
            self.current_year
        )
        self.assertEqual(len(first_creation), 3)

        second_creation = EvaluationPeriod.create_evaluation_periods_for_year(
            self.current_year
        )

        self.assertEqual(len(second_creation), 0)

        self.assertEqual(
            EvaluationPeriod.objects.filter(year=self.current_year).count(), 3
        )

    def test_get_current_evaluation_period(self):
        """Test getting the current evaluation period."""
        created_periods = EvaluationPeriod.create_evaluation_periods_for_year(
            self.current_year
        )
        self.assertEqual(len(created_periods), 3)

        db_periods = EvaluationPeriod.objects.filter(year=self.current_year)
        self.assertEqual(db_periods.count(), 3)

        today = date(self.current_year, 2, 15)
        with patch("src.supplier.models.evaluation.date") as mock_date:
            mock_date.today.return_value = today
            mock_date.side_effect = lambda: today
            current_period = EvaluationPeriod.get_current_evaluation_period()
            self.assertIsNotNone(current_period)
            if current_period:
                self.assertEqual(current_period.period_number, 1)

        today = date(self.current_year, 6, 15)
        with patch("src.supplier.models.evaluation.date") as mock_date:
            mock_date.today.return_value = today
            mock_date.side_effect = lambda: today
            current_period = EvaluationPeriod.get_current_evaluation_period()
            self.assertIsNotNone(current_period)
            if current_period:
                self.assertEqual(current_period.period_number, 2)

        today = date(self.current_year, 10, 15)
        with patch("src.supplier.models.evaluation.date") as mock_date:
            mock_date.today.return_value = today
            mock_date.side_effect = lambda: today
            current_period = EvaluationPeriod.get_current_evaluation_period()
            self.assertIsNotNone(current_period)
            if current_period:
                self.assertEqual(current_period.period_number, 3)


class BaseEvaluationViewTestCase(TestCase):
    """
    Base class for evaluation view tests.
    """

    def setUp(self):
        """Set up test data for all evaluation view tests."""
        self.client = APIClient()
        EvaluationPeriod.objects.all().delete()

        self.supplier_category = DomCategory.objects.create(name="Test Category")
        self.supplier_type = DomTypeSupplier.objects.create(name="Test Type")

        setup_situation()

        self.supplier = Supplier.objects.create(
            trade_name="Test Supplier",
            legal_name="Test Legal Name",
            tax_id="12345678901234",
            category=self.supplier_category,
            type=self.supplier_type,
        )

        self.criterion1 = EvaluationCriterion.objects.create(
            name="Quality",
            description="Product quality assessment",
            weight=Decimal("30.00"),
            order=1,
        )
        self.criterion2 = EvaluationCriterion.objects.create(
            name="Delivery Time",
            description="Timeliness of deliveries",
            weight=Decimal("40.00"),
            order=2,
        )
        self.criterion3 = EvaluationCriterion.objects.create(
            name="Price",
            description="Price competitiveness",
            weight=Decimal("30.00"),
            order=3,
        )

        self.current_year = timezone.now().year
        self.period = EvaluationPeriod.objects.create(
            name=f"First Quadrimester {self.current_year}",
            start_date=date(self.current_year, 1, 1),
            end_date=date(self.current_year, 4, 30),
            period_number=1,
        )

        self.evaluation = SupplierEvaluation.objects.create(
            supplier=self.supplier,
            period=self.period,
            evaluator_name="Test Evaluator",
            comments="Initial evaluation comments",
        )

        self.score1 = CriterionScore.objects.create(
            evaluation=self.evaluation,
            criterion=self.criterion1,
            score=Decimal("80.00"),
            comments="Good quality",
        )
        self.score2 = CriterionScore.objects.create(
            evaluation=self.evaluation,
            criterion=self.criterion2,
            score=Decimal("70.00"),
            comments="Acceptable delivery times",
        )
        self.score3 = CriterionScore.objects.create(
            evaluation=self.evaluation,
            criterion=self.criterion3,
            score=Decimal("90.00"),
            comments="Excellent pricing",
        )

        self.evaluation.save()
        weighted_sum = (
            self.score1.score * self.criterion1.weight
            + self.score2.score * self.criterion2.weight
            + self.score3.score * self.criterion3.weight
        )
        total_weight = (
            self.criterion1.weight + self.criterion2.weight + self.criterion3.weight
        )

        self.assertEqual(self.evaluation.final_score, weighted_sum / total_weight)


class EvaluationCriterionViewSetTestCase(BaseEvaluationViewTestCase):
    """
    Tests for the EvaluationCriterionViewSet views.
    """

    def test_list_criteria(self):
        """Test retrieving all evaluation criteria."""
        url = reverse("evaluation-criterion-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["name"], "Quality")
        self.assertEqual(results[1]["name"], "Delivery Time")
        self.assertEqual(results[2]["name"], "Price")

    def test_create_criterion(self):
        """Test creating a new evaluation criterion."""
        url = reverse("evaluation-criterion")
        data = {
            "name": "Customer Service",
            "description": "Quality of customer service",
            "weight": "20.00",
            "order": 4,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EvaluationCriterion.objects.count(), 4)
        result = json.loads(response.content)
        self.assertEqual(result["name"], "Customer Service")
        self.assertEqual(result["weight"], "20.00")

    def test_update_criterion(self):
        """Test updating an evaluation criterion."""
        url = reverse("evaluation-criterion-detail", args=[self.criterion1.pk])
        updated_name = "Product Quality edit"
        updated_description = "Updated quality description"
        data = {
            "name": updated_name,
            "description": updated_description,
            "weight": "35.00",
            "order": 1,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.criterion1.refresh_from_db()
        self.assertEqual(self.criterion1.name, updated_name)
        self.assertEqual(self.criterion1.description, updated_description)
        self.assertEqual(self.criterion1.weight, Decimal("35.00"))


# class SupplierEvaluationViewSetTestCase(BaseEvaluationViewTestCase):
#     """
#     Tests for the SupplierEvaluationViewSet views.
#     """

#     def test_list_evaluations(self):
#         """Test retrieving all supplier evaluations."""
#         url = reverse("supplier-evaluation-list")
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         data = json.loads(response.content)
#         self.assertEqual(len(data), 1)
#         self.assertEqual(data[0]["supplier"]["name"], "Test Supplier")
#         self.assertEqual(
#             data[0]["period"]["name"], f"First Quadrimester {self.current_year}"
#         )

#     def test_create_evaluation(self):
#         """Test creating a new supplier evaluation."""
#         # Create a new period for testing
#         second_period = EvaluationPeriod.objects.create(
#             name=f"Second Quadrimester {self.current_year}",
#             start_date=date(self.current_year, 5, 1),
#             end_date=date(self.current_year, 8, 31),
#             period_number=2,
#         )

#         url = reverse("supplier-evaluation-list")
#         data = {
#             "supplier": self.supplier.pk,
#             "period": second_period.pk,
#             "evaluator_name": "Another Evaluator",
#             "evaluation_date": str(date.today()),
#             "comments": "Follow-up evaluation",
#         }
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(SupplierEvaluation.objects.count(), 2)
#         result = json.loads(response.content)
#         self.assertEqual(result["evaluator_name"], "Another Evaluator")
#         self.assertIsNone(result["final_score"])  # No scores added yet

#     def test_retrieve_evaluation_detail(self):
#         """Test retrieving detailed information about an evaluation."""
#         url = reverse("supplier-evaluation-detail", args=[self.evaluation.pk])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         result = json.loads(response.content)
#         self.assertEqual(result["pk"], self.evaluation.pk)
#         self.assertEqual(len(result["criterion_scores"]), 3)
#         self.assertIsNotNone(result["final_score"])

#     def test_filter_evaluations_by_supplier(self):
#         """Test filtering evaluations by supplier."""
#         url = reverse("supplier-evaluation-list")
#         response = self.client.get(f"{url}?supplier={self.supplier.pk}")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         data = json.loads(response.content)
#         self.assertEqual(len(data), 1)
#         self.assertEqual(data[0]["supplier"]["pk"], self.supplier.pk)

#     def test_filter_evaluations_by_period(self):
#         """Test filtering evaluations by period."""
#         url = reverse("supplier-evaluation-list")
#         response = self.client.get(f"{url}?period={self.period.pk}")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         data = json.loads(response.content)
#         self.assertEqual(len(data), 1)
#         self.assertEqual(data[0]["period"]["pk"], self.period.pk)

#     def test_filter_evaluations_by_year(self):
#         """Test filtering evaluations by year."""
#         url = reverse("supplier-evaluation-list")
#         response = self.client.get(f"{url}?year={self.current_year}")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         data = json.loads(response.content)
#         self.assertEqual(len(data), 1)
#         self.assertEqual(data[0]["period"]["year"], self.current_year)

#     def test_summary_action(self):
#         """Test the summary action."""
#         url = reverse("supplier-evaluation-summary")
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         data = json.loads(response.content)
#         self.assertEqual(len(data), 1)

#     def test_supplier_history_action(self):
#         """Test the supplier history action."""
#         url = reverse("supplier-evaluation-supplier-history")
#         response = self.client.get(f"{url}?supplier={self.supplier.pk}")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         data = json.loads(response.content)
#         self.assertEqual(len(data), 1)

#         # Test without supplier parameter
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_add_criterion_scores_action(self):
#         """Test adding criterion scores to an evaluation."""
#         # Create a new evaluation without scores
#         new_period = EvaluationPeriod.objects.create(
#             name=f"Second Quadrimester {self.current_year}",
#             start_date=date(self.current_year, 5, 1),
#             end_date=date(self.current_year, 8, 31),
#             period_number=2,
#         )

#         new_evaluation = SupplierEvaluation.objects.create(
#             supplier=self.supplier,
#             period=new_period,
#             evaluator_name="Test Evaluator 2",
#             comments="Evaluation without scores",
#         )

#         url = reverse(
#             "supplier-evaluation-add-criterion-scores", args=[new_evaluation.pk]
#         )
#         data = [
#             {
#                 "criterion": self.criterion1.pk,
#                 "score": "85.00",
#                 "comments": "Better quality",
#             },
#             {
#                 "criterion": self.criterion2.pk,
#                 "score": "75.00",
#                 "comments": "Improved delivery",
#             },
#         ]
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         new_evaluation.refresh_from_db()

#         # Query the scores directly from the database to avoid attribute access errors
#         criterion_scores = CriterionScore.objects.filter(evaluation=new_evaluation)
#         self.assertEqual(criterion_scores.count(), 2)
#         self.assertIsNotNone(new_evaluation.final_score)

#         # Verify scores were added correctly
#         scores = list(criterion_scores)
#         self.assertEqual(scores[0].score, Decimal("85.00"))
#         self.assertEqual(scores[1].score, Decimal("75.00"))
