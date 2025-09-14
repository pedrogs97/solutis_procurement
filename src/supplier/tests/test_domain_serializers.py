"""
Tests for supplier domain serializers.
This module contains tests for all domain-related serializers in the supplier module.
"""

from django.test import TestCase
from model_bakery import baker

from src.supplier.models.domain import DomBusinessSector, DomCategory, DomClassification
from src.supplier.serializers.outbound.domain import (
    DomBusinessSectorSerializer,
    DomCategorySerializer,
    DomClassificationSerializer,
)


class TestDomBusinessSectorSerializer(TestCase):
    """Test cases for DomBusinessSectorSerializer."""

    def setUp(self):
        """Set up test data."""
        self.business_sector = baker.make(DomBusinessSector, name="Tecnologia")

    def test_serializer_instantiation(self):
        """Test that serializer can be instantiated."""
        serializer = DomBusinessSectorSerializer(self.business_sector)
        self.assertIsNotNone(serializer)
        self.assertIsNotNone(serializer.data)

    def test_serializer_data_structure(self):
        """Test serializer data structure."""
        serializer = DomBusinessSectorSerializer(self.business_sector)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("name", data)

    def test_baker_prepare_vs_make(self):
        """Test difference between baker.prepare and baker.make."""
        prepared_instance = baker.prepare(DomBusinessSector, name="Test Prepare")
        self.assertIsNone(prepared_instance.pk)

        made_instance = baker.make(DomBusinessSector, name="Test Make")
        self.assertIsNotNone(made_instance.pk)

        serializer = DomBusinessSectorSerializer(made_instance)
        data = serializer.data
        self.assertIn("id", data)

    def test_baker_batch_creation(self):
        """Test creating multiple instances efficiently with model_bakery."""
        sectors = baker.make(DomBusinessSector, _quantity=5)

        self.assertEqual(len(sectors), 5)

        serializer = DomBusinessSectorSerializer(sectors, many=True)
        data = serializer.data

        self.assertEqual(len(data), 5)
        for item in data:
            self.assertIn("id", item)
            self.assertIn("name", item)


class TestDomCategorySerializer(TestCase):
    """Test cases for DomCategorySerializer."""

    def setUp(self):
        """Set up test data."""
        self.category = baker.make(DomCategory, name="Categoria Teste")

    def test_serializer_instantiation(self):
        """Test that serializer can be instantiated."""
        serializer = DomCategorySerializer(self.category)
        self.assertIsNotNone(serializer)
        self.assertIsNotNone(serializer.data)


class TestDomClassificationSerializer(TestCase):
    """Test cases for DomClassificationSerializer."""

    def setUp(self):
        """Set up test data."""
        self.classification = baker.make(DomClassification, name="Fornecedor")

    def test_serializer_instantiation(self):
        """Test that serializer can be instantiated."""
        serializer = DomClassificationSerializer(self.classification)
        self.assertIsNotNone(serializer)
        self.assertIsNotNone(serializer.data)
