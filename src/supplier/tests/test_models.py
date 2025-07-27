"""
Tests for supplier models.
This module contains tests for all supplier-related models including Supplier, PaymentDetails,
OrganizationalDetails, FiscalDetails, CompanyInformation, and Contract models.
"""

from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from src.shared.models import Address, Contact
from src.supplier.models.domain import (
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
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)


class TestContract(TestCase):
    """Test cases for Contract model."""

    def test_contract_creation(self):
        """Test contract creation with valid data."""
        contract = baker.make(
            Contract,
            object_contract="Prestação de serviços de consultoria",
            executed_activities="Consultoria em TI e desenvolvimento de software",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
        )
        self.assertEqual(
            contract.object_contract, "Prestação de serviços de consultoria"
        )
        self.assertEqual(
            contract.executed_activities,
            "Consultoria em TI e desenvolvimento de software",
        )
        self.assertIsNotNone(contract.created_at)
        self.assertIsNotNone(contract.updated_at)

    def test_contract_str_representation(self):
        """Test contract string representation."""
        contract = baker.make(
            Contract,
            object_contract="Prestação de serviços de consultoria",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
        )
        expected_str = (
            "Contrato: Prestação de serviços de consultoria - 2024-01-01 a 2024-12-31"
        )
        self.assertEqual(str(contract), expected_str)

    def test_contract_required_fields(self):
        """Test that required fields are enforced."""
        with self.assertRaises(IntegrityError):
            Contract.objects.create()


class TestPaymentDetails(TestCase):
    """Test cases for PaymentDetails model."""

    def test_payment_details_creation(self):
        """Test payment details creation with valid data."""
        payment_method = baker.make(
            DomPaymentMethod,
            name="Transferência Bancária",
        )
        pix_type = baker.make(DomPixType, name="E-mail")

        payment = baker.make(
            PaymentDetails,
            payment_frequency="Mensal",
            payment_date="2024-01-10",
            contract_total_value=60000.00,
            contract_monthly_value=5000.00,
            checking_account="12345-6",
            payment_method=payment_method,
            pix_key_type=pix_type,
            pix_key="joao@email.com",
        )

        self.assertEqual(payment.payment_frequency, "Mensal")
        self.assertEqual(payment.contract_total_value, 60000.00)
        self.assertEqual(payment.payment_method, payment_method)

    def test_payment_details_str_representation(self):
        """Test payment details string representation."""
        payment = baker.make(
            PaymentDetails,
            payment_frequency="Mensal",
            payment_date="2024-01-10",
        )
        expected_str = "Pagamento: Mensal - 2024-01-10"
        self.assertEqual(str(payment), expected_str)


class TestOrganizationalDetails(TestCase):
    """Test cases for OrganizationalDetails model."""

    def test_organizational_details_creation(self):
        """Test organizational details creation with valid data."""
        payer_type = baker.make(DomPayerType, name="Pessoa Jurídica")
        business_sector = baker.make(DomBusinessSector, name="Tecnologia")
        taxpayer_classification = baker.make(
            DomTaxpayerClassification,
            name="Contribuinte",
        )
        public_entity = baker.make(
            DomPublicEntity,
            name="CNPJ",
        )

        org = baker.make(
            OrganizationalDetails,
            cost_center="CC001",
            business_unit="Tecnologia",
            responsible_executive="Maria Santos",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        self.assertEqual(org.cost_center, "CC001")
        self.assertEqual(org.responsible_executive, "Maria Santos")
        self.assertEqual(org.payer_type, payer_type)

    def test_organizational_details_str_representation(self):
        """Test organizational details string representation."""
        org = baker.make(
            OrganizationalDetails,
            cost_center="CC001",
            business_unit="Tecnologia",
        )
        expected_str = "Organizacional: CC001 - Tecnologia"
        self.assertEqual(str(org), expected_str)


class TestFiscalDetails(TestCase):
    """Test cases for FiscalDetails model."""

    def test_fiscal_details_creation(self):
        """Test fiscal details creation with valid data."""
        iss_withholding = baker.make(DomIssWithholding, name="Sim")
        iss_regime = baker.make(DomIssRegime, name="Normal")
        withholding_tax = baker.make(
            DomWithholdingTax,
            name="IRRF",
        )

        fiscal = baker.make(
            FiscalDetails,
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=True,
            simples_nacional_participant=False,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
        )

        self.assertEqual(fiscal.iss_withholding, iss_withholding)
        self.assertTrue(fiscal.iss_taxpayer)
        self.assertFalse(fiscal.simples_nacional_participant)

    def test_fiscal_details_str_representation(self):
        """Test fiscal details string representation."""
        iss_withholding = baker.make(DomIssWithholding, name="Sim")
        fiscal = baker.make(
            FiscalDetails,
            iss_withholding=iss_withholding,
            simples_nacional_participant=False,
        )
        expected_str = "Fiscal: ISS Sim - Simples Nacional False"
        self.assertEqual(str(fiscal), expected_str)


class TestCompanyInformation(TestCase):
    """Test cases for CompanyInformation model."""

    def test_company_information_creation(self):
        """Test company information creation with valid data."""
        company_size = baker.make(DomCompanySize, name="Médio Porte")
        icms_taxpayer = baker.make(DomIcmsTaxpayer, name="Sim")
        customer_type = baker.make(DomCustomerType, name="B2B")

        company = baker.make(
            CompanyInformation,
            company_size=company_size,
            icms_taxpayer=icms_taxpayer,
            customer_type=customer_type,
        )
        self.assertEqual(company.company_size, company_size)
        self.assertEqual(company.icms_taxpayer, icms_taxpayer)
        self.assertEqual(company.customer_type, customer_type)

    def test_company_information_str_representation(self):
        """Test company information string representation."""
        company_size = baker.make(DomCompanySize, name="Médio Porte")
        icms_taxpayer = baker.make(DomIcmsTaxpayer, name="Sim")

        company = baker.make(
            CompanyInformation,
            company_size=company_size,
            icms_taxpayer=icms_taxpayer,
        )
        expected_str = "Empresa: Médio Porte - ICMS Sim"
        self.assertEqual(str(company), expected_str)


class TestSupplier(TestCase):
    """Test cases for Supplier model."""

    def setUp(self):
        """Set up test data."""
        # Create all required related objects
        self.address = Address.objects.create(
            postal_code="01234-567", number="123", complement="Sala 456"
        )

        self.contact = Contact.objects.create(
            email="supplier@test.com", phone="11999887766"
        )

        self.payment_method = DomPaymentMethod.objects.create(name="TED")
        self.pix_type = DomPixType.objects.create(name="CPF")
        self.payment_details = PaymentDetails.objects.create(
            payment_frequency="Mensal",
            payment_date="2024-01-15",
            contract_total_value=120000.00,
            contract_monthly_value=10000.00,
            checking_account="12345-6",
            payment_method=self.payment_method,
            pix_key_type=self.pix_type,
            pix_key="12345678901",
        )

        self.payer_type = DomPayerType.objects.create(name="PJ")
        self.business_sector = DomBusinessSector.objects.create(name="Serviços")
        self.taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal"
        )
        self.public_entity = DomPublicEntity.objects.create(name="RFB")
        self.organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC100",
            business_unit="Serviços Gerais",
            responsible_executive="Ana Costa",
            payer_type=self.payer_type,
            business_sector=self.business_sector,
            taxpayer_classification=self.taxpayer_classification,
            public_entity=self.public_entity,
        )

        self.iss_withholding = DomIssWithholding.objects.create(name="Não")
        self.iss_regime = DomIssRegime.objects.create(name="Normal")
        self.withholding_tax = DomWithholdingTax.objects.create(name="Nenhum")
        self.fiscal_details = FiscalDetails.objects.create(
            iss_withholding=self.iss_withholding,
            iss_regime=self.iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=self.withholding_tax,
        )

        self.company_size = DomCompanySize.objects.create(name="Pequeno")
        self.icms_taxpayer = DomIcmsTaxpayer.objects.create(name="Não")
        self.taxation_regime = DomTaxationRegime.objects.create(name="Simples")
        self.income_type = DomIncomeType.objects.create(name="Serviços")
        self.taxation_method = DomTaxationMethod.objects.create(name="Normal")
        self.customer_type = DomCustomerType.objects.create(name="PF")
        self.company_information = CompanyInformation.objects.create(
            company_size=self.company_size,
            icms_taxpayer=self.icms_taxpayer,
            taxation_regime=self.taxation_regime,
            income_type=self.income_type,
            taxation_method=self.taxation_method,
            customer_type=self.customer_type,
        )

        self.contract = Contract.objects.create(
            object_contract="Prestação de serviços diversos",
            executed_activities="Desenvolvimento de software e consultoria",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
        )

        # Domain objects for Supplier
        self.classification = DomClassification.objects.create(name="Prestador")
        self.category = DomCategory.objects.create(name="Serviços Gerais")
        self.risk_level = DomRiskLevel.objects.create(name="Baixo")
        self.supplier_type = DomTypeSupplier.objects.create(name="Pessoa Jurídica")
        self.situation = DomSupplierSituation.objects.create(name="Ativo")

        self.supplier_data = {
            "trade_name": "Empresa Teste Ltda",
            "legal_name": "Empresa de Teste de Software Ltda",
            "tax_id": "12345678000190",
            "state_business_registration": "123456789",
            "municipal_business_registration": "987654321",
            "address": self.address,
            "contact": self.contact,
            "payment_details": self.payment_details,
            "organizational_details": self.organizational_details,
            "fiscal_details": self.fiscal_details,
            "company_information": self.company_information,
            "contract": self.contract,
            "classification": self.classification,
            "category": self.category,
            "risk_level": self.risk_level,
            "type": self.supplier_type,
            "situation": self.situation,
        }

    def test_supplier_creation(self):
        """Test supplier creation with valid data."""
        supplier = Supplier.objects.create(**self.supplier_data)
        self.assertEqual(supplier.trade_name, "Empresa Teste Ltda")
        self.assertEqual(supplier.tax_id, "12345678000190")
        self.assertEqual(supplier.classification, self.classification)
        self.assertIsNotNone(supplier.created_at)

    def test_supplier_str_representation(self):
        """Test supplier string representation."""
        supplier = Supplier.objects.create(**self.supplier_data)
        self.assertEqual(str(supplier), "Empresa Teste Ltda")

    def test_supplier_unique_constraints(self):
        """Test that unique constraints are enforced."""
        Supplier.objects.create(**self.supplier_data)

        # Try to create another supplier with same legal_name
        with self.assertRaises(IntegrityError):
            duplicate_data = self.supplier_data.copy()
            duplicate_data["trade_name"] = "Outro Nome"
            duplicate_data["tax_id"] = "98765432000111"
            Supplier.objects.create(**duplicate_data)

    def test_supplier_tax_id_unique(self):
        """Test that tax_id must be unique."""
        Supplier.objects.create(**self.supplier_data)

        # Create new required objects for second supplier
        address2 = Address.objects.create(
            postal_code="12345-678", number="456", complement="Andar 2"
        )
        contact2 = Contact.objects.create(
            email="supplier2@test.com", phone="11888776655"
        )
        payment_details2 = PaymentDetails.objects.create(
            payment_frequency="Quinzenal",
            payment_date="2024-01-30",
            contract_total_value=180000.00,
            contract_monthly_value=15000.00,
            checking_account="98765-4",
            payment_method=self.payment_method,
            pix_key_type=self.pix_type,
            pix_key="98765432100",
        )
        organizational_details2 = OrganizationalDetails.objects.create(
            cost_center="CC200",
            business_unit="Outro Setor",
            responsible_executive="Carlos Silva",
            payer_type=self.payer_type,
            business_sector=self.business_sector,
            taxpayer_classification=self.taxpayer_classification,
            public_entity=self.public_entity,
        )
        fiscal_details2 = FiscalDetails.objects.create(
            iss_withholding=self.iss_withholding,
            iss_regime=self.iss_regime,
            iss_taxpayer=True,
            simples_nacional_participant=False,
            cooperative_member=True,
            withholding_tax_nature=self.withholding_tax,
        )
        company_information2 = CompanyInformation.objects.create(
            company_size=self.company_size,
            icms_taxpayer=self.icms_taxpayer,
            taxation_regime=self.taxation_regime,
            income_type=self.income_type,
            taxation_method=self.taxation_method,
            customer_type=self.customer_type,
        )
        contract2 = Contract.objects.create(
            object_contract="Outros serviços",
            executed_activities="Outros tipos de atividades",
            contract_start_date="2024-02-01",
            contract_end_date="2024-12-31",
        )

        # Try to create supplier with same tax_id
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                trade_name="Segundo Fornecedor",
                legal_name="Segunda Empresa Ltda",
                tax_id="12345678000190",  # Same tax_id
                state_business_registration="987654321",
                municipal_business_registration="123456789",
                address=address2,
                contact=contact2,
                payment_details=payment_details2,
                organizational_details=organizational_details2,
                fiscal_details=fiscal_details2,
                company_information=company_information2,
                contract=contract2,
                classification=self.classification,
                category=self.category,
                risk_level=self.risk_level,
                type=self.supplier_type,
                situation=self.situation,
            )


class TestSupplierRelationships(TestCase):
    """Test cases for Supplier model relationships."""

    def setUp(self):
        """Set up test data for relationship tests."""
        # Create minimal required objects
        self.address = Address.objects.create(postal_code="01234-567", number="123")
        self.contact = Contact.objects.create(
            email="test@example.com", phone="11999999999"
        )

        # Create domain objects
        payment_method = DomPaymentMethod.objects.create(name="TED")
        pix_type = DomPixType.objects.create(name="Email")
        payer_type = DomPayerType.objects.create(name="PJ")
        business_sector = DomBusinessSector.objects.create(name="Tecnologia")
        taxpayer_classification = DomTaxpayerClassification.objects.create(
            name="Normal"
        )
        public_entity = DomPublicEntity.objects.create(name="RFB")
        iss_withholding = DomIssWithholding.objects.create(name="Não")
        iss_regime = DomIssRegime.objects.create(name="Normal")
        withholding_tax = DomWithholdingTax.objects.create(name="IRRF")
        company_size = DomCompanySize.objects.create(name="Pequeno")
        icms_taxpayer = DomIcmsTaxpayer.objects.create(name="Não")
        taxation_regime = DomTaxationRegime.objects.create(name="Simples")
        income_type = DomIncomeType.objects.create(name="Serviços")
        taxation_method = DomTaxationMethod.objects.create(name="Normal")
        customer_type = DomCustomerType.objects.create(name="B2B")

        # Create related objects
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

        self.organizational_details = OrganizationalDetails.objects.create(
            cost_center="CC001",
            business_unit="TI",
            responsible_executive="João",
            payer_type=payer_type,
            business_sector=business_sector,
            taxpayer_classification=taxpayer_classification,
            public_entity=public_entity,
        )

        self.fiscal_details = FiscalDetails.objects.create(
            iss_withholding=iss_withholding,
            iss_regime=iss_regime,
            iss_taxpayer=False,
            simples_nacional_participant=True,
            cooperative_member=False,
            withholding_tax_nature=withholding_tax,
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
            object_contract="Teste",
            executed_activities="Atividades de teste",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
        )

        # Create domain objects for supplier
        self.classification = DomClassification.objects.create(name="Teste")
        self.category = DomCategory.objects.create(name="Serviços")
        self.risk_level = DomRiskLevel.objects.create(name="Baixo")
        self.supplier_type = DomTypeSupplier.objects.create(name="PJ")
        self.situation = DomSupplierSituation.objects.create(name="Ativo")

    def test_supplier_cascade_deletion(self):
        """Test that deleting a supplier cascades to related objects."""
        supplier = Supplier.objects.create(
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
            classification=self.classification,
            category=self.category,
            risk_level=self.risk_level,
            type=self.supplier_type,
            situation=self.situation,
        )

        supplier_id = supplier.pk
        address_id = self.address.pk
        contact_id = self.contact.pk

        # Delete the supplier
        supplier.delete()

        # Check that supplier is deleted
        self.assertFalse(Supplier.objects.filter(pk=supplier_id).exists())

        # Check that related objects are also deleted (CASCADE)
        self.assertFalse(Address.objects.filter(pk=address_id).exists())
        self.assertFalse(Contact.objects.filter(pk=contact_id).exists())

    def test_supplier_domain_object_protection(self):
        """Test that domain objects are protected from deletion when referenced."""
        Supplier.objects.create(
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
            classification=self.classification,
            category=self.category,
            risk_level=self.risk_level,
            type=self.supplier_type,
            situation=self.situation,
        )

        # Try to delete a domain object that's referenced by supplier
        # This should raise an error due to DO_NOTHING constraint
        classification_id = self.classification.pk
        with self.assertRaises(Exception):
            self.classification.delete()

        # Verify the classification still exists
        self.assertTrue(DomClassification.objects.filter(pk=classification_id).exists())
