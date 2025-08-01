"""
Tests for domain views.
This module contains tests for all domain-related views in the supplier module.
"""

from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from src.supplier.models.domain import DomBusinessSector, DomCategory, DomClassification


class TestDomainListViews(TestCase):
    """Test cases for domain list views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test data
        self.business_sector = baker.make(DomBusinessSector, name="Tecnologia")
        self.category = baker.make(DomCategory, name="Software")
        self.classification = baker.make(DomClassification, name="Fornecedor")

    def test_dom_business_sector_list_view(self):
        """Test DomBusinessSector list view."""
        url = reverse("dom-business-sector-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)  # Now returns a direct list
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Tecnologia")

    def test_dom_category_list_view(self):
        """Test DomCategory list view."""
        url = reverse("dom-category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)  # Now returns a direct list
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Software")

    def test_dom_classification_list_view(self):
        """Test DomClassification list view."""
        url = reverse("dom-classification-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)  # Now returns a direct list
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Fornecedor")

    def test_empty_lists(self):
        """Test that views return empty lists when no data exists."""
        # Clear all data
        DomBusinessSector.objects.all().delete()
        DomCategory.objects.all().delete()
        DomClassification.objects.all().delete()

        views_to_test = [
            "dom-business-sector-list",
            "dom-category-list",
            "dom-classification-list",
        ]

        for view_name in views_to_test:
            with self.subTest(view=view_name):
                url = reverse(view_name)
                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.json()
                self.assertIsInstance(data, list)  # Now returns a direct list
                self.assertEqual(len(data), 0)

    def test_multiple_records(self):
        """Test views with multiple records."""
        # Add more test data
        baker.make(DomBusinessSector, _quantity=3)
        baker.make(DomCategory, _quantity=2)

        # Test business sectors
        url = reverse("dom-business-sector-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 4)  # 1 + 3 new

        # Test categories
        url = reverse("dom-category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 3)  # 1 + 2 new
