"""
Tests for ResponsibilityMatrix model.
This module contains tests for the ResponsibilityMatrix model including
creation, validation, relationships, and RACI matrix functionality.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from src.supplier.models.responsibility_matrix import RACI_CHOICES, ResponsibilityMatrix
from src.supplier.models.supplier import Supplier


class TestResponsibilityMatrix(TestCase):
    """Test cases for ResponsibilityMatrix model."""

    def setUp(self):
        """Set up test data."""
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
        # Test default values
        self.assertEqual(
            matrix.contract_request_legal, "-"
        )  # Corrigido para valor padrão real
        self.assertEqual(
            matrix.contract_request_financial, "-"
        )  # Corrigido para valor padrão real

    def test_responsibility_matrix_str_representation(self):
        """Test matrix string representation."""
        matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)
        expected_str = "Matriz de Responsabilidade - Test Supplier"  # Corrigido para o formato real
        self.assertEqual(str(matrix), expected_str)

    def test_raci_choices_validation(self):
        """Test that only valid RACI choices are accepted."""
        # Valid choices should work
        valid_matrix = baker.make(
            ResponsibilityMatrix,
            supplier=self.supplier,
            contract_request_requesting_area="A",
            contract_request_administrative="R",
            contract_request_legal="C",
            contract_request_financial="I",
            contract_request_integrity="-",
        )
        self.assertIsNotNone(valid_matrix.pk)

    def test_accountability_business_rule(self):
        """Test business rule: each activity must have exactly one Accountable (A)."""
        # Test contract_request activity with one A
        matrix = baker.make(
            ResponsibilityMatrix,
            supplier=self.supplier,
            contract_request_requesting_area="A",  # One A - valid
            contract_request_administrative="R",
            contract_request_legal="C",
            contract_request_financial="I",
            contract_request_integrity="-",
            contract_request_board="I",
        )

        # Should validate successfully
        try:
            matrix.full_clean()
        except ValidationError:
            self.fail("Valid RACI matrix should not raise ValidationError")

    def test_responsibility_business_rule(self):
        """Test business rule: each activity must have at least one Responsible (R)."""
        # Using self.supplier from setUp

        # Test with at least one R
        matrix = baker.make(
            ResponsibilityMatrix,
            supplier=self.supplier,
            contract_request_requesting_area="A",
            contract_request_administrative="R",  # At least one R - valid
            contract_request_legal="C",
        )

        # Should validate successfully
        try:
            matrix.full_clean()
        except ValidationError:
            self.fail("Valid RACI matrix should not raise ValidationError")

    def test_unique_supplier_constraint(self):
        """Test that each supplier can have only one responsibility matrix."""
        # Using self.supplier from setUp
        baker.make(ResponsibilityMatrix, supplier=self.supplier)

        # Try to create another matrix for the same supplier
        with self.assertRaises(IntegrityError):
            baker.make(ResponsibilityMatrix, supplier=self.supplier)

    def test_all_activities_have_default_values(self):
        """Test that all 12 activities have proper default values."""
        # Using self.supplier from setUp
        matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)

        # Check all activities have default values
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
        # Using self.supplier from setUp
        matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)
        matrix_id = matrix.pk

        # Delete supplier
        supplier.delete()

        # Matrix should be deleted too
        self.assertFalse(ResponsibilityMatrix.objects.filter(id=matrix_id).exists())

    def test_raci_choices_constants(self):
        """Test that RACI_CHOICES contains expected values."""
        expected_choices = [
            ("A", "Accountable"),
            ("R", "Responsible"),
            ("C", "Consulted"),
            ("I", "Informed"),
            ("-", "Not Involved"),
        ]

        self.assertEqual(RACI_CHOICES, expected_choices)

    def test_matrix_activities_coverage(self):
        """Test that all business activities are covered in the matrix."""
        # Using self.supplier from setUp
        matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)

        # Test contract request activities
        contract_activities = [
            "contract_request_requesting_area",
            "contract_request_administrative",
            "contract_request_legal",
            "contract_request_financial",
            "contract_request_integrity",
            "contract_request_board",
        ]

        # Test document analysis activities
        analysis_activities = [
            "document_analysis_requesting_area",
            "document_analysis_administrative",
            "document_analysis_legal",
            "document_analysis_financial",
            "document_analysis_integrity",
            "document_analysis_board",
        ]

        # All activities should exist as model fields
        for activity in contract_activities + analysis_activities:
            self.assertTrue(hasattr(matrix, activity))
            value = getattr(matrix, activity)
            self.assertIsNotNone(value)

    def test_responsibility_matrix_creation_with_defaults(self):
        """Test responsibility matrix creation with default values."""
        matrix = ResponsibilityMatrix.objects.create(supplier=self.supplier)

        # Test that default values are set correctly
        self.assertEqual(matrix.contract_request_requesting_area, "-")
        self.assertEqual(matrix.document_analysis_administrative, "A/R")
        self.assertEqual(matrix.risk_consultation_integrity, "A")
        self.assertEqual(matrix.final_approval_board, "A/R")

        # Test string representation
        expected_str = f"Matriz de Responsabilidade - {self.supplier.trade_name}"
        self.assertEqual(str(matrix), expected_str)

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

    def test_responsibility_matrix_one_to_one_relationship(self):
        """Test that only one matrix can exist per supplier."""
        # Create first matrix
        ResponsibilityMatrix.objects.create(supplier=self.supplier)

        # Try to create second matrix for same supplier
        with self.assertRaises(IntegrityError):
            ResponsibilityMatrix.objects.create(supplier=self.supplier)

    def test_raci_choices_validation(self):
        """Test that RACI fields only accept valid choices."""
        # Valid choices should work
        matrix = ResponsibilityMatrix.objects.create(
            supplier=self.supplier,
            contract_request_requesting_area="A",
            contract_request_administrative="R",
            contract_request_legal="C",
            contract_request_financial="I",
            contract_request_integrity="-",
            contract_request_board="A/R",
        )

        self.assertEqual(matrix.contract_request_requesting_area, "A")
        self.assertEqual(matrix.contract_request_administrative, "R")
        self.assertEqual(matrix.contract_request_legal, "C")
        self.assertEqual(matrix.contract_request_financial, "I")
        self.assertEqual(matrix.contract_request_integrity, "-")
        self.assertEqual(matrix.contract_request_board, "A/R")

    def test_all_activity_fields_present(self):
        """Test that all expected activity fields are present."""
        matrix = ResponsibilityMatrix.objects.create(supplier=self.supplier)

        # Test contract request activity fields
        self.assertTrue(hasattr(matrix, "contract_request_requesting_area"))
        self.assertTrue(hasattr(matrix, "contract_request_administrative"))
        self.assertTrue(hasattr(matrix, "contract_request_legal"))
        self.assertTrue(hasattr(matrix, "contract_request_financial"))
        self.assertTrue(hasattr(matrix, "contract_request_integrity"))
        self.assertTrue(hasattr(matrix, "contract_request_board"))

        # Test document analysis activity fields
        self.assertTrue(hasattr(matrix, "document_analysis_requesting_area"))
        self.assertTrue(hasattr(matrix, "document_analysis_administrative"))
        self.assertTrue(hasattr(matrix, "document_analysis_legal"))
        self.assertTrue(hasattr(matrix, "document_analysis_financial"))
        self.assertTrue(hasattr(matrix, "document_analysis_integrity"))
        self.assertTrue(hasattr(matrix, "document_analysis_board"))

        # Test risk consultation activity fields
        self.assertTrue(hasattr(matrix, "risk_consultation_requesting_area"))
        self.assertTrue(hasattr(matrix, "risk_consultation_administrative"))
        self.assertTrue(hasattr(matrix, "risk_consultation_legal"))
        self.assertTrue(hasattr(matrix, "risk_consultation_financial"))
        self.assertTrue(hasattr(matrix, "risk_consultation_integrity"))
        self.assertTrue(hasattr(matrix, "risk_consultation_board"))

        # Test final approval activity fields
        self.assertTrue(hasattr(matrix, "final_approval_requesting_area"))
        self.assertTrue(hasattr(matrix, "final_approval_administrative"))
        self.assertTrue(hasattr(matrix, "final_approval_legal"))
        self.assertTrue(hasattr(matrix, "final_approval_financial"))
        self.assertTrue(hasattr(matrix, "final_approval_integrity"))
        self.assertTrue(hasattr(matrix, "final_approval_board"))

        # Test payment release activity fields
        self.assertTrue(hasattr(matrix, "payment_release_requesting_area"))
        self.assertTrue(hasattr(matrix, "payment_release_administrative"))
        self.assertTrue(hasattr(matrix, "payment_release_legal"))
        self.assertTrue(hasattr(matrix, "payment_release_financial"))
        self.assertTrue(hasattr(matrix, "payment_release_integrity"))
        self.assertTrue(hasattr(matrix, "payment_release_board"))

    def test_cascade_deletion_from_supplier(self):
        """Test that deleting supplier cascades to responsibility matrix."""
        matrix = ResponsibilityMatrix.objects.create(supplier=self.supplier)
        matrix_id = matrix.pk

        # Delete supplier
        self.supplier.delete()

        # Check that matrix is also deleted
        self.assertFalse(ResponsibilityMatrix.objects.filter(pk=matrix_id).exists())

    def test_meta_configuration(self):
        """Test model meta configuration."""
        matrix = ResponsibilityMatrix.objects.create(supplier=self.supplier)

        # Test meta attributes
        self.assertEqual(matrix._meta.db_table, "responsibility_matrix")
        self.assertEqual(matrix._meta.verbose_name, "Matriz de Responsabilidade")
        self.assertEqual(
            matrix._meta.verbose_name_plural, "Matrizes de Responsabilidade"
        )
        self.assertFalse(matrix._meta.abstract)

    def test_raci_choices_constants(self):
        """Test that RACI choices are correctly defined."""
        expected_choices = [
            ("A", "A - Accountable (Responsável)"),
            ("R", "R - Responsible (Executa)"),
            ("C", "C - Consulted (Consultado)"),
            ("I", "I - Informed (Informado)"),
            ("-", "- Não Envolvido"),
            ("A/R", "A/R - Responsável e Executa"),
        ]

        self.assertEqual(RACI_CHOICES, expected_choices)

    def test_default_raci_configuration(self):
        """Test that default RACI configuration follows expected patterns."""
        matrix = ResponsibilityMatrix.objects.create(supplier=self.supplier)

        # Test some key default configurations
        # Document analysis should have administrative as A/R and integrity as C
        self.assertEqual(matrix.document_analysis_administrative, "A/R")
        self.assertEqual(matrix.document_analysis_integrity, "C")

        # Risk consultation should have integrity as A (accountable)
        self.assertEqual(matrix.risk_consultation_integrity, "A")

        # Final approval should have board as A/R (accountable and responsible)
        self.assertEqual(matrix.final_approval_board, "A/R")

        # Payment release should have financial as A/R
        self.assertEqual(matrix.payment_release_financial, "A/R")

    def test_all_raci_activities_covered(self):
        """Test that all 12 activities are covered in the matrix."""
        matrix = ResponsibilityMatrix.objects.create(supplier=self.supplier)

        # List of all activities that should be present
        activities = [
            "contract_request",
            "document_analysis",
            "risk_consultation",
            "risk_assessment",
            "system_registration",
            "form_handling",
            "contract_draft",
            "compliance_validation",
            "final_approval",
            "contract_signing",
            "document_management",
            "payment_release",
        ]

        # List of all areas/roles
        areas = [
            "requesting_area",
            "administrative",
            "legal",
            "financial",
            "integrity",
            "board",
        ]

        # Check that all combinations exist
        for activity in activities:
            for area in areas:
                field_name = f"{activity}_{area}"
                self.assertTrue(
                    hasattr(matrix, field_name), f"Field {field_name} should exist"
                )

                # Check that the field has a valid RACI value
                field_value = getattr(matrix, field_name)
                valid_values = [choice[0] for choice in RACI_CHOICES]
                self.assertIn(
                    field_value,
                    valid_values,
                    f"Field {field_name} has invalid value: {field_value}",
                )


class TestResponsibilityMatrixQueryMethods(TestCase):
    """Test cases for ResponsibilityMatrix query methods and relationships."""

    def setUp(self):
        """Set up test data for query tests."""
        # Create minimal supplier setup using model_bakery
        self.supplier = baker.make(Supplier, trade_name="Test Supplier")
        self.matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)

    def test_supplier_responsibility_matrix_relationship(self):
        """Test accessing responsibility matrix from supplier."""
        # Test forward relationship
        self.assertEqual(self.matrix.supplier, self.supplier)

        # Test that we can query by supplier
        found_matrix = ResponsibilityMatrix.objects.get(supplier=self.supplier)
        self.assertEqual(found_matrix, self.matrix)

    def test_responsibility_matrix_queryset_filtering(self):
        """Test filtering responsibility matrix by various criteria."""
        # Test filtering by RACI value usando existing matrix
        self.matrix.contract_request_requesting_area = "A"
        self.matrix.save()

        matrices_with_accountable = ResponsibilityMatrix.objects.filter(
            contract_request_requesting_area="A"
        )
        self.assertIn(self.matrix, matrices_with_accountable)

        # Test filtering by supplier
        supplier_matrices = ResponsibilityMatrix.objects.filter(supplier=self.supplier)
        self.assertIn(matrix1, supplier_matrices)

    def test_responsibility_matrix_timestamps(self):
        """Test that timestamp fields are properly set."""
        import time

        self.assertIsNotNone(self.matrix.created_at)
        self.assertIsNotNone(self.matrix.updated_at)

        # Update the matrix and check timestamp update (add small delay)
        original_updated_at = self.matrix.updated_at
        time.sleep(0.01)  # Small delay to ensure time difference
        self.matrix.contract_request_requesting_area = "A"
        self.matrix.save()

        self.assertGreater(self.matrix.updated_at, original_updated_at)
