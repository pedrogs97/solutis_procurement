"""
Tests for shared models.
This module contains tests for Address, Contact and TimestampedModel.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from src.shared.models import Address, Contact


class TestTimestampedModel(TestCase):
    """
    Test cases for TimestampedModel functionality.
    Since it's abstract, we test through Address and Contact models.
    """

    def test_created_at_auto_now_add(self):
        """Test that created_at is automatically set on creation."""
        before_creation = timezone.now()
        address = Address.objects.create(
            street="Rua Teste",
            city="São Paulo",
            state="SP",
            number=123,
            postal_code="01234567",
        )
        after_creation = timezone.now()

        self.assertIsNotNone(address.created_at)
        self.assertGreaterEqual(address.created_at, before_creation)
        self.assertLessEqual(address.created_at, after_creation)

    def test_updated_at_auto_now(self):
        """Test that updated_at is automatically updated on save."""
        address = Address.objects.create(
            street="Rua Teste",
            city="São Paulo",
            state="SP",
            number=123,
            postal_code="01234567",
        )
        original_updated_at = address.updated_at

        # Wait a moment and update
        import time

        time.sleep(0.01)

        address.street = "Rua Atualizada"
        address.save()

        self.assertGreater(address.updated_at, original_updated_at)


class TestAddressModel(TestCase):
    """Test cases for Address model."""

    def setUp(self):
        """Set up test data."""
        self.valid_address_data = {
            "street": "Rua das Flores, 123",
            "city": "São Paulo",
            "state": "SP",
            "neighbourhood": "Centro",
            "number": 123,
            "postal_code": "01234567",
            "complement": "Apto 45",
        }

    def test_create_address_with_all_fields(self):
        """Test creating an address with all fields."""
        address = Address.objects.create(**self.valid_address_data)

        self.assertEqual(address.street, "Rua das Flores, 123")
        self.assertEqual(address.city, "São Paulo")
        self.assertEqual(address.state, "SP")
        self.assertEqual(address.neighbourhood, "Centro")
        self.assertEqual(address.number, 123)
        self.assertEqual(address.postal_code, "01234567")
        self.assertEqual(address.complement, "Apto 45")
        self.assertIsNotNone(address.created_at)
        self.assertIsNotNone(address.updated_at)

    def test_create_address_minimal_fields(self):
        """Test creating an address with only required fields."""
        minimal_data = {
            "street": "Rua Teste",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "number": 456,
            "postal_code": "12345678",
        }

        address = Address.objects.create(**minimal_data)

        self.assertEqual(address.street, "Rua Teste")
        self.assertEqual(address.city, "Rio de Janeiro")
        self.assertEqual(address.state, "RJ")
        self.assertEqual(address.number, 456)
        self.assertEqual(address.postal_code, "12345678")
        self.assertEqual(address.neighbourhood, "")  # Should be empty
        self.assertEqual(address.complement, "")  # Should be empty

    def test_address_str_representation(self):
        """Test the string representation of Address."""
        address = Address.objects.create(**self.valid_address_data)
        expected_str = "Rua das Flores, 123, São Paulo/SP - 01234567"

        self.assertEqual(str(address), expected_str)

    def test_address_meta_options(self):
        """Test Address model meta options."""
        self.assertEqual(Address._meta.db_table, "address")
        self.assertEqual(Address._meta.verbose_name, "Endereço")
        self.assertEqual(Address._meta.verbose_name_plural, "Endereços")

    def test_address_field_max_lengths(self):
        """Test field maximum lengths."""
        # Test street max_length
        long_street = "x" * 256  # Exceeds max_length of 255
        with self.assertRaises(ValidationError):
            address = Address(
                street=long_street,
                city="São Paulo",
                state="SP",
                number=123,
                postal_code="01234567",
            )
            address.full_clean()

    def test_postal_code_length(self):
        """Test postal code field length."""
        # Test valid 8-digit postal code
        address = Address.objects.create(
            street="Rua Teste",
            city="São Paulo",
            state="SP",
            number=123,
            postal_code="01234567",
        )
        self.assertEqual(len(address.postal_code), 8)


class TestContactModel(TestCase):
    """Test cases for Contact model."""

    def setUp(self):
        """Set up test data."""
        self.valid_contact_data = {"email": "teste@exemplo.com", "phone": "11999999999"}

    def test_create_contact_with_all_fields(self):
        """Test creating a contact with all fields."""
        contact = Contact.objects.create(**self.valid_contact_data)

        self.assertEqual(contact.email, "teste@exemplo.com")
        self.assertEqual(contact.phone, "11999999999")
        self.assertIsNotNone(contact.created_at)
        self.assertIsNotNone(contact.updated_at)

    def test_create_contact_email_only(self):
        """Test creating a contact with email only."""
        contact = Contact.objects.create(email="email@teste.com")

        self.assertEqual(contact.email, "email@teste.com")
        self.assertEqual(contact.phone, "")

    def test_create_contact_phone_only(self):
        """Test creating a contact with phone only."""
        contact = Contact.objects.create(phone="11888888888")

        self.assertEqual(contact.phone, "11888888888")
        self.assertEqual(contact.email, "")

    def test_create_empty_contact(self):
        """Test creating a contact with no data."""
        contact = Contact.objects.create()

        self.assertEqual(contact.email, "")
        self.assertEqual(contact.phone, "")

    def test_contact_str_representation(self):
        """Test the string representation of Contact."""
        contact = Contact.objects.create(**self.valid_contact_data)
        expected_str = "teste@exemplo.com / 11999999999"

        self.assertEqual(str(contact), expected_str)

    def test_email_allows_duplicates(self):
        """Test that email field allows duplicates (unique constraint removed for supplier updates)."""
        # Create first contact
        contact1 = Contact.objects.create(
            email="duplicado@teste.com", phone="11111111111"
        )

        # Create second contact with same email - should not raise error
        contact2 = Contact.objects.create(
            email="duplicado@teste.com", phone="11222222222"
        )

        self.assertEqual(contact1.email, contact2.email)
        self.assertNotEqual(contact1.pk, contact2.pk)

    def test_email_blank_allowed(self):
        """Test that blank email is allowed."""
        contact1 = Contact.objects.create(phone="11111111111")
        contact2 = Contact.objects.create(phone="11222222222")

        self.assertEqual(contact1.email, "")
        self.assertEqual(contact2.email, "")

    def test_contact_meta_options(self):
        """Test Contact model meta options."""
        self.assertEqual(Contact._meta.db_table, "contact")
        self.assertEqual(Contact._meta.verbose_name, "Contato")
        self.assertEqual(Contact._meta.verbose_name_plural, "Contatos")

    def test_phone_max_length(self):
        """Test phone field maximum length."""
        long_phone = "1" * 12  # Exceeds max_length of 11
        with self.assertRaises(ValidationError):
            contact = Contact(email="teste@teste.com", phone=long_phone)
            contact.full_clean()

    def test_email_field_validation(self):
        """Test email field validation."""
        # Test invalid email format
        with self.assertRaises(ValidationError):
            contact = Contact(email="email-invalido", phone="11999999999")
            contact.full_clean()

    def test_duplicate_empty_emails_allowed(self):
        """Test that multiple contacts with empty email are allowed."""
        contact1 = Contact.objects.create(email="", phone="11111111111")
        contact2 = Contact.objects.create(email="", phone="11222222222")

        self.assertEqual(contact1.email, "")
        self.assertEqual(contact2.email, "")
        self.assertNotEqual(contact1.pk, contact2.pk)
