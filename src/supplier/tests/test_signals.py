from django.test import TestCase
from model_bakery import baker

from src.supplier.enums import DomPendecyTypeEnum
from src.supplier.models.domain import DomPendecyType, DomSupplierSituation
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import Supplier


class TestSupplierSignals(TestCase):
    def setUp(self):
        # Cria todos os relacionamentos obrigatórios completos
        baker.make(
            DomPendecyType,
            name="PENDÊNCIA DE CADASTRO",
            id=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
        )
        baker.make(
            DomPendecyType,
            name="PENDÊNCIA MATRIZ DE RESPONSABILIDADE",
            id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
        )
        baker.make(
            DomPendecyType,
            name="PENDÊNCIA DE DOCUMENTAÇÃO",
            id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
        )

        baker.make(DomSupplierSituation, name="ATIVO")
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
        )
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

    def test_supplier_pendency_signal_sets_pendency_when_incomplete(self):
        # Deixa o supplier incompleto (ex: trade_name vazio)
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
        # Preenche todos os campos do supplier e relacionados com valores não-default
        self.supplier.trade_name = "Fornecedor Completo"
        self.supplier.state_business_registration = "123"
        self.supplier.municipal_business_registration = "456"
        # Address
        from datetime import date
        from decimal import Decimal

        # Address
        if self.supplier.address is None:
            address = baker.make("shared.Address")
            self.supplier.address = address
            self.supplier.save()
        address = self.supplier.address
        address.street = "Rua Teste"
        address.number = 100
        address.complement = "Apto 1"
        address.city = "Cidade"
        address.state = "ST"
        address.postal_code = "12345678"
        address.save()
        # Contact
        if self.supplier.contact is None:
            contact = baker.make("shared.Contact")
            self.supplier.contact = contact
            self.supplier.save()
        contact = self.supplier.contact
        contact.email = "contato@teste.com"
        contact.phone = "11999999999"
        contact.save()
        # PaymentDetails
        if self.supplier.payment_details is None:
            pd = baker.make("supplier.PaymentDetails")
            self.supplier.payment_details = pd
            self.supplier.save()
        pd = self.supplier.payment_details
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
        # OrganizationalDetails
        if self.supplier.organizational_details is None:
            org = baker.make("supplier.OrganizationalDetails")
            self.supplier.organizational_details = org
            self.supplier.save()
        org = self.supplier.organizational_details
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
        # FiscalDetails
        if self.supplier.fiscal_details is None:
            fiscal = baker.make("supplier.FiscalDetails")
            self.supplier.fiscal_details = fiscal
            self.supplier.save()
        fiscal = self.supplier.fiscal_details
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
        # CompanyInformation
        if self.supplier.company_information is None:
            ci = baker.make("supplier.CompanyInformation")
            self.supplier.company_information = ci
            self.supplier.save()
        ci = self.supplier.company_information
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
        # Contract
        if self.supplier.contract is None:
            contract = baker.make("supplier.Contract")
            self.supplier.contract = contract
            self.supplier.save()
        contract = self.supplier.contract
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
        # FKs
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
        # Não deve ser pendente de cadastro
        assert not (
            self.supplier.situation
            and self.supplier.situation.status.name == "PENDENTE"
            and self.supplier.situation.status.pendency_type is not None
            and self.supplier.situation.status.pendency_type.name
            == "PENDÊNCIA DE CADASTRO"
        )


class TestResponsibilityMatrixSignals(TestCase):
    def setUp(self):
        # Cria todos os relacionamentos obrigatórios completos
        baker.make(
            DomPendecyType,
            name="PENDÊNCIA DE CADASTRO",
            id=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
        )
        baker.make(
            DomPendecyType,
            name="PENDÊNCIA MATRIZ DE RESPONSABILIDADE",
            id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
        )
        baker.make(
            DomPendecyType,
            name="PENDÊNCIA DE DOCUMENTAÇÃO",
            id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
        )

        baker.make(DomSupplierSituation, name="ATIVO")
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
        )
        baker.make(
            DomSupplierSituation,
            name="PENDENTE",
            pendency_type_id=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
        )

        # Cria supplier completo para não ser pendente por outros motivos
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
        self.matrix = baker.make(ResponsibilityMatrix, supplier=self.supplier)

    def test_responsibility_matrix_pendency_signal_sets_pendency_when_incomplete(self):
        # Deixa todos os campos contract_execution_monitoring_* como '-'
        for field in self.matrix._meta.get_fields():
            if hasattr(field, "name") and field.name.startswith(
                "contract_execution_monitoring_"
            ):
                setattr(self.matrix, field.name, "-")
        self.matrix.save()
        self.supplier.refresh_from_db()
        assert not self.matrix.is_completed
        assert self.supplier.situation is not None
        assert self.supplier.situation.status.name == "PENDENTE"
        assert self.supplier.situation.status.pendency_type is not None
        assert (
            self.supplier.situation.status.pendency_type.name
            == "PENDÊNCIA MATRIZ DE RESPONSABILIDADE"
        )

    def test_responsibility_matrix_complete_property(self):
        # Preenche todos os campos contract_execution_monitoring_* com valores válidos
        for field in self.matrix._meta.get_fields():
            if hasattr(field, "name") and field.name.startswith(
                "contract_execution_monitoring_"
            ):
                setattr(self.matrix, field.name, "valor")
        assert self.matrix.is_completed
