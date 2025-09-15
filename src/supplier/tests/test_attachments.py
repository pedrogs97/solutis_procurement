"""
Tests for SupplierAttachment model.
This module contains tests for the SupplierAttachment model including
creation, file handling, relationships, and unique constraints.
"""

from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase

from src.shared.models import Address, Contact
from src.supplier.enums import DomPendecyTypeEnum
from src.supplier.models.attachments import SupplierAttachment
from src.supplier.models.domain import (
    DomAttachmentType,
    DomBusinessSector,
    DomCategory,
    DomClassification,
    DomCompanySize,
    DomCustomerType,
    DomIcmsTaxpayer,
    DomIncomeType,
    DomIssRegime,
    DomIssWithholding,
    DomPayerType,
    DomPaymentMethod,
    DomPendencyType,
    DomPixType,
    DomPublicEntity,
    DomRiskLevel,
    DomSupplierSituation,
    DomTaxationMethod,
    DomTaxationRegime,
    DomTaxpayerClassification,
    DomTypeSupplier,
    DomWithholdingTax,
)
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)


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


class TestSupplierAttachment(TestCase):
    """Test cases for SupplierAttachment model."""

    def setUp(self):
        """Set up test data."""
        self.attachment_type = DomAttachmentType.objects.create(name="Contrato Social")

        address = Address.objects.create(postal_code="01234-567", number="123")
        contact = Contact.objects.create(email="test@example.com", phone="11999999999")

        setup_situation()

        payment_method = DomPaymentMethod.objects.create(name="TED")
        pix_type = DomPixType.objects.create(name="Email")
        payment_details = PaymentDetails.objects.create(
            payment_frequency="Mensal",
            payment_date="2024-01-15",
            contract_total_value=60000.00,
            contract_monthly_value=5000.00,
            checking_account="12345",
            payment_method=payment_method,
            pix_key_type=pix_type,
            pix_key="test@email.com",
        )

        payer_type = DomPayerType.objects.create(name="PJ")
        business_sector = DomBusinessSector.objects.create(name="Technology")
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal"
        )
        public_entity = DomPublicEntity.objects.create(name="RFB")
        organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        iss_withholding = DomIssWithholding.objects.create(name="No")
        iss_regime = DomIssRegime.objects.create(name="Normal")
        withholding_tax = DomWithholdingTax.objects.create(name="IRRF")
        fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        company_size = DomCompanySize.objects.create(name="Small")
        icms_taxpayer = DomIcmsTaxpayer.objects.create(name="No")
        taxation_regime = DomTaxationRegime.objects.create(name="Simple")
        income_type = DomIncomeType.objects.create(name="Services")
        taxation_method = DomTaxationMethod.objects.create(name="Normal")
        customer_type = DomCustomerType.objects.create(name="B2B")
        company_information = CompanyInformation.objects.create(
            company_size=company_size,
            icms_taxpayer=icms_taxpayer,
            taxation_regime=taxation_regime,
            income_type=income_type,
            taxation_method=taxation_method,
            customer_type=customer_type,
        )

        contract = Contract.objects.create(
            object_contract="Test Contract",
            executed_activities="Test activities",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
        )

        classification = DomClassification.objects.create(name="Test")
        category = DomCategory.objects.create(name="Services")
        risk_level = DomRiskLevel.objects.create(name="Low")
        supplier_type = DomTypeSupplier.objects.create(name="Legal")

        self.supplier = Supplier.objects.create(
            trade_name="Test Supplier",
            legal_name="Test Supplier LTDA",
            tax_id="12345678000190",
            state_business_registration="123456789",
            municipal_business_registration="987654321",
            address=address,
            contact=contact,
            payment_details=payment_details,
            organizational_details=organizational_details,
            fiscal_details=fiscal_details,
            company_information=company_information,
            contract=contract,
            classification=classification,
            category=category,
            risk_level=risk_level,
            type=supplier_type,
        )

        self.test_file = SimpleUploadedFile(
            "test_contract.pdf", b"file_content", content_type="application/pdf"
        )

    def test_supplier_attachment_creation(self):
        """Test supplier attachment creation with valid data."""
        attachment = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            file=self.test_file,
            description="Contrato social da empresa teste",
        )

        self.assertEqual(attachment.supplier, self.supplier)
        self.assertEqual(attachment.attachment_type, self.attachment_type)
        self.assertEqual(attachment.description, "Contrato social da empresa teste")
        self.assertIsNotNone(attachment.file)

    def test_file_name_property(self):
        """Test the file_name property returns only the filename."""
        test_file = SimpleUploadedFile(
            "contract_social.pdf", b"file_content", content_type="application/pdf"
        )

        attachment = SupplierAttachment.objects.create(
            supplier=self.supplier, attachment_type=self.attachment_type, file=test_file
        )

        self.assertIsNotNone(attachment.file_name)
        if attachment.file_name:
            self.assertIn("contract_social", attachment.file_name)
            self.assertTrue(attachment.file_name.endswith(".pdf"))

    def test_file_name_property_without_file(self):
        """Test the file_name property when no file is attached."""
        attachment = SupplierAttachment(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            description="Test without file",
        )

        self.assertIsNone(attachment.file_name)

    @patch("src.supplier.models.attachments.SupplierAttachment.file")
    def test_get_file_url_with_file(self, mock_file):
        """Test get_file_url method when file exists."""
        mock_file.url = "/media/test/file.pdf"
        mock_file.__bool__ = lambda x: True

        attachment = SupplierAttachment(
            supplier=self.supplier, attachment_type=self.attachment_type, file=mock_file
        )

        self.assertEqual(attachment.get_file_url(), "/media/test/file.pdf")

    def test_get_file_url_without_file(self):
        """Test get_file_url method when no file exists."""
        attachment = SupplierAttachment(
            supplier=self.supplier, attachment_type=self.attachment_type
        )

        self.assertIsNone(attachment.get_file_url())

    @patch("src.supplier.models.attachments.SupplierAttachment.file")
    def test_storage_path_property(self, mock_file):
        """Test storage_path property."""
        mock_file.path = "/full/path/to/file.pdf"
        mock_file.__bool__ = lambda x: True

        attachment = SupplierAttachment(
            supplier=self.supplier, attachment_type=self.attachment_type, file=mock_file
        )

        self.assertEqual(attachment.storage_path, "/full/path/to/file.pdf")

    def test_storage_path_property_without_file(self):
        """Test storage_path property when no file exists."""
        attachment = SupplierAttachment(
            supplier=self.supplier, attachment_type=self.attachment_type
        )

        self.assertIsNone(attachment.storage_path)

    def test_unique_together_constraint(self):
        """Test that unique_together constraint is enforced."""
        SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            file=self.test_file,
            description="First attachment",
        )

        test_file_2 = SimpleUploadedFile(
            "test_contract_2.pdf", b"different_content", content_type="application/pdf"
        )

        with self.assertRaises(IntegrityError):
            SupplierAttachment.objects.create(
                supplier=self.supplier,
                attachment_type=self.attachment_type,
                file=test_file_2,
                description="Second attachment",
            )

    def test_different_attachment_types_allowed(self):
        """Test that same supplier can have multiple attachments of different types."""
        attachment_type_2 = DomAttachmentType.objects.create(name="CNPJ")

        attachment_1 = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            file=self.test_file,
            description="First attachment",
        )

        test_file_2 = SimpleUploadedFile(
            "cnpj.pdf", b"cnpj_content", content_type="application/pdf"
        )

        attachment_2 = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=attachment_type_2,
            file=test_file_2,
            description="Second attachment",
        )

        self.assertTrue(SupplierAttachment.objects.filter(pk=attachment_1.pk).exists())
        self.assertTrue(SupplierAttachment.objects.filter(pk=attachment_2.pk).exists())

    def test_cascade_deletion_from_supplier(self):
        """Test that deleting supplier cascades to attachments."""
        attachment = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            file=self.test_file,
            description="Test attachment",
        )

        attachment_id = attachment.pk

        self.supplier.delete()

        self.assertFalse(SupplierAttachment.objects.filter(pk=attachment_id).exists())

    def test_do_nothing_deletion_from_attachment_type(self):
        """Test that deleting attachment type doesn't delete attachments."""
        attachment = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            file=self.test_file,
            description="Test attachment",
        )

        attachment_id = attachment.pk

        with self.assertRaises(Exception):
            self.attachment_type.delete()

        self.assertTrue(SupplierAttachment.objects.filter(pk=attachment_id).exists())

    def test_attachment_relationships(self):
        """Test attachment model relationships."""
        attachment = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            file=self.test_file,
            description="Relationship test",
        )

        self.assertEqual(attachment.supplier, self.supplier)
        self.assertEqual(attachment.attachment_type, self.attachment_type)

        supplier_attachments = SupplierAttachment.objects.filter(supplier=self.supplier)
        self.assertIn(attachment, supplier_attachments)

        type_attachments = SupplierAttachment.objects.filter(
            attachment_type=self.attachment_type
        )
        self.assertIn(attachment, type_attachments)


class TestSupplierAttachmentQueryMethods(TestCase):
    """Test cases for SupplierAttachment query methods and filtering."""

    def setUp(self):
        """Set up test data for query tests."""
        self.contract_type = DomAttachmentType.objects.create(name="Contrato Social")
        self.cnpj_type = DomAttachmentType.objects.create(name="CNPJ")

        setup_situation()

        address = Address.objects.create(postal_code="01234-567", number="123")
        contact = Contact.objects.create(email="test@example.com", phone="11999999999")

        payment_method = DomPaymentMethod.objects.create(name="TED")
        pix_type = DomPixType.objects.create(name="Email")
        payment_details = PaymentDetails.objects.create(
            payment_frequency="Mensal",
            payment_date="2024-01-15",
            contract_total_value=60000.00,
            contract_monthly_value=5000.00,
            checking_account="12345",
            payment_method=payment_method,
            pix_key_type=pix_type,
            pix_key="test@email.com",
        )

        payer_type = DomPayerType.objects.create(name="PJ")
        business_sector = DomBusinessSector.objects.create(name="Tech")
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal"
        )
        public_entity = DomPublicEntity.objects.create(name="RFB")
        organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        iss_withholding = DomIssWithholding.objects.create(name="No")
        iss_regime = DomIssRegime.objects.create(name="Normal")
        withholding_tax = DomWithholdingTax.objects.create(name="IRRF")
        fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        company_size = DomCompanySize.objects.create(name="Small")
        icms_taxpayer = DomIcmsTaxpayer.objects.create(name="No")
        taxation_regime = DomTaxationRegime.objects.create(name="Simple")
        income_type = DomIncomeType.objects.create(name="Services")
        taxation_method = DomTaxationMethod.objects.create(name="Normal")
        customer_type = DomCustomerType.objects.create(name="B2B")
        company_information = CompanyInformation.objects.create(
            company_size=company_size,
            icms_taxpayer=icms_taxpayer,
            taxation_regime=taxation_regime,
            income_type=income_type,
            taxation_method=taxation_method,
            customer_type=customer_type,
        )

        contract = Contract.objects.create(
            object_contract="Test Contract",
            executed_activities="Test activities",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
        )

        classification = DomClassification.objects.create(name="Test")
        category = DomCategory.objects.create(name="Services")
        risk_level = DomRiskLevel.objects.create(name="Low")
        supplier_type = DomTypeSupplier.objects.create(name="Legal")
        self.supplier = Supplier.objects.create(
            trade_name="Test Supplier",
            legal_name="Test Supplier LTDA",
            tax_id="12345678000190",
            state_business_registration="123456789",
            municipal_business_registration="987654321",
            address=address,
            contact=contact,
            payment_details=payment_details,
            organizational_details=organizational_details,
            fiscal_details=fiscal_details,
            company_information=company_information,
            contract=contract,
            classification=classification,
            category=category,
            risk_level=risk_level,
            type=supplier_type,
        )

    def test_filter_by_attachment_type(self):
        """Test filtering attachments by type."""
        contract_file = SimpleUploadedFile(
            "contract.pdf", b"contract_content", content_type="application/pdf"
        )
        cnpj_file = SimpleUploadedFile(
            "cnpj.pdf", b"cnpj_content", content_type="application/pdf"
        )

        contract_attachment = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.contract_type,
            file=contract_file,
        )
        cnpj_attachment = SupplierAttachment.objects.create(
            supplier=self.supplier, attachment_type=self.cnpj_type, file=cnpj_file
        )

        contract_attachments = SupplierAttachment.objects.filter(
            attachment_type=self.contract_type
        )
        self.assertIn(contract_attachment, contract_attachments)
        self.assertNotIn(cnpj_attachment, contract_attachments)

        cnpj_attachments = SupplierAttachment.objects.filter(
            attachment_type=self.cnpj_type
        )
        self.assertIn(cnpj_attachment, cnpj_attachments)
        self.assertNotIn(contract_attachment, cnpj_attachments)

    def test_filter_by_supplier(self):
        """Test filtering attachments by supplier."""
        test_file = SimpleUploadedFile(
            "test.pdf", b"content", content_type="application/pdf"
        )

        attachment = SupplierAttachment.objects.create(
            supplier=self.supplier, attachment_type=self.contract_type, file=test_file
        )

        supplier_attachments = SupplierAttachment.objects.filter(supplier=self.supplier)
        self.assertIn(attachment, supplier_attachments)

    def test_count_attachments_by_type(self):
        """Test counting attachments by type."""
        test_file_1 = SimpleUploadedFile(
            "test1.pdf", b"content1", content_type="application/pdf"
        )

        SupplierAttachment.objects.create(
            supplier=self.supplier, attachment_type=self.contract_type, file=test_file_1
        )

        contract_count = SupplierAttachment.objects.filter(
            attachment_type=self.contract_type
        ).count()
        self.assertEqual(contract_count, 1)

        cnpj_count = SupplierAttachment.objects.filter(
            attachment_type=self.cnpj_type
        ).count()
        self.assertEqual(cnpj_count, 0)
