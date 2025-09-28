"""
Tests for shared serializers.
This module contains tests for BaseSerializer, AddressSerializer, and ContactSerializer.
"""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import serializers

from src.shared.models import Address, Contact
from src.shared.serializers import AddressSerializer, BaseSerializer, ContactSerializer


class TestBaseSerializer(TestCase):
    """Test cases for BaseSerializer."""

    def test_meta_fields_all(self):
        """Test that BaseSerializer.Meta has fields set to '__all__'."""
        self.assertEqual(BaseSerializer.Meta.fields, "__all__")

    def test_meta_read_only_fields(self):
        """Test that BaseSerializer.Meta has correct read_only_fields."""
        expected_fields = ("id", "created_at", "updated_at")
        self.assertEqual(BaseSerializer.Meta.read_only_fields, expected_fields)

    def test_inheritance_includes_mixin(self):
        """Test that BaseSerializer inherits from the camelCase mixin."""
        from src.shared.mixins import SerializerCamelCaseRepresentationMixin

        self.assertTrue(
            issubclass(BaseSerializer, SerializerCamelCaseRepresentationMixin)
        )
        self.assertTrue(issubclass(BaseSerializer, serializers.ModelSerializer))


class TestAddressSerializer(TestCase):
    """Test cases for AddressSerializer."""

    def setUp(self):
        """Set up test data."""
        self.valid_address_data = {
            "postal_code": "01310100",  # CEP válido de São Paulo
            "number": 123,
            "complement": "Apto 45",
        }

    def test_inheritance_from_base_serializer(self):
        """Test that AddressSerializer inherits from BaseSerializer."""
        self.assertTrue(issubclass(AddressSerializer, BaseSerializer))

    def test_meta_model(self):
        """Test that Meta.model is set to Address."""
        self.assertEqual(AddressSerializer.Meta.model, Address)

    def test_meta_fields(self):
        """Test that Meta.fields contains expected fields."""
        expected_fields = ["id", "postal_code", "number", "complement"]
        self.assertEqual(AddressSerializer.Meta.fields, expected_fields)

    def test_meta_read_only_fields(self):
        """Test that Meta.read_only_fields contains id."""
        self.assertEqual(AddressSerializer.Meta.read_only_fields, ("id",))

    @patch("src.shared.serializers.get_address_from_cep")
    def test_validate_with_valid_postal_code(self, mock_get_address):
        """Test validation with valid postal code."""
        mock_get_address.return_value = {
            "street": "Avenida Paulista",
            "district": "Bela Vista",
            "city": "São Paulo",
            "uf": "SP",
        }

        serializer = AddressSerializer(data=self.valid_address_data)
        self.assertTrue(serializer.is_valid())

        self.assertIn("street", serializer.validated_data)
        self.assertIn("neighbourhood", serializer.validated_data)
        self.assertIn("city", serializer.validated_data)
        self.assertIn("state", serializer.validated_data)

    @patch("src.shared.serializers.get_address_from_cep")
    def test_validate_with_invalid_postal_code_format(self, mock_get_address):
        """Test validation with invalid postal code format."""
        from brazilcep.exceptions import InvalidCEP

        mock_get_address.side_effect = InvalidCEP("Invalid CEP format")

        invalid_data = self.valid_address_data.copy()
        invalid_data["postal_code"] = "invalid"

        serializer = AddressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("field", serializer.errors)

    @patch("src.shared.serializers.get_address_from_cep")
    def test_validate_with_postal_code_not_found(self, mock_get_address):
        """Test validation with postal code not found."""
        from brazilcep.exceptions import CEPNotFound

        mock_get_address.side_effect = CEPNotFound("CEP not found")

        invalid_data = self.valid_address_data.copy()
        invalid_data["postal_code"] = "99999999"

        serializer = AddressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("field", serializer.errors)

    @patch("src.shared.serializers.get_address_from_cep")
    def test_validate_with_connection_error(self, mock_get_address):
        """Test validation when all CEP services fail."""
        from brazilcep.exceptions import BrazilCEPException, ConnectionError

        mock_get_address.side_effect = [
            ConnectionError("Service 1 failed"),
            BrazilCEPException("Service 2 failed"),
            ConnectionError("Service 3 failed"),
        ]

        serializer = AddressSerializer(data=self.valid_address_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("field", serializer.errors)

    def test_create_address(self):
        """Test creating an address through serializer."""
        with patch("src.shared.serializers.get_address_from_cep") as mock_get_address:
            mock_get_address.return_value = {
                "street": "Rua Teste",
                "district": "Centro",
                "city": "São Paulo",
                "uf": "SP",
            }

            serializer = AddressSerializer(data=self.valid_address_data)
            self.assertTrue(serializer.is_valid())

            address = serializer.save()
            self.assertIsInstance(address, Address)
            self.assertEqual(address.postal_code, "01310100")
            self.assertEqual(address.number, 123)
            self.assertEqual(address.complement, "Apto 45")
            self.assertEqual(address.street, "Rua Teste")


class TestContactSerializer(TestCase):
    """Test cases for ContactSerializer."""

    def setUp(self):
        """Set up test data."""
        self.valid_contact_data = {"email": "teste@exemplo.com", "phone": "11999999999"}

    def test_inheritance_from_base_serializer(self):
        """Test that ContactSerializer inherits from BaseSerializer."""
        self.assertTrue(issubclass(ContactSerializer, BaseSerializer))

    def test_meta_model(self):
        """Test that Meta.model is set to Contact."""
        self.assertEqual(ContactSerializer.Meta.model, Contact)

    def test_meta_fields(self):
        """Test that Meta.fields contains expected fields."""
        expected_fields = ["id", "email", "phone"]
        self.assertEqual(ContactSerializer.Meta.fields, expected_fields)

    def test_meta_read_only_fields(self):
        """Test that Meta.read_only_fields contains id."""
        self.assertEqual(ContactSerializer.Meta.read_only_fields, ("id",))

    def test_validate_with_valid_data(self):
        """Test validation with valid contact data."""
        serializer = ContactSerializer(data=self.valid_contact_data)
        self.assertTrue(serializer.is_valid())

        self.assertIsNotNone(serializer.validated_data)

    def test_validate_with_empty_email(self):
        """Test validation with empty email."""
        data = {"phone": "11999999999"}
        serializer = ContactSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_with_empty_phone(self):
        """Test validation with empty phone."""
        data = {"email": "teste@exemplo.com"}
        serializer = ContactSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_email_unique_constraint_new_contact(self):
        """Test email unique validation for new contact."""
        Contact.objects.create(email="existente@exemplo.com")

        data = {"email": "existente@exemplo.com", "phone": "11888888888"}
        serializer = ContactSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_validate_email_same_instance_update(self):
        """Test email validation when updating with same email."""
        contact = Contact.objects.create(email="teste@exemplo.com", phone="11999999999")

        data = {"email": "teste@exemplo.com", "phone": "11888888888"}
        serializer = ContactSerializer(instance=contact, data=data, partial=True)

        self.assertTrue(serializer.is_valid())

    def test_validate_email_different_instance_update(self):
        """Test email validation when updating with existing email from another contact."""
        Contact.objects.create(email="contato1@exemplo.com", phone="11111111111")
        contact2 = Contact.objects.create(
            email="contato2@exemplo.com", phone="11222222222"
        )

        data = {"email": "contato1@exemplo.com"}
        serializer = ContactSerializer(instance=contact2, data=data, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    @patch("rest_framework.serializers.EmailField.run_validation")
    def test_validate_with_invalid_email_format(self, mock_email_validation):
        """Test validation with invalid email format."""
        mock_email_validation.side_effect = serializers.ValidationError("Invalid email")

        data = {"email": "email-invalido", "phone": "11999999999"}
        serializer = ContactSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_create_contact(self):
        """Test creating a contact through serializer."""
        serializer = ContactSerializer(data=self.valid_contact_data)
        self.assertTrue(serializer.is_valid())

        contact = serializer.save()
        self.assertIsInstance(contact, Contact)

    def test_update_contact(self):
        """Test updating a contact through serializer."""
        contact = Contact.objects.create(
            email="original@exemplo.com", phone="11999999999"
        )

        update_data = {"phone": "11888888888"}
        serializer = ContactSerializer(instance=contact, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_contact = serializer.save()
        self.assertIsInstance(updated_contact, Contact)
