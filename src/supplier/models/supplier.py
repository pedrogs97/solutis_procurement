"""
Supplier management models for procurement service.
This module contains models related to suppliers.
"""

from decimal import Decimal
from typing import Optional

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
from src.supplier.models.validators import validate_object_complete


class Contract(TimestampedModel):
    """
    Model representing a contract associated with suppliers.
    Contains contract details such as object, activities, start and end dates.
    """

    object_contract = models.CharField(
        max_length=255, help_text="Objeto do Contrato", blank=True, default=""
    )
    executed_activities = models.TextField(
        help_text="Atividades Executadas", blank=True, default=""
    )
    contract_start_date = models.DateField(
        help_text="Data de Início do Contrato", null=True, blank=True
    )
    contract_end_date = models.DateField(
        help_text="Data Final do Contrato", null=True, blank=True
    )
    contract_type = models.CharField(
        max_length=50, help_text="Tipo de Contrato", blank=True, default=""
    )
    contract_period = models.CharField(
        max_length=3, help_text="Período do Contrato", blank=True, default=""
    )
    has_contract_renewal = models.BooleanField(
        help_text="Renovação de Contrato", default=False
    )
    warning_contract_renewal = models.BooleanField(
        help_text="Aviso de Renovação de Contrato", default=False
    )
    warning_contract_period = models.CharField(
        max_length=3, help_text="Aviso Prévio de Contrato", blank=True, default=""
    )
    warning_on_termination = models.BooleanField(
        help_text="Tem Aviso de Término de Contrato", default=False
    )
    warning_on_renewal = models.BooleanField(
        help_text="Tem Aviso de Renovação de Contrato", default=False
    )
    warning_on_period = models.BooleanField(
        help_text="Tem Aviso Prévio de Contrato", default=False
    )

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
        max_length=50, help_text="Periodicidade do Pagamento", blank=True, default=""
    )
    payment_date = models.CharField(
        max_length=100, help_text="Data de Pagamento", blank=True, default=""
    )
    contract_total_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valor Total do Contrato",
        default=Decimal(0),
    )
    contract_monthly_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valor Mensal do Contrato",
        default=Decimal(0),
    )
    checking_account = models.CharField(
        max_length=20, help_text="Conta Corrente", blank=True, default=""
    )
    bank = models.CharField(max_length=50, help_text="Banco", blank=True, default="")
    bank_code = models.CharField(
        max_length=50, help_text="Código do Banco", blank=True, default=""
    )
    agency = models.CharField(
        max_length=20, help_text="Agência", blank=True, default=""
    )
    payment_method = models.ForeignKey(
        DomPaymentMethod,
        on_delete=models.DO_NOTHING,
        related_name="payment_details",
        help_text="Forma de Pagamento",
        null=True,
        blank=True,
    )
    pix_key_type = models.ForeignKey(
        DomPixType,
        on_delete=models.DO_NOTHING,
        related_name="payment_details",
        help_text="Tipo de Chave PIX",
        null=True,
        blank=True,
    )
    pix_key = models.CharField(
        max_length=255, help_text="Chave PIX", blank=True, default=""
    )

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

    cost_center = models.CharField(
        max_length=50, help_text="Centro de Custo", blank=True, default=""
    )
    business_unit = models.CharField(
        max_length=100, help_text="BU (Unidade de Negócio)", blank=True, default=""
    )
    responsible_executive = models.CharField(
        max_length=255, help_text="Executivo Responsável", blank=True, default=""
    )

    payer_type = models.ForeignKey(
        DomPayerType,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Tipo de Tomador",
        null=True,
        blank=True,
    )
    business_sector = models.ForeignKey(
        DomBusinessSector,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Ramo de Atividade",
        null=True,
        blank=True,
    )
    taxpayer_classification = models.ForeignKey(
        DomTaxpayerClassification,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Classificação do Contribuinte",
        null=True,
        blank=True,
    )
    public_entity = models.ForeignKey(
        DomPublicEntity,
        on_delete=models.DO_NOTHING,
        related_name="organizational_details",
        help_text="Órgão Público",
        null=True,
        blank=True,
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
        null=True,
        blank=True,
    )
    iss_regime = models.ForeignKey(
        DomIssRegime,
        on_delete=models.DO_NOTHING,
        related_name="fiscal_details",
        help_text="Regime ISS",
        null=True,
        blank=True,
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
        null=True,
        blank=True,
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
        null=True,
        blank=True,
    )
    icms_taxpayer = models.ForeignKey(
        DomIcmsTaxpayer,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Contribuinte ICMS",
        null=True,
        blank=True,
    )
    taxation_regime = models.ForeignKey(
        DomTaxationRegime,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Regime de Tributação",
        null=True,
        blank=True,
    )
    income_type = models.ForeignKey(
        DomIncomeType,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Tipo de Rendimento",
        null=True,
        blank=True,
    )
    taxation_method = models.ForeignKey(
        DomTaxationMethod,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Forma de Tributação",
        null=True,
        blank=True,
    )
    customer_type = models.ForeignKey(
        DomCustomerType,
        on_delete=models.DO_NOTHING,
        related_name="company_information",
        help_text="Tipo de Cliente",
        null=True,
        blank=True,
    )
    nit = models.CharField(
        max_length=20,
        blank=True,
        default="",
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

    trade_name = models.CharField(
        max_length=255, help_text="Nome fantasia", blank=True, default=""
    )
    legal_name = models.CharField(max_length=255, unique=True, help_text="Razão Social")
    tax_id = models.CharField(max_length=18, unique=True, help_text="CPF/CNPJ")
    state_business_registration = models.CharField(
        max_length=20, help_text="Inscrição Estadual", blank=True, default=""
    )
    municipal_business_registration = models.CharField(
        max_length=20, help_text="Inscrição Municipal", blank=True, default=""
    )
    # One-to-one relationships
    address = models.OneToOneField(
        Address,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )
    contact = models.OneToOneField(
        Contact,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )
    payment_details = models.OneToOneField(
        PaymentDetails,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )
    organizational_details = models.OneToOneField(
        OrganizationalDetails,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )
    fiscal_details = models.OneToOneField(
        FiscalDetails,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )
    company_information = models.OneToOneField(
        CompanyInformation,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name="supplier",
        null=True,
        blank=True,
    )
    # Foreign key relationships
    classification = models.ForeignKey(
        DomClassification,
        on_delete=models.DO_NOTHING,
        related_name="suppliers",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        DomCategory,
        on_delete=models.DO_NOTHING,
        related_name="suppliers",
        null=True,
        blank=True,
    )
    risk_level = models.ForeignKey(
        DomRiskLevel,
        on_delete=models.DO_NOTHING,
        related_name="suppliers",
        null=True,
        blank=True,
    )
    type = models.ForeignKey(
        DomTypeSupplier,
        on_delete=models.DO_NOTHING,
        related_name="suppliers",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.trade_name

    @property
    def is_completed_registration(self) -> bool:
        """
        Check if the supplier registration is complete.
        """
        is_obj_complete = validate_object_complete(self)
        first_attach = self.attachments.first()
        is_files_complete = first_attach and first_attach.is_completed_files
        is_responsibility_complete = (
            hasattr(self, "responsibility_matrix")
            and self.responsibility_matrix.is_completed
        )
        return is_obj_complete and is_files_complete and is_responsibility_complete

    @property
    def situation(self) -> Optional["SupplierSituation"]:
        """
        Get the current situation of the supplier.
        """
        return self.situations.order_by("-created_at").first()

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for Supplier model.
        """

        db_table = "supplier"
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        abstract = False


class SupplierSituation(TimestampedModel):
    """
    Model representing the situation of a supplier.
    """

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="situations"
    )
    status = models.ForeignKey(
        DomSupplierSituation, on_delete=models.CASCADE, related_name="situations"
    )

    class Meta(TimestampedModel.Meta):
        """
        Meta configuration for SupplierSituation model.
        """

        db_table = "supplier_situation"
        verbose_name = "Situação do Fornecedor"
        verbose_name_plural = "Situações do Fornecedor"
        abstract = False
        unique_together = (("supplier", "status"),)
