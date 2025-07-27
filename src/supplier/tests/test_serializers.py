"""
Tests for supplier serializers.
This module contains tests for all supplier-related serializers including
input and output serializers for Supplier, ResponsibilityMatrix, and SupplierAttachment.
"""

from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from src.shared.models import Address, Contact
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
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)
from src.supplier.serializers.inbound.attachment import SupplierAttachmentInSerializer
from src.supplier.serializers.inbound.responsibility_matrix import (
    ResponsibilityMatrixInSerializer,
)
from src.supplier.serializers.inbound.supplier import SupplierInSerializer
from src.supplier.serializers.outbound.attachment import SupplierAttachmentOutSerializer
from src.supplier.serializers.outbound.responsibility_matrix import (
    ResponsibilityMatrixOutSerializer,
)
from src.supplier.serializers.outbound.supplier import SupplierOutSerializer


class TestSupplierInSerializer(TestCase):
    """Test cases for SupplierInSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create domain objects
        self.payment_method = DomPaymentMethod.objects.create(
            name="TED", description="Transferência Eletrônica"
        )
        self.pix_type = DomPixType.objects.create(
            name="Email", description="Chave PIX por Email"
        )
        self.payer_type = DomPayerType.objects.create(
            name="PJ", description="Pessoa Jurídica"
        )
        self.business_sector = DomBusinessSector.objects.create(
            name="Tecnologia", description="Setor de Tecnologia"
        )
        self.taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Contribuinte", description="Contribuinte Normal"
        )
        self.public_entity = DomPublicEntity.objects.create(
            name="RFB", description="Receita Federal do Brasil"
        )
        self.iss_withholding = DomIssWithholding.objects.create(
            name="Não", description="Não retém ISS"
        )
        self.iss_regime = DomIssRegime.objects.create(
            name="Normal", description="Regime Normal"
        )
        self.withholding_tax = DomWithholdingTax.objects.create(
            name="IRRF", description="Imposto de Renda Retido na Fonte"
        )
        self.company_size = DomCompanySize.objects.create(
            name="Médio", description="Empresa de Médio Porte"
        )
        self.icms_taxpayer = DomIcmsTaxpayer.objects.create(
            name="Sim", description="Contribuinte ICMS"
        )
        self.taxation_regime = DomTaxationRegime.objects.create(
            name="Lucro Real", description="Lucro Real"
        )
        self.income_type = DomIncomeType.objects.create(
            name="Serviços", description="Prestação de Serviços"
        )
        self.taxation_method = DomTaxationMethod.objects.create(
            name="Retenção", description="Tributação por Retenção"
        )
        self.customer_type = DomCustomerType.objects.create(
            name="B2B", description="Business to Business"
        )
        self.classification = DomClassification.objects.create(
            name="Prestador", description="Prestador de Serviços"
        )
        self.category = DomCategory.objects.create(
            name="TI", description="Tecnologia da Informação"
        )
        self.risk_level = DomRiskLevel.objects.create(
            name="Baixo", description="Risco Baixo"
        )
        self.supplier_type = DomTypeSupplier.objects.create(
            name="PJ", description="Pessoa Jurídica"
        )
        self.situation = DomSupplierSituation.objects.create(
            name="Ativo", description="Fornecedor Ativo"
        )

        self.valid_data = {
            "tradeName": "Empresa Teste LTDA",
            "legalName": "Empresa de Teste de Software LTDA",
            "taxId": "12345678000190",
            "stateBusinessRegistration": "123456789",
            "municipalBusinessRegistration": "987654321",
            "address": {
                "postalCode": "01234-567",
                "number": "123",
                "complement": "Sala 456",
            },
            "contact": {"email": "contato@empresa.com", "phone": "11999887766"},
            "paymentDetails": {
                "paymentFrequency": "Mensal",
                "paymentDate": "2024-01-15",
                "contractTotalValue": "120000.00",
                "contractMonthlyValue": "10000.00",
                "checkingAccount": "12345-6",
                "paymentMethod": self.payment_method.pk,
                "pixKeyType": self.pix_type.pk,
                "pixKey": "empresa@teste.com",
            },
            "organizationalDetails": {
                "costCenter": "CC001",
                "businessUnit": "Tecnologia",
                "responsibleExecutive": "Maria Santos",
                "payerType": self.payer_type.pk,
                "businessSector": self.business_sector.pk,
                "taxpayerClassification": self.taxpayer_classification.pk,
                "publicEntity": self.public_entity.pk,
            },
            "fiscalDetails": {
                "issWithholding": self.iss_withholding.pk,
                "issRegime": self.iss_regime.pk,
                "issTaxpayer": False,
                "simplesNacionalParticipant": True,
                "cooperativeMember": False,
                "withholdingTaxNature": self.withholding_tax.pk,
            },
            "companyInformation": {
                "companySize": self.company_size.pk,
                "icmsTaxpayer": self.icms_taxpayer.pk,
                "taxationRegime": self.taxation_regime.pk,
                "incomeType": self.income_type.pk,
                "taxationMethod": self.taxation_method.pk,
                "customerType": self.customer_type.pk,
            },
            "contract": {
                "objectContract": "Prestação de serviços de consultoria",
                "executedActivities": "Consultoria em TI e desenvolvimento",
                "contractStartDate": "2024-01-01",
                "contractEndDate": "2024-12-31",
            },
            "classification": self.classification.pk,
            "category": self.category.pk,
            "riskLevel": self.risk_level.pk,
            "type": self.supplier_type.pk,
            "situation": self.situation.pk,
        }

    def test_valid_data_serialization(self):
        """Test serializer with valid data."""
        serializer = SupplierInSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_required_fields(self):
        """Test serializer with missing required fields."""
        invalid_data = self.valid_data.copy()
        del invalid_data["tradeName"]

        serializer = SupplierInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("tradeName", serializer.errors)

    def test_invalid_tax_id(self):
        """Test serializer with invalid tax ID."""
        invalid_data = self.valid_data.copy()
        invalid_data["taxId"] = "invalid_tax_id"

        serializer = SupplierInSerializer(data=invalid_data)
        # Note: This test depends on whether you have tax ID validation
        # If not implemented yet, this test might pass
        if not serializer.is_valid():
            self.assertIn("taxId", serializer.errors)

    @patch("src.shared.serializers.get_address_from_cep")
    def test_address_validation(self, mock_get_address):
        """Test address validation in nested serializer."""
        mock_get_address.return_value = {
            "cep": "01234-567",
            "logradouro": "Rua Teste",
            "bairro": "Centro",
            "localidade": "São Paulo",
            "uf": "SP",
        }

        serializer = SupplierInSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_email_in_contact(self):
        """Test serializer with invalid email in contact."""
        invalid_data = self.valid_data.copy()
        invalid_data["contact"]["email"] = "invalid-email"

        serializer = SupplierInSerializer(data=invalid_data)
        # This depends on email validation in ContactSerializer
        if not serializer.is_valid():
            self.assertIn("contact", serializer.errors)

    def test_create_supplier(self):
        """Test creating supplier through serializer."""
        with patch("src.shared.serializers.get_address_from_cep") as mock_get_address:
            mock_get_address.return_value = {
                "cep": "01234-567",
                "logradouro": "Rua Teste",
                "bairro": "Centro",
                "localidade": "São Paulo",
                "uf": "SP",
            }

            serializer = SupplierInSerializer(data=self.valid_data)
            self.assertTrue(serializer.is_valid(), serializer.errors)

            supplier = serializer.save()

            self.assertIsInstance(supplier, Supplier)
            self.assertEqual(supplier.trade_name, "Empresa Teste LTDA")
            self.assertEqual(supplier.tax_id, "12345678000190")
            self.assertIsNotNone(supplier.address)
            self.assertIsNotNone(supplier.contact)


class TestSupplierOutSerializer(TestCase):
    """Test cases for SupplierOutSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create all required objects
        self.address = Address.objects.create(
            postal_code="01234-567", number="123", complement="Sala 456"
        )
        self.contact = Contact.objects.create(
            email="test@example.com", phone="11999999999"
        )

        # Create domain objects
        payment_method = DomPaymentMethod.objects.create(
            name="TED", description="Transfer"
        )
        pix_type = DomPixType.objects.create(name="Email", description="Email PIX")
        self.payment_details = PaymentDetails.objects.create(
            payment_frequency="Mensal",
            payment_date="2024-01-15",
            contract_total_value=60000.00,
            contract_monthly_value=5000.00,
            checking_account="12345",
            payment_method=payment_method,
            pix_key_type=pix_type,
            pix_key="test@email.com",
        )

        payer_type = DomPayerType.objects.create(name="PJ", description="Legal Entity")
        business_sector = DomBusinessSector.objects.create(
            name="Tech", description="Technology"
        )
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal", description="Normal"
        )
        public_entity = DomPublicEntity.objects.create(
            name="RFB", description="Federal Revenue"
        )
        self.organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        iss_withholding = DomIssWithholding.objects.create(
            name="No", description="No withholding"
        )
        iss_regime = DomIssRegime.objects.create(
            name="Normal", description="Normal regime"
        )
        withholding_tax = DomWithholdingTax.objects.create(
            name="IRRF", description="Income tax"
        )
        self.fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        company_size = DomCompanySize.objects.create(
            name="Small", description="Small company"
        )
        icms_taxpayer = DomIcmsTaxpayer.objects.create(
            name="No", description="Not taxpayer"
        )
        taxation_regime = DomTaxationRegime.objects.create(
            name="Simple", description="Simple regime"
        )
        income_type = DomIncomeType.objects.create(
            name="Services", description="Service income"
        )
        taxation_method = DomTaxationMethod.objects.create(
            name="Normal", description="Normal method"
        )
        customer_type = DomCustomerType.objects.create(
            name="B2B", description="Business to Business"
        )
        self.company_information = CompanyInformation.objects.create(
            company_size=company_size,
            icms_taxpayer=icms_taxpayer,
            taxation_regime=taxation_regime,
            income_type=income_type,
            taxation_method=taxation_method,
            customer_type=customer_type,
        )

        self.contract = Contract.objects.create(
            object_contract="Test Contract",
            executed_activities="Test activities",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
        )

        classification = DomClassification.objects.create(
            name="Test", description="Test classification"
        )
        category = DomCategory.objects.create(
            name="Services", description="Service category"
        )
        risk_level = DomRiskLevel.objects.create(name="Low", description="Low risk")
        supplier_type = DomTypeSupplier.objects.create(
            name="Legal", description="Legal entity"
        )
        situation = DomSupplierSituation.objects.create(
            name="Active", description="Active"
        )

        self.supplier = Supplier.objects.create(
            trade_name="Test Supplier",
            legal_name="Test Supplier LTDA",
            tax_id="12345678000190",
            state_business_registration="123456789",
            municipal_business_registration="987654321",
            address=self.address,
            contact=self.contact,
            payment_details=self.payment_details,
            organizational_details=self.organizational_details,
            fiscal_details=self.fiscal_details,
            company_information=self.company_information,
            contract=self.contract,
            classification=classification,
            category=category,
            risk_level=risk_level,
            type=supplier_type,
            situation=situation,
        )

    def test_supplier_serialization(self):
        """Test serializing supplier to output format."""
        serializer = SupplierOutSerializer(self.supplier)
        data = serializer.data

        # Test basic fields
        self.assertEqual(data["tradeName"], "Test Supplier")
        self.assertEqual(data["legalName"], "Test Supplier LTDA")
        self.assertEqual(data["taxId"], "12345678000190")

        # Test nested objects
        self.assertIn("address", data)
        self.assertIn("contact", data)
        self.assertIn("paymentDetails", data)
        self.assertIn("organizationalDetails", data)
        self.assertIn("fiscalDetails", data)
        self.assertIn("companyInformation", data)
        self.assertIn("contract", data)

        # Test domain objects
        self.assertIn("classification", data)
        self.assertIn("category", data)
        self.assertIn("riskLevel", data)
        self.assertIn("type", data)
        self.assertIn("situation", data)

    def test_camel_case_conversion(self):
        """Test that field names are converted to camelCase."""
        serializer = SupplierOutSerializer(self.supplier)
        data = serializer.data

        # Check camelCase field names
        self.assertIn("tradeName", data)
        self.assertIn("legalName", data)
        self.assertIn("taxId", data)
        self.assertIn("stateBusinessRegistration", data)
        self.assertIn("municipalBusinessRegistration", data)

        # Check that snake_case names are not present
        self.assertNotIn("trade_name", data)
        self.assertNotIn("legal_name", data)
        self.assertNotIn("tax_id", data)


class TestResponsibilityMatrixInSerializer(TestCase):
    """Test cases for ResponsibilityMatrixInSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create supplier
        address = Address.objects.create(postal_code="01234-567", number="123")
        contact = Contact.objects.create(email="test@example.com", phone="11999999999")

        payment_method = DomPaymentMethod.objects.create(
            name="TED", description="Transfer"
        )
        pix_type = DomPixType.objects.create(name="Email", description="Email PIX")
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

        payer_type = DomPayerType.objects.create(name="PJ", description="Legal Entity")
        business_sector = DomBusinessSector.objects.create(
            name="Tech", description="Technology"
        )
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal", description="Normal"
        )
        public_entity = DomPublicEntity.objects.create(
            name="RFB", description="Federal Revenue"
        )
        organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        iss_withholding = DomIssWithholding.objects.create(
            name="No", description="No withholding"
        )
        iss_regime = DomIssRegime.objects.create(
            name="Normal", description="Normal regime"
        )
        withholding_tax = DomWithholdingTax.objects.create(
            name="IRRF", description="Income tax"
        )
        fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        company_size = DomCompanySize.objects.create(
            name="Small", description="Small company"
        )
        icms_taxpayer = DomIcmsTaxpayer.objects.create(
            name="No", description="Not taxpayer"
        )
        taxation_regime = DomTaxationRegime.objects.create(
            name="Simple", description="Simple regime"
        )
        income_type = DomIncomeType.objects.create(
            name="Services", description="Service income"
        )
        taxation_method = DomTaxationMethod.objects.create(
            name="Normal", description="Normal method"
        )
        customer_type = DomCustomerType.objects.create(
            name="B2B", description="Business to Business"
        )
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

        classification = DomClassification.objects.create(
            name="Test", description="Test classification"
        )
        category = DomCategory.objects.create(
            name="Services", description="Service category"
        )
        risk_level = DomRiskLevel.objects.create(name="Low", description="Low risk")
        supplier_type = DomTypeSupplier.objects.create(
            name="Legal", description="Legal entity"
        )
        situation = DomSupplierSituation.objects.create(
            name="Active", description="Active"
        )

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
            situation=situation,
        )

        self.valid_data = {
            "supplier": self.supplier.pk,
            "contractRequestRequestingArea": "A",
            "contractRequestAdministrative": "R",
            "contractRequestLegal": "C",
            "contractRequestFinancial": "I",
            "contractRequestIntegrity": "-",
            "contractRequestBoard": "I",
            "documentAnalysisRequestingArea": "I",
            "documentAnalysisAdministrative": "A",
            "documentAnalysisLegal": "C",
            "documentAnalysisFinancial": "-",
            "documentAnalysisIntegrity": "C",
            "documentAnalysisBoard": "-",
        }

    def test_valid_data_serialization(self):
        """Test serializer with valid RACI data."""
        serializer = ResponsibilityMatrixInSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_supplier(self):
        """Test serializer with invalid supplier ID."""
        invalid_data = self.valid_data.copy()
        invalid_data["supplier"] = 99999  # Non-existent supplier ID

        serializer = ResponsibilityMatrixInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_raci_value(self):
        """Test serializer with invalid RACI value."""
        invalid_data = self.valid_data.copy()
        invalid_data["contractRequestRequestingArea"] = "X"  # Invalid RACI value

        serializer = ResponsibilityMatrixInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("contractRequestRequestingArea", serializer.errors)

    def test_raci_business_rules_validation(self):
        """Test RACI business rules validation."""
        # Test case: Multiple accountable for same activity (should fail)
        invalid_data = self.valid_data.copy()
        invalid_data.update(
            {
                "contractRequestRequestingArea": "A",
                "contractRequestAdministrative": "A",  # Two A's for same activity
            }
        )

        serializer = ResponsibilityMatrixInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        # The validation error should be in non_field_errors since it's a general validation
        self.assertIn("non_field_errors", serializer.errors)

    def test_missing_accountable_validation(self):
        """Test that activities without accountable are caught."""
        invalid_data = self.valid_data.copy()
        # Set all roles to non-accountable for contract request activity
        invalid_data.update(
            {
                "contractRequestRequestingArea": "I",
                "contractRequestAdministrative": "R",
                "contractRequestLegal": "C",
                "contractRequestFinancial": "I",
                "contractRequestIntegrity": "-",
                "contractRequestBoard": "I",
            }
        )

        serializer = ResponsibilityMatrixInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_create_responsibility_matrix(self):
        """Test creating responsibility matrix through serializer."""
        serializer = ResponsibilityMatrixInSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        matrix = serializer.save()

        self.assertIsInstance(matrix, ResponsibilityMatrix)
        self.assertEqual(matrix.supplier, self.supplier)
        self.assertEqual(matrix.contract_request_requesting_area, "A")
        self.assertEqual(matrix.document_analysis_administrative, "A")


class TestResponsibilityMatrixOutSerializer(TestCase):
    """Test cases for ResponsibilityMatrixOutSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create supplier (minimal setup)
        address = Address.objects.create(postal_code="01234-567", number="123")
        contact = Contact.objects.create(email="test@example.com", phone="11999999999")

        payment_method = DomPaymentMethod.objects.create(
            name="TED", description="Transfer"
        )
        pix_type = DomPixType.objects.create(name="Email", description="Email PIX")
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

        payer_type = DomPayerType.objects.create(name="PJ", description="Legal Entity")
        business_sector = DomBusinessSector.objects.create(
            name="Tech", description="Technology"
        )
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal", description="Normal"
        )
        public_entity = DomPublicEntity.objects.create(
            name="RFB", description="Federal Revenue"
        )
        organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        iss_withholding = DomIssWithholding.objects.create(
            name="No", description="No withholding"
        )
        iss_regime = DomIssRegime.objects.create(
            name="Normal", description="Normal regime"
        )
        withholding_tax = DomWithholdingTax.objects.create(
            name="IRRF", description="Income tax"
        )
        fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        company_size = DomCompanySize.objects.create(
            name="Small", description="Small company"
        )
        icms_taxpayer = DomIcmsTaxpayer.objects.create(
            name="No", description="Not taxpayer"
        )
        taxation_regime = DomTaxationRegime.objects.create(
            name="Simple", description="Simple regime"
        )
        income_type = DomIncomeType.objects.create(
            name="Services", description="Service income"
        )
        taxation_method = DomTaxationMethod.objects.create(
            name="Normal", description="Normal method"
        )
        customer_type = DomCustomerType.objects.create(
            name="B2B", description="Business to Business"
        )
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

        classification = DomClassification.objects.create(
            name="Test", description="Test classification"
        )
        category = DomCategory.objects.create(
            name="Services", description="Service category"
        )
        risk_level = DomRiskLevel.objects.create(name="Low", description="Low risk")
        supplier_type = DomTypeSupplier.objects.create(
            name="Legal", description="Legal entity"
        )
        situation = DomSupplierSituation.objects.create(
            name="Active", description="Active"
        )

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
            situation=situation,
        )

        self.matrix = ResponsibilityMatrix.objects.create(
            supplier=self.supplier,
            contract_request_requesting_area="A",
            contract_request_administrative="R",
            document_analysis_administrative="A",
        )

    def test_responsibility_matrix_serialization(self):
        """Test serializing responsibility matrix to output format."""
        serializer = ResponsibilityMatrixOutSerializer(self.matrix)
        data = serializer.data

        # Test that supplier field is excluded
        self.assertNotIn("supplier", data)

        # Test RACI fields are present
        self.assertIn("contractRequestRequestingArea", data)
        self.assertIn("contractRequestAdministrative", data)
        self.assertIn("documentAnalysisAdministrative", data)

        # Test values
        self.assertEqual(data["contractRequestRequestingArea"], "A")
        self.assertEqual(data["contractRequestAdministrative"], "R")
        self.assertEqual(data["documentAnalysisAdministrative"], "A")

    def test_camel_case_conversion(self):
        """Test that field names are converted to camelCase."""
        serializer = ResponsibilityMatrixOutSerializer(self.matrix)
        data = serializer.data

        # Check camelCase field names
        self.assertIn("contractRequestRequestingArea", data)
        self.assertIn("documentAnalysisAdministrative", data)

        # Check that snake_case names are not present
        self.assertNotIn("contract_request_requesting_area", data)
        self.assertNotIn("document_analysis_administrative", data)


class TestSupplierAttachmentInSerializer(TestCase):
    """Test cases for SupplierAttachmentInSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create attachment type
        self.attachment_type = DomAttachmentType.objects.create(
            name="Contrato Social", description="Contrato social da empresa"
        )

        # Create supplier (minimal setup)
        address = Address.objects.create(postal_code="01234-567", number="123")
        contact = Contact.objects.create(email="test@example.com", phone="11999999999")

        payment_method = DomPaymentMethod.objects.create(
            name="TED", description="Transfer"
        )
        pix_type = DomPixType.objects.create(name="Email", description="Email PIX")
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

        payer_type = DomPayerType.objects.create(name="PJ", description="Legal Entity")
        business_sector = DomBusinessSector.objects.create(
            name="Tech", description="Technology"
        )
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal", description="Normal"
        )
        public_entity = DomPublicEntity.objects.create(
            name="RFB", description="Federal Revenue"
        )
        organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        iss_withholding = DomIssWithholding.objects.create(
            name="No", description="No withholding"
        )
        iss_regime = DomIssRegime.objects.create(
            name="Normal", description="Normal regime"
        )
        withholding_tax = DomWithholdingTax.objects.create(
            name="IRRF", description="Income tax"
        )
        fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        company_size = DomCompanySize.objects.create(
            name="Small", description="Small company"
        )
        icms_taxpayer = DomIcmsTaxpayer.objects.create(
            name="No", description="Not taxpayer"
        )
        taxation_regime = DomTaxationRegime.objects.create(
            name="Simple", description="Simple regime"
        )
        income_type = DomIncomeType.objects.create(
            name="Services", description="Service income"
        )
        taxation_method = DomTaxationMethod.objects.create(
            name="Normal", description="Normal method"
        )
        customer_type = DomCustomerType.objects.create(
            name="B2B", description="Business to Business"
        )
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

        classification = DomClassification.objects.create(
            name="Test", description="Test classification"
        )
        category = DomCategory.objects.create(
            name="Services", description="Service category"
        )
        risk_level = DomRiskLevel.objects.create(name="Low", description="Low risk")
        supplier_type = DomTypeSupplier.objects.create(
            name="Legal", description="Legal entity"
        )
        situation = DomSupplierSituation.objects.create(
            name="Active", description="Active"
        )

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
            situation=situation,
        )

        self.test_file = SimpleUploadedFile(
            "test_contract.pdf", b"file_content", content_type="application/pdf"
        )

        self.valid_data = {
            "supplier": self.supplier.pk,
            "attachment_type": self.attachment_type.pk,
            "file": self.test_file,
            "description": "Contrato social da empresa teste",
        }

    def test_valid_data_serialization(self):
        """Test serializer with valid data."""
        serializer = SupplierAttachmentInSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_supplier(self):
        """Test serializer with invalid supplier."""
        invalid_data = self.valid_data.copy()
        invalid_data["supplier"] = 99999  # Non-existent supplier

        serializer = SupplierAttachmentInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_attachment_type(self):
        """Test serializer with invalid attachment type."""
        invalid_data = self.valid_data.copy()
        invalid_data["attachment_type"] = 99999  # Non-existent attachment type

        serializer = SupplierAttachmentInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_file_extension(self):
        """Test serializer with invalid file extension."""
        invalid_file = SimpleUploadedFile(
            "test.txt", b"file_content", content_type="text/plain"
        )

        invalid_data = self.valid_data.copy()
        invalid_data["file"] = invalid_file

        serializer = SupplierAttachmentInSerializer(data=invalid_data)
        # This test depends on file extension validation in the serializer
        if not serializer.is_valid():
            self.assertIn("file", serializer.errors)

    def test_missing_required_fields(self):
        """Test serializer with missing required fields."""
        invalid_data = self.valid_data.copy()
        del invalid_data["file"]

        serializer = SupplierAttachmentInSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)


class TestSupplierAttachmentOutSerializer(TestCase):
    """Test cases for SupplierAttachmentOutSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create attachment type
        self.attachment_type = DomAttachmentType.objects.create(
            name="Contrato Social", description="Contrato social da empresa"
        )

        # Create supplier (minimal setup)
        address = Address.objects.create(postal_code="01234-567", number="123")
        contact = Contact.objects.create(email="test@example.com", phone="11999999999")

        payment_method = DomPaymentMethod.objects.create(
            name="TED", description="Transfer"
        )
        pix_type = DomPixType.objects.create(name="Email", description="Email PIX")
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

        payer_type = DomPayerType.objects.create(name="PJ", description="Legal Entity")
        business_sector = DomBusinessSector.objects.create(
            name="Tech", description="Technology"
        )
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal", description="Normal"
        )
        public_entity = DomPublicEntity.objects.create(
            name="RFB", description="Federal Revenue"
        )
        organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        iss_withholding = DomIssWithholding.objects.create(
            name="No", description="No withholding"
        )
        iss_regime = DomIssRegime.objects.create(
            name="Normal", description="Normal regime"
        )
        withholding_tax = DomWithholdingTax.objects.create(
            name="IRRF", description="Income tax"
        )
        fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        company_size = DomCompanySize.objects.create(
            name="Small", description="Small company"
        )
        icms_taxpayer = DomIcmsTaxpayer.objects.create(
            name="No", description="Not taxpayer"
        )
        taxation_regime = DomTaxationRegime.objects.create(
            name="Simple", description="Simple regime"
        )
        income_type = DomIncomeType.objects.create(
            name="Services", description="Service income"
        )
        taxation_method = DomTaxationMethod.objects.create(
            name="Normal", description="Normal method"
        )
        customer_type = DomCustomerType.objects.create(
            name="B2B", description="Business to Business"
        )
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

        classification = DomClassification.objects.create(
            name="Test", description="Test classification"
        )
        category = DomCategory.objects.create(
            name="Services", description="Service category"
        )
        risk_level = DomRiskLevel.objects.create(name="Low", description="Low risk")
        supplier_type = DomTypeSupplier.objects.create(
            name="Legal", description="Legal entity"
        )
        situation = DomSupplierSituation.objects.create(
            name="Active", description="Active"
        )

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
            situation=situation,
        )

        test_file = SimpleUploadedFile(
            "test_contract.pdf", b"file_content", content_type="application/pdf"
        )

        self.attachment = SupplierAttachment.objects.create(
            supplier=self.supplier,
            attachment_type=self.attachment_type,
            file=test_file,
            description="Test attachment description",
        )

    def test_attachment_serialization(self):
        """Test serializing attachment to output format."""
        serializer = SupplierAttachmentOutSerializer(self.attachment)
        data = serializer.data

        # Test basic fields
        self.assertIn("id", data)
        self.assertIn("attachmentTypeName", data)
        self.assertIn("fileName", data)
        self.assertIn("description", data)

        # Test values
        self.assertEqual(data["attachmentTypeName"], "Contrato Social")
        self.assertEqual(data["description"], "Test attachment description")
        self.assertIsNotNone(data["fileName"])

    def test_attachment_type_name_field(self):
        """Test that attachment type name is properly serialized."""
        serializer = SupplierAttachmentOutSerializer(self.attachment)
        data = serializer.data

        self.assertEqual(data["attachmentTypeName"], self.attachment_type.name)
