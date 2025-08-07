"""
Supplier management models for procurement service.
This module contains models related to suppliers.
"""

from django.db import models

from src.shared.models import Address, Contact, TimestampedModel
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


class Contract(TimestampedModel):
    """
    Model representing a contract associated with suppliers.
    Contains contract details such as object, activities, start and end dates.
    """

    object_contract = models.CharField(max_length=255, help_text="Objeto do Contrato")
    executed_activities = models.TextField(help_text="Atividades Executadas")
    contract_start_date = models.DateField(help_text="Data de Início do Contrato")
    contract_end_date = models.DateField(help_text="Data Final do Contrato")

    def __str__(self):
        return f"Contrato: {self.object_contract} - {self.contract_start_date} a {self.contract_end_date}"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for Contract model.
        """

        db_table = "contract"
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        abstract = False


class PaymentDetails(TimestampedModel):
    """
    Model representing payment details for supplier contracts.
    Contains payment information including frequencies, dates, and values.
    """

    payment_frequency = models.CharField(
        max_length=50, help_text="Periodicidade do Pagamento"
    )
    payment_date = models.DateField(help_text="Data de Pagamento")
    contract_total_value = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Valor Total do Contrato"
    )
    contract_monthly_value = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Valor Mensal do Contrato"
    )
    checking_account = models.CharField(max_length=20, help_text="Conta Corrente")
    bank = models.CharField(max_length=50, help_text="Banco", blank=True, default="")
    agency = models.CharField(
        max_length=20, help_text="Agência", blank=True, default=""
    )
    payment_method = models.ForeignKey(
        DomPaymentMethod,
        on_delete=models.DO_NOTHING,
        related_name="payment_details",
        help_text="Forma de Pagamento",
    )
    pix_key_type = models.ForeignKey(
        DomPixType,
        on_delete=models.DO_NOTHING,
        related_name="payment_details",
        help_text="Tipo de Chave PIX",
    )
    pix_key = models.CharField(max_length=255, help_text="Chave PIX")

    def __str__(self):
        return f"Pagamento: {self.payment_frequency} - {self.payment_date}"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for PaymentDetails model.
        """

        db_table = "payment_details"
        verbose_name = "Detalhes de Pagamento"
        verbose_name_plural = "Detalhes de Pagamento"
        abstract = False


class OrganizationalDetails(TimestampedModel):
    """
    Model representing organizational details of suppliers.
    Contains cost center, business unit, and other organizational information.
    """

    cost_center = models.CharField(max_length=50, help_text="Centro de Custo")
    business_unit = models.CharField(
        max_length=100, help_text="BU (Unidade de Negócio)"
    )
    responsible_executive = models.CharField(
        max_length=255, help_text="Executivo Responsável"
    )

    payer_type = models.ForeignKey(
        DomPayerType,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Tipo de Tomador",
    )
    business_sector = models.ForeignKey(
        DomBusinessSector,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Ramo de Atividade",
    )
    taxpayer_classification = models.ForeignKey(
        DomTaxpayerClassification,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Classificação do Contribuinte",
    )
    public_entity = models.ForeignKey(
        DomPublicEntity,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Órgão Público",
    )

    def __str__(self):
        return f"Organizacional: {self.cost_center} - {self.business_unit}"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for OrganizationalDetails model.
        """

        db_table = "organizational_details"
        verbose_name = "Detalhes Organizacionais"
        verbose_name_plural = "Detalhes Organizacionais"
        abstract = False


class FiscalDetails(TimestampedModel):
    """
    Model representing fiscal details for suppliers.
    Contains tax-related information including ISS, withholding tax, and cooperative details.
    """

    # Campos Fiscais - ISS
    iss_withholding = models.ForeignKey(
        DomIssWithholding,
        on_delete=models.DO_NOTHING,
        related_name="fiscal_details",
        help_text="Retenção de ISS",
    )
    iss_regime = models.ForeignKey(
        DomIssRegime,
        on_delete=models.DO_NOTHING,
        related_name="fiscal_details",
        help_text="Regime ISS",
    )
    iss_taxpayer = models.BooleanField(default=False, help_text="Contribuinte ISS")

    # Campos Fiscais - Gerais
    simples_nacional_participant = models.BooleanField(
        default=False, help_text="Optante pelo Simples Nacional"
    )
    cooperative_member = models.BooleanField(default=False, help_text="Sócio Cooperado")
    withholding_tax_nature = models.ForeignKey(
        DomWithholdingTax,
        on_delete=models.DO_NOTHING,
        related_name="fiscal_details",
        help_text="Natureza da Retenção na Fonte",
    )

    def __str__(self):
        return f"Fiscal: ISS {self.iss_withholding} - Simples Nacional {self.simples_nacional_participant}"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for FiscalDetails model.
        """

        db_table = "fiscal_details"
        verbose_name = "Detalhes Fiscais"
        verbose_name_plural = "Detalhes Fiscais"
        abstract = False


class CompanyInformation(TimestampedModel):
    """
    Model representing company information for suppliers.
    Contains company size, tax details, and classification information.
    """

    company_size = models.ForeignKey(
        DomCompanySize,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Porte da Empresa",
    )
    icms_taxpayer = models.ForeignKey(
        DomIcmsTaxpayer,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Contribuinte ICMS",
    )
    taxation_regime = models.ForeignKey(
        DomTaxationRegime,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Regime de Tributação",
    )
    income_type = models.ForeignKey(
        DomIncomeType,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Tipo de Rendimento",
    )
    taxation_method = models.ForeignKey(
        DomTaxationMethod,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Forma de Tributação",
    )
    customer_type = models.ForeignKey(
        DomCustomerType,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Tipo de Cliente",
    )
    nit = models.CharField(
        max_length=20,
        blank=True,
        help_text="NIT (Número de Identificação do Trabalhador)",
    )

    def __str__(self):
        return f"Empresa: {self.company_size} - ICMS {self.icms_taxpayer}"

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for CompanyInformation model.
        """

        db_table = "company_information"
        verbose_name = "Informações da Empresa"
        verbose_name_plural = "Informações da Empresa"
        abstract = False


class Supplier(TimestampedModel):
    """
    Model representing a supplier in the procurement system.
    Contains basic supplier information and relationships to detailed information.
    """

    trade_name = models.CharField(max_length=255, help_text="Nome fantasia")
    legal_name = models.CharField(max_length=255, unique=True, help_text="Razão Social")
    tax_id = models.CharField(max_length=16, unique=True, help_text="CPF/CNPJ")
    state_business_registration = models.CharField(
        max_length=20, help_text="Inscrição Estadual"
    )
    municipal_business_registration = models.CharField(
        max_length=20, help_text="Inscrição Municipal"
    )
    # One-to-one relationships
    address = models.OneToOneField(
        Address, on_delete=models.CASCADE, related_name="supplier"
    )
    contact = models.OneToOneField(
        Contact, on_delete=models.CASCADE, related_name="supplier"
    )
    payment_details = models.OneToOneField(
        PaymentDetails, on_delete=models.CASCADE, related_name="supplier"
    )
    organizational_details = models.OneToOneField(
        OrganizationalDetails,
        on_delete=models.CASCADE,
        related_name="supplier",
    )
    fiscal_details = models.OneToOneField(
        FiscalDetails, on_delete=models.CASCADE, related_name="supplier"
    )
    company_information = models.OneToOneField(
        CompanyInformation,
        on_delete=models.CASCADE,
        related_name="supplier",
    )
    contract = models.OneToOneField(
        Contract, on_delete=models.CASCADE, related_name="supplier"
    )
    # Foreign key relationships
    classification = models.ForeignKey(
        DomClassification, on_delete=models.DO_NOTHING, related_name="suppliers"
    )
    category = models.ForeignKey(
        DomCategory, on_delete=models.DO_NOTHING, related_name="suppliers"
    )
    risk_level = models.ForeignKey(
        DomRiskLevel, on_delete=models.DO_NOTHING, related_name="suppliers"
    )
    type = models.ForeignKey(
        DomTypeSupplier, on_delete=models.DO_NOTHING, related_name="suppliers"
    )
    situation = models.ForeignKey(
        DomSupplierSituation, on_delete=models.DO_NOTHING, related_name="suppliers"
    )

    def __str__(self):
        return self.trade_name

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for Supplier model.
        """

        db_table = "supplier"
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        abstract = False
