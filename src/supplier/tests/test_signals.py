"""Tests for supplier signals."""

from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from model_bakery import baker

from src.supplier.enums import DomPendecyTypeEnum
from src.supplier.models.attachments import SupplierAttachment
from src.supplier.models.domain import DomAttachmentType, DomSupplierSituation
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import Supplier, SupplierSituation


class TestSupplierSignals(TestCase):
    def setUp(self):
        self.supplier = baker.make(
            Supplier,
            address=baker.make("shared.Address"),
            contact=baker.make("shared.Contact"),
            payment_details=baker.make("supplier.PaymentDetails"),
            organizational_details=baker.make("supplier.OrganizationalDetails"),
            fiscal_details=baker.make("supplier.FiscalDetails"),
            company_information=baker.make("supplier.CompanyInformation"),
            contract=baker.make("supplier.Contract"),
            classification=baker.make("supplier.DomClassification"),
            category=baker.make("supplier.DomCategory"),
            risk_level=baker.make("supplier.DomRiskLevel"),
            type=baker.make("supplier.DomTypeSupplier"),
        )

    def _setup_address(self, supplier):
        if supplier.address is None:
            supplier.address = baker.make("shared.Address")
            supplier.save()
        address = supplier.address
        address.street = "Rua Teste"
        address.number = 100
        address.complement = "Apto 1"
        address.city = "Cidade"
        address.state = "ST"
        address.postal_code = "12345678"
        address.save()

    def _setup_contact(self, supplier: Supplier):
        if supplier.contact is None:
            supplier.contact = baker.make("shared.Contact")
            supplier.save()
        contact = supplier.contact
        contact.name = "Contato Teste"
        contact.email = "contato@teste.com"
        contact.phone = "11999999999"
        contact.save()

    def _setup_payment_details(self, supplier: Supplier):
        if supplier.payment_details is None:
            supplier.payment_details = baker.make("supplier.PaymentDetails")
            supplier.save()
        pd = supplier.payment_details
        pd.payment_frequency = "Mensal"
        pd.payment_date = date(2025, 1, 1)
        pd.contract_total_value = Decimal("1000.00")
        pd.contract_monthly_value = Decimal("100.00")
        pd.checking_account = "12345"
        pd.bank = "Banco Teste"
        pd.agency = "0001"
        if pd.payment_method is None:
            pd.payment_method = baker.make("supplier.DomPaymentMethod")
        if pd.pix_key_type is None:
            pd.pix_key_type = baker.make("supplier.DomPixType")
        pd.pix_key = "chavepix"
        pd.save()

    def _setup_organizational_details(self, supplier: Supplier):
        if supplier.organizational_details is None:
            supplier.organizational_details = baker.make(
                "supplier.OrganizationalDetails"
            )
            supplier.save()
        org = supplier.organizational_details
        org.cost_center = "CC123"
        org.business_unit = "BU1"
        org.responsible_executive = "Executivo"
        if org.payer_type is None:
            org.payer_type = baker.make("supplier.DomPayerType")
        if org.business_sector is None:
            org.business_sector = baker.make("supplier.DomBusinessSector")
        if org.taxpayer_classification is None:
            org.taxpayer_classification = baker.make(
                "supplier.DomTaxpayerClassification"
            )
        if org.public_entity is None:
            org.public_entity = baker.make("supplier.DomPublicEntity")
        org.save()

    def _setup_fiscal_details(self, supplier: Supplier):
        if supplier.fiscal_details is None:
            supplier.fiscal_details = baker.make("supplier.FiscalDetails")
            supplier.save()
        fiscal = supplier.fiscal_details
        if fiscal.iss_withholding is None:
            fiscal.iss_withholding = baker.make("supplier.DomIssWithholding")
        if fiscal.iss_regime is None:
            fiscal.iss_regime = baker.make("supplier.DomIssRegime")
        fiscal.iss_taxpayer = True
        fiscal.simples_nacional_participant = True
        fiscal.cooperative_member = True
        if fiscal.withholding_tax_nature is None:
            fiscal.withholding_tax_nature = baker.make("supplier.DomWithholdingTax")
        fiscal.save()

    def _setup_company_information(self, supplier: Supplier):
        if supplier.company_information is None:
            supplier.company_information = baker.make("supplier.CompanyInformation")
            supplier.save()
        ci = supplier.company_information
        if ci.company_size is None:
            ci.company_size = baker.make("supplier.DomCompanySize")
        if ci.icms_taxpayer is None:
            ci.icms_taxpayer = baker.make("supplier.DomIcmsTaxpayer")
        if ci.taxation_regime is None:
            ci.taxation_regime = baker.make("supplier.DomTaxationRegime")
        if ci.income_type is None:
            ci.income_type = baker.make("supplier.DomIncomeType")
        if ci.taxation_method is None:
            ci.taxation_method = baker.make("supplier.DomTaxationMethod")
        if ci.customer_type is None:
            ci.customer_type = baker.make("supplier.DomCustomerType")
        ci.nit = "123456789"
        ci.save()

    def _setup_contract(self, supplier: Supplier):
        if supplier.contract is None:
            supplier.contract = baker.make("supplier.Contract")
            supplier.save()
        contract = supplier.contract
        contract.object_contract = "Objeto"
        contract.executed_activities = "Atividades"
        contract.contract_start_date = date(2025, 1, 1)
        contract.contract_end_date = date(2025, 12, 31)
        contract.contract_type = "Tipo"
        contract.contract_period = "12"
        contract.has_contract_renewal = True
        contract.warning_contract_renewal = True
        contract.warning_contract_period = "3"
        contract.warning_on_termination = True
        contract.warning_on_renewal = True
        contract.warning_on_period = True
        contract.save()

    def _setup_responsibility_matrix(self, supplier: Supplier):
        if not ResponsibilityMatrix.objects.filter(supplier=supplier).exists():
            matrix = ResponsibilityMatrix.objects.create(supplier=supplier)
            for field in matrix._meta.get_fields():
                if hasattr(field, "name") and field.name.startswith(
                    "contract_execution_monitoring_"
                ):
                    setattr(matrix, field.name, "R")
            matrix.save()

    def _setup_attachment(self, supplier: Supplier):
        if not SupplierAttachment.objects.filter(supplier=supplier).exists():
            attachment_type = DomAttachmentType.objects.create(name="Contrato Social")
            test_file = SimpleUploadedFile(
                "test_contract.pdf", b"file_content", content_type="application/pdf"
            )
            SupplierAttachment.objects.create(
                supplier=supplier,
                file=test_file,
                description="Documento",
                attachment_type=attachment_type,
            )

    def test_supplier_pendency_signal_sets_pendency_when_incomplete(self):
        self.supplier.trade_name = ""
        self.supplier.save()
        self.supplier.refresh_from_db()
        assert self.supplier.situation is not None
        assert self.supplier.situation.status.name == "PENDENTE"
        assert self.supplier.situation.status.pendency_type is not None
        assert (
            self.supplier.situation.status.pendency_type.name == "PENDÊNCIA DE CADASTRO"
        )

    def test_supplier_pendency_signal_does_not_set_pendency_when_complete(self):
        self.supplier.trade_name = "Fornecedor Completo"
        self.supplier.state_business_registration = "123"
        self.supplier.municipal_business_registration = "456"

        self._setup_address(self.supplier)
        self._setup_contact(self.supplier)
        self._setup_payment_details(self.supplier)
        self._setup_organizational_details(self.supplier)
        self._setup_fiscal_details(self.supplier)
        self._setup_company_information(self.supplier)
        self._setup_contract(self.supplier)
        self._setup_responsibility_matrix(self.supplier)
        self._setup_attachment(self.supplier)

        self.supplier.classification = self.supplier.classification or baker.make(
            "supplier.DomClassification"
        )
        self.supplier.category = self.supplier.category or baker.make(
            "supplier.DomCategory"
        )
        self.supplier.risk_level = self.supplier.risk_level or baker.make(
            "supplier.DomRiskLevel"
        )
        self.supplier.type = self.supplier.type or baker.make(
            "supplier.DomTypeSupplier"
        )
        self.supplier.save()
        self.supplier.refresh_from_db()
        self.assertIsNotNone(self.supplier.situation)
        self.assertIsNotNone(self.supplier.situation.status)
        self.assertEqual(self.supplier.situation.status.name, "ATIVO")
        self.assertIsNone(self.supplier.situation.status.pendency_type)

    def test_supplier_pendency_signal_sets_pendency_when_matrix_incomplete(self):
        SupplierSituation.objects.filter(supplier=self.supplier).delete()
        SupplierSituation.objects.create(
            supplier=self.supplier,
            status=DomSupplierSituation.objects.get(
                name="PENDENTE",
                pendency_type_id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
            ),
        )

        self.supplier.refresh_from_db()
        self.assertIsNotNone(self.supplier.situation)
        self.assertEqual(self.supplier.situation.status.name, "PENDENTE")
        self.assertIsNotNone(self.supplier.situation.status.pendency_type)
        self.assertEqual(
            self.supplier.situation.status.pendency_type.name,
            "PENDÊNCIA MATRIZ DE RESPONSABILIDADE",
        )

    def test_supplier_pendency_signal_sets_pendency_when_attachments_incomplete(self):
        SupplierSituation.objects.filter(supplier=self.supplier).delete()
        SupplierSituation.objects.create(
            supplier=self.supplier,
            status=DomSupplierSituation.objects.get(
                name="PENDENTE",
                pendency_type_id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
            ),
        )

        self.supplier.refresh_from_db()
        self.assertIsNotNone(self.supplier.situation)
        self.assertEqual(self.supplier.situation.status.name, "PENDENTE")
        self.assertIsNotNone(self.supplier.situation.status.pendency_type)
        self.assertEqual(
            self.supplier.situation.status.pendency_type.name,
            "PENDÊNCIA DE DOCUMENTAÇÃO",
        )
