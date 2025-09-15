"""
Tests for ResponsibilityMatrix model.
This module contains tests for the ResponsibilityMatrix model including
creation, validation, relationships, and RACI matrix functionality.
"""

from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from src.supplier.enums import DomPendecyTypeEnum
from src.supplier.models.domain import DomPendencyType, DomSupplierSituation
from src.supplier.models.responsibility_matrix import RACI_CHOICES, ResponsibilityMatrix
from src.supplier.models.supplier import Supplier


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


class TestResponsibilityMatrix(TestCase):
    """Test cases for ResponsibilityMatrix model."""

    def setUp(self):
        """Set up test data."""
        setup_situation()
        self.supplier = baker.make(Supplier, trade_name="Test Supplier")

    def test_responsibility_matrix_creation(self):
        """Test responsibility matrix creation with default values."""
        matrix = baker.make(
            ResponsibilityMatrix,
            supplier=self.supplier,
            contract_request_requesting_area="A",
            contract_request_administrative="R",
        )

        self.assertEqual(matrix.supplier, self.supplier)
        self.assertEqual(matrix.contract_request_requesting_area, "A")
        self.assertEqual(matrix.contract_request_administrative, "R")

        self.assertEqual(matrix.contract_request_legal, "-")
        self.assertEqual(matrix.contract_request_financial, "-")

    def test_unique_supplier_constraint(self):
        """Test that each supplier can have only one responsibility matrix."""
        baker.make(ResponsibilityMatrix, supplier=self.supplier)

        with self.assertRaises(IntegrityError):
            baker.make(ResponsibilityMatrix, supplier=self.supplier)

    def test_all_activities_have_default_values(self):
        """Test that all 12 activities have proper default values."""
        matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)

        activities = [
            "contract_request_requesting_area",
            "contract_request_administrative",
            "contract_request_legal",
            "contract_request_financial",
            "contract_request_integrity",
            "contract_request_board",
            "document_analysis_requesting_area",
            "document_analysis_administrative",
            "document_analysis_legal",
            "document_analysis_financial",
            "document_analysis_integrity",
            "document_analysis_board",
        ]

        for activity in activities:
            value = getattr(matrix, activity)
            self.assertIn(value, [choice[0] for choice in RACI_CHOICES])

    def test_matrix_cascade_deletion(self):
        """Test that matrix is deleted when supplier is deleted."""
        matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)
        matrix_id = matrix.pk

        self.supplier.delete()

        self.assertFalse(ResponsibilityMatrix.objects.filter(id=matrix_id).exists())

    def test_raci_choices_constants(self):
        """Test that RACI_CHOICES contains expected values."""
        expected_choices = [
            ("A", "A - Accountable (Responsável)"),
            ("R", "R - Responsible (Executa)"),
            ("C", "C - Consulted (Consultado)"),
            ("I", "I - Informed (Informado)"),
            ("-", "- Não Envolvido"),
            ("A/R", "A/R - Responsável e Executa"),
        ]

        self.assertEqual(RACI_CHOICES, expected_choices)

    def test_matrix_activities_coverage(self):
        """Test that all business activities are covered in the matrix."""
        matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)

        contract_activities = [
            "contract_request_requesting_area",
            "contract_request_administrative",
            "contract_request_legal",
            "contract_request_financial",
            "contract_request_integrity",
            "contract_request_board",
        ]

        analysis_activities = [
            "document_analysis_requesting_area",
            "document_analysis_administrative",
            "document_analysis_legal",
            "document_analysis_financial",
            "document_analysis_integrity",
            "document_analysis_board",
        ]

        for activity in contract_activities + analysis_activities:
            self.assertTrue(hasattr(matrix, activity))
            value = getattr(matrix, activity)
            self.assertIsNotNone(value)

    def test_responsibility_matrix_custom_values(self):
        """Test responsibility matrix creation with custom RACI values."""
        matrix = ResponsibilityMatrix.objects.create(
            supplier=self.supplier,
            contract_request_requesting_area="A",
            contract_request_administrative="R",
            document_analysis_legal="C",
            risk_consultation_board="I",
        )

        self.assertEqual(matrix.contract_request_requesting_area, "A")
        self.assertEqual(matrix.contract_request_administrative, "R")
        self.assertEqual(matrix.document_analysis_legal, "C")
        self.assertEqual(matrix.risk_consultation_board, "I")

    def test_all_activity_fields_present(self):
        """Test that all expected activity fields are present."""
        matrix = ResponsibilityMatrix.objects.create(supplier=self.supplier)

        # Ccontract request activity fields
        self.assertTrue(hasattr(matrix, "contract_request_requesting_area"))
        self.assertTrue(hasattr(matrix, "contract_request_administrative"))
        self.assertTrue(hasattr(matrix, "contract_request_legal"))
        self.assertTrue(hasattr(matrix, "contract_request_financial"))
        self.assertTrue(hasattr(matrix, "contract_request_integrity"))
        self.assertTrue(hasattr(matrix, "contract_request_board"))

        # Document analysis activity fields
        self.assertTrue(hasattr(matrix, "document_analysis_requesting_area"))
        self.assertTrue(hasattr(matrix, "document_analysis_administrative"))
        self.assertTrue(hasattr(matrix, "document_analysis_legal"))
        self.assertTrue(hasattr(matrix, "document_analysis_financial"))
        self.assertTrue(hasattr(matrix, "document_analysis_integrity"))
        self.assertTrue(hasattr(matrix, "document_analysis_board"))

        # Risk consultation activity fields
        self.assertTrue(hasattr(matrix, "risk_consultation_requesting_area"))
        self.assertTrue(hasattr(matrix, "risk_consultation_administrative"))
        self.assertTrue(hasattr(matrix, "risk_consultation_legal"))
        self.assertTrue(hasattr(matrix, "risk_consultation_financial"))
        self.assertTrue(hasattr(matrix, "risk_consultation_integrity"))
        self.assertTrue(hasattr(matrix, "risk_consultation_board"))

        # Final approval activity fields
        self.assertTrue(hasattr(matrix, "final_approval_requesting_area"))
        self.assertTrue(hasattr(matrix, "final_approval_administrative"))
        self.assertTrue(hasattr(matrix, "final_approval_legal"))
        self.assertTrue(hasattr(matrix, "final_approval_financial"))
        self.assertTrue(hasattr(matrix, "final_approval_integrity"))
        self.assertTrue(hasattr(matrix, "final_approval_board"))

        # Payment release activity fields
        self.assertTrue(hasattr(matrix, "payment_release_requesting_area"))
        self.assertTrue(hasattr(matrix, "payment_release_administrative"))
        self.assertTrue(hasattr(matrix, "payment_release_legal"))
        self.assertTrue(hasattr(matrix, "payment_release_financial"))
        self.assertTrue(hasattr(matrix, "payment_release_integrity"))
        self.assertTrue(hasattr(matrix, "payment_release_board"))
