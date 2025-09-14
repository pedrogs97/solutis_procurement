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

        self.business_sector = baker.make(DomBusinessSector, name="Tecnologia")
        self.category = baker.make(DomCategory, name="Software")
        self.classification = baker.make(DomClassification, name="Fornecedor")

    def test_dom_business_sector_list_view(self):
        """Test DomBusinessSector list view."""
        url = reverse("dom-business-sector-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Tecnologia")

    def test_dom_category_list_view(self):
        """Test DomCategory list view."""
        url = reverse("dom-category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Software")

    def test_dom_classification_list_view(self):
        """Test DomClassification list view."""
        url = reverse("dom-classification-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Fornecedor")

    def test_empty_lists(self):
        """Test that views return empty lists when no data exists."""
        DomBusinessSector.objects.all().delete()
        DomCategory.objects.all().delete()
        DomClassification.objects.all().delete()

        views_to_test = [
            "dom-business-sector-list",
            "dom-category-list",
            "dom-classification-list",
            "dom-risk-level-list",
            "dom-supplier-type-list",
            "dom-payment-method-list",
            "dom-company-size-list",
            "dom-taxation-regime-list",
        ]

        for view_name in views_to_test:
            with self.subTest(view=view_name):
                url = reverse(view_name)
                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.json()
                self.assertIsInstance(data, list)
                self.assertEqual(len(data), 0)

    def test_multiple_records(self):
        """Test views with multiple records."""
        baker.make(DomBusinessSector, _quantity=3)
        baker.make(DomCategory, _quantity=2)

        url = reverse("dom-business-sector-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 4)

        url = reverse("dom-category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 3)

    def test_all_domain_endpoints(self):
        """Test all domain endpoints exist and return valid responses."""

        domain_endpoints = [
            "dom-business-sector-list",
            "dom-category-list",
            "dom-classification-list",
            "dom-risk-level-list",
            "dom-supplier-type-list",
            "dom-supplier-situation-list",
            "dom-pix-type-list",
            "dom-payment-method-list",
            "dom-payer-type-list",
            "dom-taxpayer-classification-list",
            "dom-public-entity-list",
            "dom-iss-withholding-list",
            "dom-iss-regime-list",
            "dom-withholding-tax-list",
            "dom-company-size-list",
            "dom-icms-taxpayer-list",
            "dom-income-type-list",
            "dom-taxation-method-list",
            "dom-customer-type-list",
            "dom-taxation-regime-list",
        ]

        for endpoint in domain_endpoints:
            with self.subTest(endpoint=endpoint):
                url = reverse(endpoint)
                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.json()
                self.assertIsInstance(data, list)

    def test_ordered_results(self):
        """Test that results are ordered by name."""
        baker.make(DomBusinessSector, name="Zebra")
        baker.make(DomBusinessSector, name="Alpha")
        baker.make(DomBusinessSector, name="Beta")

        url = reverse("dom-business-sector-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        names = [item["name"] for item in data]
        self.assertEqual(names, ["Alpha", "Beta", "Tecnologia", "Zebra"])

    def test_serialization_format(self):
        """Test that serialized data has correct format."""
        baker.make(DomBusinessSector, name="Test Sector")

        url = reverse("dom-business-sector-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertGreater(len(data), 0)

        item = data[0]
        self.assertIn("id", item)
        self.assertIn("name", item)
        self.assertIsInstance(item["id"], int)
        self.assertIsInstance(item["name"], str)

    def test_baker_integration_with_views(self):
        """Test that model_bakery works correctly with domain views."""
        baker.make(DomBusinessSector, _quantity=3)
        baker.make(DomCategory, _quantity=2)
        baker.make(DomClassification, _quantity=1)

        url = reverse("dom-business-sector-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data), 4)

        url = reverse("dom-category-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data), 3)

        url = reverse("dom-classification-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data), 2)
