"""Tests for evaluation endpoints and model rules."""

import json
from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from src.supplier.models.domain import DomCategory, DomTypeSupplier
from src.supplier.models.evaluation import (
    CriterionScore,
    EvaluationCriterion,
    SupplierEvaluation,
    SupplierEvaluationYearCycle,
)
from src.supplier.models.supplier import Supplier


class BaseEvaluationViewTestCase(TestCase):
    """Base class for evaluation endpoint tests."""

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer test-token",
            HTTP_X_AUTHENTICATED_USER_ID="1",
            HTTP_X_AUTHENTICATED_USER_EMAIL="tests@solutis.com.br",
            HTTP_X_AUTHENTICATED_USER_FULL_NAME="Test User",
            HTTP_X_AUTHENTICATED_USER_GROUP="Compras",
        )

        self.supplier_category = DomCategory.objects.create(name="Test Category")
        self.supplier_type = DomTypeSupplier.objects.create(name="Test Type")

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

        self.evaluation = SupplierEvaluation.objects.create(
            supplier=self.supplier,
            evaluation_year=2026,
            period_type="QUADRIMESTER",
            period_number=1,
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
    """Tests for criterion endpoints."""

    def test_list_criteria(self):
        url = "/api/v1/evaluation/criteria-list/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["name"], "Quality")
        self.assertEqual(results[1]["name"], "Delivery Time")
        self.assertEqual(results[2]["name"], "Price")


class SupplierEvaluationViewSetTestCase(BaseEvaluationViewTestCase):
    """Tests for supplier evaluation endpoints."""

    def test_list_evaluations(self):
        url = "/api/v1/evaluation/evaluations-list/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["supplier"]["name"], "Test Supplier")
        self.assertEqual(results[0]["evaluationYear"], 2026)
        self.assertEqual(results[0]["periodType"], "QUADRIMESTER")
        self.assertEqual(results[0]["periodNumber"], 1)

    def test_create_evaluation(self):
        url = "/api/v1/evaluation/evaluations/"
        data = {
            "supplier": self.supplier.pk,
            "evaluationYear": 2026,
            "periodType": "QUADRIMESTER",
            "periodNumber": 2,
            "evaluatorName": "Another Evaluator",
            "evaluationDate": str(date.today()),
            "comments": "Follow-up evaluation",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupplierEvaluation.objects.count(), 2)
        result = json.loads(response.content)
        self.assertEqual(result["evaluatorName"], "Another Evaluator")
        self.assertEqual(result["evaluationYear"], 2026)
        self.assertEqual(result["periodType"], "QUADRIMESTER")
        self.assertEqual(result["periodNumber"], 2)
        self.assertIsNone(result["finalScore"])

    def test_rejects_legacy_period_payload(self):
        url = "/api/v1/evaluation/evaluations/"
        data = {
            "supplier": self.supplier.pk,
            "period": 99,
            "evaluatorName": "Legacy Client",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_supplier_year_period_returns_400(self):
        url = "/api/v1/evaluation/evaluations/"
        data = {
            "supplier": self.supplier.pk,
            "evaluationYear": 2026,
            "periodType": "QUADRIMESTER",
            "periodNumber": 1,
            "evaluatorName": "Duplicated",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_mixed_period_type_same_supplier_year(self):
        url = "/api/v1/evaluation/evaluations/"
        data = {
            "supplier": self.supplier.pk,
            "evaluationYear": 2026,
            "periodType": "SEMESTER",
            "periodNumber": 1,
            "evaluatorName": "Invalid",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_invalid_period_number_for_semester(self):
        url = "/api/v1/evaluation/evaluations/"
        data = {
            "supplier": self.supplier.pk,
            "evaluationYear": 2027,
            "periodType": "SEMESTER",
            "periodNumber": 3,
            "evaluatorName": "Invalid Number",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_evaluation_detail(self):
        url = f"/api/v1/evaluation/evaluations/{self.evaluation.pk}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content)
        self.assertEqual(result["id"], self.evaluation.pk)
        self.assertEqual(result["evaluationYear"], 2026)
        self.assertEqual(result["periodType"], "QUADRIMESTER")
        self.assertEqual(result["periodNumber"], 1)
        criterion_scores = result.get("criterionScores", [])
        self.assertEqual(len(criterion_scores), 3)
        self.assertIsNotNone(result["finalScore"])

    def test_filter_evaluations_by_supplier(self):
        url = "/api/v1/evaluation/evaluations-list/"
        response = self.client.get(f"{url}?supplier={self.supplier.pk}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)

    def test_filter_evaluations_by_year_type_number(self):
        url = "/api/v1/evaluation/evaluations-list/"
        response = self.client.get(
            f"{url}?evaluationYear=2026&periodType=QUADRIMESTER&periodNumber=1"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["evaluationYear"], 2026)
        self.assertEqual(data["results"][0]["periodType"], "QUADRIMESTER")
        self.assertEqual(data["results"][0]["periodNumber"], 1)

    def test_add_criterion_scores_action(self):
        new_evaluation = SupplierEvaluation.objects.create(
            supplier=self.supplier,
            evaluation_year=2026,
            period_type="QUADRIMESTER",
            period_number=2,
            evaluator_name="Test Evaluator 2",
            comments="Evaluation without scores",
        )

        url = f"/api/v1/evaluation/evaluations/{new_evaluation.pk}/scores/"
        data = [
            {
                "criterion": self.criterion1.pk,
                "score": "85.00",
                "comments": "Better quality",
            },
            {
                "criterion": self.criterion2.pk,
                "score": "75.00",
                "comments": "Improved delivery",
            },
        ]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_evaluation.refresh_from_db()

        criterion_scores = CriterionScore.objects.filter(evaluation=new_evaluation)
        self.assertEqual(criterion_scores.count(), 2)
        self.assertIsNotNone(new_evaluation.final_score)

    def test_creates_year_cycle_lock(self):
        self.assertTrue(
            SupplierEvaluationYearCycle.objects.filter(
                supplier=self.supplier,
                evaluation_year=2026,
                period_type="QUADRIMESTER",
            ).exists()
        )
